#!/usr/bin/env python3
"""LAN screen discovery and DLNA control using Python's standard library.

Examples (run from the skill root):
    python3 scripts/remote_display.py discover --json
    python3 scripts/remote_display.py play "$SCREEN_IP" ./movie.mp4 --duration 600
    python3 scripts/remote_display.py status "$SCREEN_IP"
    python3 scripts/remote_display.py wake "$SCREEN_IP"
    python3 scripts/remote_display.py monitor "$SCREEN_IP" --output HEADLESS-2 --create-headless
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import math
import mimetypes
import os
import re
import shutil
import select
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape

RENDERER = "urn:schemas-upnp-org:device:MediaRenderer:1"
MDNS_TYPES = ("_airplay._tcp.local", "_raop._tcp.local",
              "_googlecast._tcp.local", "_display._tcp.local",
              "_samsungmsf._tcp.local", "_services._dns-sd._udp.local")
HTTP = urllib.request.build_opener(urllib.request.ProxyHandler({}))
# stdlib build_opener also installs File/FTP handlers; drop them so a hostile
# device description can never make the tool read local files or hit FTP targets.
HTTP.handlers = [handler for handler in HTTP.handlers
                 if not isinstance(handler, (urllib.request.FileHandler,
                                             urllib.request.FTPHandler))]
MAX_BODY = 2 * 1024 * 1024


class NotFound(Exception):
    """Device, service, or response not found within the requested wait."""


def parse_ssdp_response(packet: bytes | str) -> dict[str, str]:
    """Return case-normalized headers from a successful SSDP reply."""
    text = packet.decode("utf-8", "replace") if isinstance(packet, bytes) else packet
    lines = text.replace("\r\n", "\n").splitlines()
    if not lines or not re.match(r"HTTP/1\.[01]\s+200(?:\s|$)", lines[0]):
        return {}
    return {k.strip().upper(): v.strip() for line in lines[1:] if ":" in line
            for k, v in [line.split(":", 1)]}


def parse_dns_name(packet: bytes, offset: int) -> tuple[str, int]:
    """Decode a DNS name, returning its value and next wire offset."""
    labels: list[str] = []
    seen: set[int] = set()
    end = None
    size = 0
    while True:
        if offset in seen or offset >= len(packet) or offset < 0:
            raise ValueError("Invalid DNS name or compression loop")
        seen.add(offset)
        length = packet[offset]
        if length & 0xC0 == 0xC0:
            if offset + 1 >= len(packet):
                raise ValueError("Truncated DNS pointer")
            if end is None:
                end = offset + 2
            offset = ((length & 0x3F) << 8) | packet[offset + 1]
            continue
        if length & 0xC0:
            raise ValueError("Unsupported DNS label")
        offset += 1
        if length == 0:
            return ".".join(labels), end if end is not None else offset
        if offset + length > len(packet):
            raise ValueError("Truncated DNS label")
        size += length + 1
        if size > 254:
            raise ValueError("DNS name too long")
        labels.append(packet[offset:offset + length].decode("utf-8", "replace"))
        offset += length


def local_tag(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def reject_xml_entities(data: bytes | str) -> None:
    """Refuse DOCTYPE/ENTITY declarations (removes any XXE / entity-expansion surface)."""
    probe = data if isinstance(data, bytes) else data.encode("utf-8", "replace")
    head = probe[:4096].upper()
    if b"<!DOCTYPE" in head or b"<!ENTITY" in head:
        raise ValueError("XML DOCTYPE/ENTITY declarations are not accepted")


def xml_values(data: bytes | str) -> dict[str, str]:
    reject_xml_entities(data)
    root = ET.fromstring(data)
    values = {local_tag(e.tag): e.text or "" for e in root.iter() if not len(e)}
    if any(local_tag(e.tag) == "Fault" for e in root.iter()):
        raise RuntimeError("SOAP fault: " + values.get("errorDescription",
                           values.get("faultstring", "Unknown device error")))
    return values


def parse_description(data: bytes | str, location: str) -> dict[str, Any]:
    """Extract renderer metadata and resolve relative service URLs."""
    reject_xml_entities(data)
    root = ET.fromstring(data)
    base = next((e.text for e in root.iter() if local_tag(e.tag) == "URLBase"
                 and e.text), location)
    if urllib.parse.urlsplit(base).scheme not in ("http", "https"):
        raise ValueError("Device URLBase must use HTTP or HTTPS")
    devices = [e for e in root.iter() if local_tag(e.tag) == "device"]
    device = next((e for e in devices if any(local_tag(c.tag) == "deviceType"
                   and "MediaRenderer:" in (c.text or "") for c in e)),
                  devices[0] if devices else root)
    fields = {local_tag(e.tag): e.text or "" for e in device if not len(e)}
    services = []
    for e in device.iter():
        if local_tag(e.tag) != "service":
            continue
        service = {local_tag(c.tag): c.text or "" for c in e}
        for key in ("controlURL", "eventSubURL", "SCPDURL"):
            if service.get(key):
                resolved = urllib.parse.urljoin(base, service[key])
                if urllib.parse.urlsplit(resolved).scheme not in ("http", "https"):
                    raise ValueError("Device service URLs must use HTTP or HTTPS")
                service[key] = resolved
        services.append(service)
    return {"name": fields.get("friendlyName", "Unknown screen"),
            "manufacturer": fields.get("manufacturer", ""),
            "model": fields.get("modelName", ""),
            "ip": urllib.parse.urlsplit(location).hostname,
            "location": location, "services": services,
            "AVTransport": any(":AVTransport:" in s.get("serviceType", "") for s in services),
            "RenderingControl": any(":RenderingControl:" in s.get("serviceType", "") for s in services)}


def read_http(url: str, timeout: float, data: bytes | None = None,
              headers: dict[str, str] | None = None) -> bytes:
    if urllib.parse.urlsplit(url).scheme not in ("http", "https"):
        raise ValueError("Only HTTP(S) URLs are allowed")
    request = urllib.request.Request(url, data=data, headers=headers or {})
    with HTTP.open(request, timeout=timeout) as response:
        body = response.read(MAX_BODY + 1)
    if len(body) > MAX_BODY:
        raise ValueError("Device response exceeds 2 MiB")
    return body


def fetch_description(location: str, timeout: float = 2) -> dict[str, Any]:
    if urllib.parse.urlsplit(location).scheme not in ("http", "https"):
        raise ValueError("Description LOCATION must use HTTP or HTTPS")
    return parse_description(read_http(location, min(timeout, 2)), location)


def find_service(device: dict[str, Any], name: str) -> dict[str, str]:
    for service in device.get("services", []):
        if f":{name}:" in service.get("serviceType", "") and service.get("controlURL"):
            return service
    raise NotFound(f"Screen has no {name} control service")


def build_soap_envelope(service_type: str, action: str,
                        arguments: dict[str, Any]) -> bytes:
    envelope = ET.Element("{http://schemas.xmlsoap.org/soap/envelope/}Envelope",
                          {"{http://schemas.xmlsoap.org/soap/envelope/}encodingStyle":
                           "http://schemas.xmlsoap.org/soap/encoding/"})
    body = ET.SubElement(envelope, "{http://schemas.xmlsoap.org/soap/envelope/}Body")
    call = ET.SubElement(body, f"{{{service_type}}}{action}")
    for key, value in arguments.items():
        ET.SubElement(call, key).text = str(value)
    return ET.tostring(envelope, encoding="utf-8", xml_declaration=True)


def soap_call(service: dict[str, str], action: str, arguments: dict[str, Any],
              timeout: float = 3) -> dict[str, str]:
    service_type = service["serviceType"]
    headers = {"Content-Type": 'text/xml; charset="utf-8"',
               "SOAPACTION": f'"{service_type}#{action}"'}
    try:
        data = read_http(service["controlURL"], timeout,
                         build_soap_envelope(service_type, action, arguments), headers)
    except urllib.error.HTTPError as exc:
        # UPnP faults commonly arrive with HTTP 500; retain the useful fault text.
        try:
            fault = exc.read(MAX_BODY)
        finally:
            exc.close()
        try:
            xml_values(fault)  # raises RuntimeError carrying the fault text
        except (ET.ParseError, ValueError) as parse_exc:
            raise RuntimeError(f"SOAP {action}: HTTP {exc.code}") from parse_exc
        raise RuntimeError(f"SOAP {action}: HTTP {exc.code}")
    return xml_values(data)


def content_type_for(path: str | Path) -> str:
    overrides = {".mp4": "video/mp4", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                 ".mp3": "audio/mpeg"}
    return overrides.get(Path(path).suffix.lower()) or mimetypes.guess_type(str(path))[0] or "application/octet-stream"


def parse_range_header(header: str | None, size: int) -> tuple[int, int] | None:
    """Inclusive byte bounds; reject malformed, multiple, or unsatisfiable ranges."""
    if header is None:
        return None
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", header.strip())
    if not match or size <= 0 or not any(match.groups()):
        raise ValueError("Invalid or unsatisfiable byte range")
    first, last = match.groups()
    if not first:
        length = int(last)
        if length <= 0:
            raise ValueError("Invalid suffix range")
        return max(0, size - length), size - 1
    start = int(first)
    end = min(int(last), size - 1) if last else size - 1
    if start >= size or end < start:
        raise ValueError("Unsatisfiable byte range")
    return start, end


def parse_mdns_packet(packet: bytes) -> list[dict[str, Any]]:
    if len(packet) < 12:
        raise ValueError("Truncated DNS header")
    _, flags, qd, an, ns, ar = struct.unpack_from("!6H", packet)
    if not flags & 0x8000:
        return []
    offset = 12
    for _ in range(qd):
        _, offset = parse_dns_name(packet, offset)
        offset += 4
        if offset > len(packet):
            raise ValueError("Truncated DNS question")
    records = []
    for _ in range(an + ns + ar):
        name, offset = parse_dns_name(packet, offset)
        if offset + 10 > len(packet):
            raise ValueError("Truncated DNS record")
        kind, cls, ttl, length = struct.unpack_from("!HHIH", packet, offset)
        offset += 10
        end = offset + length
        if end > len(packet):
            raise ValueError("Truncated DNS data")
        record: dict[str, Any] = {"name": name, "kind": kind, "ttl": ttl}
        if cls & 0x7FFF != 1:
            offset = end
            continue
        if kind == 12:
            record["value"], next_offset = parse_dns_name(packet, offset)
            if next_offset > end:
                raise ValueError("PTR exceeds record")
        elif kind == 33:
            if length < 7:
                raise ValueError("Truncated SRV record")
            record["port"] = struct.unpack_from("!H", packet, offset + 4)[0]
            record["target"], next_offset = parse_dns_name(packet, offset + 6)
            if next_offset > end:
                raise ValueError("SRV exceeds record")
        elif kind == 1 and length == 4:
            record["value"] = socket.inet_ntoa(packet[offset:end])
        elif kind == 16:
            items = []
            cursor = offset
            while cursor < end:
                length = packet[cursor]
                cursor += 1
                if cursor + length > end:
                    raise ValueError("Truncated TXT item")
                items.append(packet[cursor:cursor + length].decode("utf-8", "replace"))
                cursor += length
            record["txt"] = items
        else:
            offset = end
            continue
        records.append(record)
        offset = end
    return records


def mdns_services(records: list[dict[str, Any]], types: tuple[str, ...]) -> list[dict[str, Any]]:
    """Join PTR/SRV/TXT/A records across all received packets."""
    srvs = {r["name"].lower(): r for r in records if r["kind"] == 33}
    addresses = {r["name"].lower(): r["value"] for r in records if r["kind"] == 1}
    txts = {r["name"].lower(): r["txt"] for r in records if r["kind"] == 16}
    found = {}
    for record in records:
        if record["kind"] != 12 or record["name"].lower() not in types:
            continue
        instance = record["value"]
        srv = srvs.get(instance.lower(), {})
        target = srv.get("target", "")
        found[(record["name"].lower(), instance.lower())] = {
            "type": record["name"], "name": instance, "target": target,
            "port": srv.get("port"), "ip": addresses.get(target.lower()),
            "txt": txts.get(instance.lower(), [])}
    return list(found.values())


def dns_query(types: tuple[str, ...]) -> bytes:
    questions = b""
    for name in types:
        questions += b"".join(bytes([len(p)]) + p.encode("ascii") for p in name.split("."))
        questions += b"\0" + struct.pack("!HH", 12, 1)
    return struct.pack("!6H", 0, 0, len(types), 0, 0, 0) + questions


def mdns_scan(timeout: float, types: tuple[str, ...] = MDNS_TYPES) -> list[dict[str, Any]]:
    records = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", 5353))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                        socket.inet_aton("224.0.0.251") + socket.inet_aton("0.0.0.0"))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
        sock.sendto(dns_query(types), ("224.0.0.251", 5353))
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            sock.settimeout(max(0.001, deadline - time.monotonic()))
            try:
                packet, _ = sock.recvfrom(65535)
            except socket.timeout:
                break
            try:
                records.extend(parse_mdns_packet(packet))
            except (ValueError, struct.error, UnicodeError):
                continue
    return mdns_services(records, types)


def ssdp_search(timeout: float, ip: str | None = None) -> list[str]:
    locations: set[str] = set()
    message = ("M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\n"
               'MAN: "ssdp:discover"\r\nMX: 1\r\nST: ' + RENDERER + "\r\n\r\n").encode()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(message, ("239.255.255.250", 1900))
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            sock.settimeout(max(0.001, deadline - time.monotonic()))
            try:
                packet, sender = sock.recvfrom(65535)
            except socket.timeout:
                break
            if ip and sender[0] != ip:
                continue
            headers = parse_ssdp_response(packet)
            location = headers.get("LOCATION")
            if not location:
                continue
            try:
                parsed = urllib.parse.urlsplit(location)
                if parsed.scheme in ("http", "https") and parsed.hostname and (not ip or parsed.hostname == ip):
                    locations.add(location)
            except ValueError:
                continue
    return sorted(locations)


def resolve_device(ip: str, timeout: float) -> dict[str, Any]:
    failures = []
    try:
        locations = ssdp_search(timeout, ip)
    except OSError as exc:
        locations = []
        failures.append(str(exc))
    for location in locations + [f"http://{ip}:9197/dmr"]:
        try:
            return fetch_description(location, timeout)
        except (OSError, ValueError, ET.ParseError) as exc:
            failures.append(str(exc))
    try:
        data = json.loads(read_http(f"http://{ip}:8001/api/v2/", timeout))
        if not isinstance(data, dict):
            raise ValueError("Tizen response is not an object")
        details = data.get("device", {})
        if not isinstance(details, dict):
            details = {}
        return {"ip": ip, "name": details.get("name", "Tizen screen"),
                "model": details.get("modelName", ""), "manufacturer": "Samsung",
                "services": [], "tizen_keys": sorted(data), "tizen_device_keys": sorted(details)}
    except (OSError, ValueError) as exc:
        failures.append(str(exc))
    raise NotFound(f"No screen description found for {ip}: " + "; ".join(failures))


def discover(timeout: float) -> list[dict[str, Any]]:
    devices: dict[str, dict[str, Any]] = {}
    failures = []
    try:
        locations = ssdp_search(timeout)
    except OSError as exc:
        locations = []
        failures.append(f"SSDP: {exc}")
    if len(locations) > 16:
        print(f"Discovery: capping description fetches at 16 of {len(locations)} locations.",
              file=sys.stderr)
    for location in locations[:16]:
        try:
            device = fetch_description(location, timeout)
            devices.setdefault(device["ip"], device)
        except (OSError, ValueError, ET.ParseError) as exc:
            print(f"Skipping description {location}: {exc}", file=sys.stderr)
    try:
        services = mdns_scan(timeout)
    except OSError as exc:
        services = []
        failures.append(f"mDNS: {exc}")
    for service in services:
        # Keep unresolved advertisements identifiable; never collapse all missing IPs.
        key = service["ip"] or service["target"] or service["name"]
        device = devices.setdefault(key, {"ip": service["ip"], "name": service["name"],
                                         "model": "", "services": []})
        if service not in device.setdefault("mdns", []):
            device["mdns"].append(service)
    for failure in failures:
        print(f"Discovery warning: {failure}", file=sys.stderr)
    if not devices and len(failures) == 2:
        raise RuntimeError("Both discovery transports failed")
    return list(devices.values())


def get_status(device: dict[str, Any], timeout: float) -> dict[str, str]:
    service = find_service(device, "AVTransport")
    transport = soap_call(service, "GetTransportInfo", {"InstanceID": 0}, timeout)
    position = soap_call(service, "GetPositionInfo", {"InstanceID": 0}, timeout)
    return {"TransportState": transport.get("CurrentTransportState", transport.get("TransportState", "")),
            "CurrentURI": position.get("TrackURI", ""),
            "position": position.get("RelTime", ""), "duration": position.get("TrackDuration", "")}


def make_media_handler(path: Path, allowed_client: str | None = None) -> type[BaseHTTPRequestHandler]:
    resource = "/" + urllib.parse.quote(path.name, safe="")

    class MediaHandler(BaseHTTPRequestHandler):
        timeout = 10

        def do_HEAD(self) -> None:
            self.serve(False)

        def do_GET(self) -> None:
            self.serve(True)

        def log_message(self, format: str, *args: Any) -> None:
            pass

        def serve(self, send_body: bool) -> None:
            if allowed_client and self.client_address[0] != allowed_client:
                self.send_error(403, "Only the target screen may fetch this file")
                return
            if urllib.parse.urlsplit(self.path).path != resource:
                self.send_error(404, "Only the selected media file is served")
                return
            try:
                media = path.open("rb")
            except OSError:
                self.send_error(404, "Media file unavailable")
                return
            with media:
                size = os.fstat(media.fileno()).st_size
                try:
                    bounds = parse_range_header(self.headers.get("Range"), size)
                except ValueError:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                start, end = bounds if bounds else (0, size - 1)
                self.send_response(206 if bounds else 200)
                self.send_header("Content-Type", content_type_for(path))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Length", str(max(0, end - start + 1)))
                if bounds:
                    self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.end_headers()
                if not send_body:
                    return
                media.seek(start)
                remaining = end - start + 1
                try:
                    while remaining > 0:
                        chunk = media.read(min(65536, remaining))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        remaining -= len(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    pass
    return MediaHandler


def lan_ip(screen_ip: str) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect((screen_ip, 9))
        return sock.getsockname()[0]


MAC_PATTERN = re.compile(r"^(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")


def mac_from_arp(ip: str) -> str | None:
    """Return the MAC address for ip from the kernel ARP table, when known."""
    try:
        with open("/proc/net/arp", "r", encoding="ascii", errors="replace") as table:
            next(table, None)  # header row
            for row in table:
                fields = row.split()
                if len(fields) >= 4 and fields[0] == ip and fields[3] != "00:00:00:00:00:00":
                    return fields[3]
    except OSError:
        return None
    return None


def wake(args: argparse.Namespace) -> None:
    target = args.target.strip()
    ip = None
    if MAC_PATTERN.match(target):
        mac = target.replace("-", ":").lower()
    else:
        try:
            ip = str(ipaddress.IPv4Address(target))
        except ipaddress.AddressValueError as exc:
            raise ValueError("target must be a MAC address or an IPv4 address") from exc
        mac = mac_from_arp(ip)
        if mac is None or not MAC_PATTERN.match(mac):
            raise NotFound(f"no usable ARP entry for {ip}; reach it once or pass its MAC address")
    packet = b"\xff" * 6 + bytes.fromhex(mac.replace(":", "")) * 16
    destinations = [args.broadcast] + ([ip] if ip else [])
    sent: list[str] = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        for destination in destinations:
            try:
                sock.sendto(packet, (destination, args.port))
                sent.append(destination)
            except OSError:
                continue
    if not sent:
        raise OSError("could not send the magic packet")
    print(f"Wake-on-LAN magic packet sent to {mac} via {', '.join(sent)}")


def seek(args: argparse.Namespace, device: dict[str, Any]) -> None:
    soap_call(find_service(device, "AVTransport"), "Seek",
              {"InstanceID": 0, "Unit": "REL_TIME", "Target": args.position}, args.timeout)
    output(get_status(device, args.timeout), False)


def display_env() -> dict[str, str]:
    """Environment able to reach the user session (Wayland/Hyprland) for capture tools."""
    env = dict(os.environ)
    runtime = Path(env.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}")
    env["XDG_RUNTIME_DIR"] = str(runtime)
    if not env.get("WAYLAND_DISPLAY") and runtime.is_dir():
        sockets = sorted(p.name for p in runtime.glob("wayland-?") if not p.name.endswith(".lock"))
        if sockets:
            env["WAYLAND_DISPLAY"] = sockets[0]
    if not env.get("HYPRLAND_INSTANCE_SIGNATURE"):
        hypr_dir = runtime / "hypr"
        if hypr_dir.is_dir():
            instances = sorted(hypr_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
            if instances:
                env["HYPRLAND_INSTANCE_SIGNATURE"] = instances[0].name
    return env


def hyprctl(env: dict[str, str], *argv: str) -> str:
    result = subprocess.run(["hyprctl", *argv], env=env, capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        raise RuntimeError(f"hyprctl {' '.join(argv)} failed: "
                           f"{result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def output_present(env: dict[str, str], name: str) -> bool:
    try:
        monitors = json.loads(hyprctl(env, "monitors", "-j"))
    except (RuntimeError, ValueError):
        return False
    return any(monitor.get("name") == name for monitor in monitors)


def ensure_output(env: dict[str, str], name: str, create: bool) -> bool:
    """Ensure the output exists; returns True when this call created it."""
    if output_present(env, name):
        return False
    if not create:
        raise NotFound(f"no output named '{name}' exists; create it first or pass --create-headless")
    hyprctl(env, "output", "create", "headless", name)
    deadline = time.time() + 10
    while time.time() < deadline:
        if output_present(env, name):
            return True
        time.sleep(0.5)
    raise RuntimeError(f"headless output '{name}' did not appear")


def build_didl(url: str, title: str = "Remote media", mime: str | None = None) -> str:
    """DIDL-Lite metadata so strict renderers (notably Samsung) accept stream URLs."""
    mime = mime or ("application/x-mpegurl" if urllib.parse.urlsplit(url).path.lower().endswith(".m3u8")
            else "video/mpeg" if urllib.parse.urlsplit(url).path.endswith(".ts") else "video/mp4")
    features = DLNA_TS if urllib.parse.urlsplit(url).path.endswith(".ts") else "*"
    return ('<DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" '
            'xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/">'
            f'<item id="0" parentID="-1" restricted="1"><dc:title>{xml_escape(title)}</dc:title>'
            '<upnp:class>object.item.videoItem</upnp:class>'
            f'<res protocolInfo="http-get:*:{mime}:{features}">{xml_escape(url)}</res></item></DIDL-Lite>')


DLNA_TS = ("DLNA.ORG_PN=AVC_TS_MP_HD_AAC;DLNA.ORG_OP=01;DLNA.ORG_CI=0;"
           "DLNA.ORG_FLAGS=01700000000000000000000000000000")


def make_ts_handler(fifo: Path, stopped: threading.Event, mime: str = "video/mpeg",
                    log=lambda message: None,
                    allowed_client: str | None = None) -> type[BaseHTTPRequestHandler]:
    """Connection-close framed live TS; one FIFO reader, bounded unbuffered reads."""
    viewer = threading.Lock()

    class TsHandler(BaseHTTPRequestHandler):
        timeout = 10

        def log_message(self, format: str, *args: Any) -> None:
            log(format % args)

        def do_HEAD(self) -> None:
            self.serve(False)

        def do_GET(self) -> None:
            self.serve(True)

        def serve(self, body: bool) -> None:
            if allowed_client and self.client_address[0] != allowed_client:
                self.send_error(403, "Only the target screen may view this stream")
                return
            if urllib.parse.urlsplit(self.path).path != "/live.ts":
                self.send_error(404)
                return
            if body and not viewer.acquire(blocking=False):
                self.send_error(409, "Only one live viewer is supported")
                return
            fd = None
            total = 0
            last = time.monotonic()
            try:
                self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.connection.settimeout(5)
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Cache-Control", "no-store")
                self.send_header("contentFeatures.dlna.org", DLNA_TS)
                self.send_header("transferMode.dlna.org", "Streaming")
                self.send_header("Connection", "close")
                self.end_headers()
                self.close_connection = True
                if not body:
                    return
                fd = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
                while not stopped.is_set():
                    if not select.select([fd], [], [], 0.2)[0]:
                        continue
                    try:
                        data = os.read(fd, 65536)
                    except BlockingIOError:
                        continue
                    if not data:
                        if total:
                            break
                        stopped.wait(0.05)
                        continue
                    self.wfile.write(data)
                    if not total:
                        log(f"TS first-byte client={self.client_address[0]} bytes={len(data)}")
                    total += len(data)
                    if time.monotonic() - last >= 5:
                        log(f"TS flow client={self.client_address[0]} bytes={total}")
                        last = time.monotonic()
            except (BrokenPipeError, ConnectionResetError, TimeoutError):
                pass
            finally:
                if fd is not None:
                    os.close(fd)
                if body:
                    log(f"TS disconnected bytes={total}")
                    viewer.release()
    return TsHandler


HLS_NAME = re.compile(r"^(live\.m3u8|seg\d{5}\.ts)$")


def make_hls_handler(directory: Path, log=lambda message: None,
                     allowed_client: str | None = None) -> type[BaseHTTPRequestHandler]:
    """Serve only the live playlist and its segments, with the MIME types TVs expect."""
    class HlsHandler(BaseHTTPRequestHandler):
        timeout = 10

        def do_HEAD(self) -> None:
            self.serve(False)

        def do_GET(self) -> None:
            self.serve(True)

        def log_message(self, format: str, *args: Any) -> None:
            log(format % args)

        def serve(self, send_body: bool) -> None:
            if allowed_client and self.client_address[0] != allowed_client:
                self.send_error(403, "Only the target screen may fetch this stream")
                return
            name = urllib.parse.urlsplit(self.path).path.lstrip("/")
            if not HLS_NAME.fullmatch(name):
                self.send_error(404, "Only the HLS playlist and segments are served")
                return
            try:
                media = (directory / name).open("rb", buffering=0)
                size = os.fstat(media.fileno()).st_size
            except OSError:
                self.send_error(404, "Not available yet")
                return
            with media:
                self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.connection.settimeout(5)
                self.send_response(200)
                self.send_header("Content-Type",
                                 "application/x-mpegurl" if name.endswith(".m3u8") else "video/mp2t")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(size))
                self.end_headers()
                if send_body:
                    total = 0
                    try:
                        while data := media.read(65536):
                            self.wfile.write(data)
                            total += len(data)
                        log(f"HLS served client={self.client_address[0]} file={name} bytes={total}")
                    except (BrokenPipeError, ConnectionResetError, TimeoutError):
                        log(f"HLS disconnected file={name} bytes={total}")
    return HlsHandler


def monitor(args: argparse.Namespace, device: dict[str, Any]) -> None:
    """Mirror a compositor output via progressive TS or segmented HLS."""
    service = find_service(device, "AVTransport")
    env = display_env()
    capture_bin = args.capture or shutil.which("wf-recorder")
    if not capture_bin:
        raise RuntimeError("wf-recorder not found; install it or pass --capture")
    ffmpeg_bin = args.ffmpeg_bin or shutil.which("ffmpeg")
    if args.transport == "hls" and not ffmpeg_bin:
        raise RuntimeError("ffmpeg not found; install it or pass --ffmpeg")
    run_dir = (Path(args.dir).expanduser() if args.dir
               else Path.home() / ".cache" / "remote-display" / "monitor")
    if run_dir.is_symlink():
        raise RuntimeError(f"refusing symlinked run directory: {run_dir}")
    if not run_dir.is_dir():
        run_dir.mkdir(parents=True, mode=0o700)
    for pattern in ("seg*.ts", "live.m3u8"):
        for stale in run_dir.glob(pattern):
            stale.unlink()
    fifo = run_dir / "capture.fifo"
    started = time.monotonic()
    stopped = threading.Event()
    def log(message):
        if args.verbose:
            print(f"latency +{time.monotonic() - started:.3f}s {message}", file=sys.stderr, flush=True)
    gop = args.fps
    capture_cmd = [capture_bin, "-y", "-o", args.output, "-D", "-r", str(args.fps), "-m", "mpegts",
                   "-c", "libx264", "-p", "preset=veryfast", "-p", "tune=zerolatency",
                   "-p", "x264-params=rc-lookahead=0:sync-lookahead=0:bframes=0",
                   "-p", f"g={gop}", "-p", "crf=23", "-f", str(fifo)]
    hls_cmd = [ffmpeg_bin, "-hide_banner", "-loglevel", "warning",
               "-analyzeduration", "0", "-probesize", "32768",
               "-f", "mpegts", "-i", str(fifo), "-an", "-c:v", "copy",
               "-f", "hls", "-hls_time", str(args.segment), "-hls_list_size", str(args.list_size),
               "-hls_flags", "delete_segments+omit_endlist+independent_segments+temp_file",
               "-hls_segment_filename", str(run_dir / "seg%05d.ts"), str(run_dir / "live.m3u8")]
    capture = hls = server = None
    previous = signal.signal(signal.SIGTERM, lambda *_: stopped.set())
    created_output = False
    fifo_keeper = None
    try:
        created_output = ensure_output(env, args.output, args.create_headless)
        advertised = args.advertise_ip or lan_ip(args.ip)
        if fifo.exists():
            fifo.unlink()
        os.mkfifo(fifo)
        if args.transport == "ts":
            # Samsung probes with a short GET before opening playback. Keep a
            # reader present between GETs so the recorder does not receive SIGPIPE.
            fifo_keeper = os.open(fifo, os.O_RDWR | os.O_NONBLOCK)
        capture = subprocess.Popen(capture_cmd, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL,
                                   stderr=None if args.verbose else subprocess.DEVNULL, env=env)
        if args.transport == "hls":
            hls = subprocess.Popen(hls_cmd, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL,
                                   stderr=None if args.verbose else subprocess.DEVNULL)
        deadline = time.monotonic() + 20
        while args.transport == "hls" and time.monotonic() < deadline:
            if stopped.is_set():
                return
            if (run_dir / "live.m3u8").is_file() and len(list(run_dir.glob("seg*.ts"))) >= 2:
                break
            if capture.poll() is not None or (hls is not None and hls.poll() is not None):
                raise RuntimeError("capture pipeline exited before producing HLS output")
            time.sleep(0.5)
        if args.transport == "hls" and (not (run_dir / "live.m3u8").is_file()
                                        or len(list(run_dir.glob("seg*.ts"))) < 2):
            raise RuntimeError("no HLS output produced within 20 seconds")
        allowed_client = None if args.allow_any_client else args.ip
        server = ThreadingHTTPServer((advertised, args.port),
                                     (make_hls_handler(run_dir, log, allowed_client) if hls else
                                      make_ts_handler(fifo, stopped, args.ts_mime, log, allowed_client)))
        server.daemon_threads = True
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f"http://{advertised}:{args.port}/live.{'m3u8' if hls else 'ts'}"
        log(f"pipeline-ready url={url}")
        try:
            soap_call(service, "Stop", {"InstanceID": 0}, args.timeout)
        except RuntimeError:
            pass
        soap_call(service, "SetAVTransportURI",
                  {"InstanceID": 0, "CurrentURI": url,
                   "CurrentURIMetaData": build_didl(url, "Desktop mirror", args.ts_mime if not hls else None)}, args.timeout)
        soap_call(service, "Play", {"InstanceID": 0, "Speed": 1}, args.timeout)
        print(f"Mirroring '{args.output}' to {device.get('name', args.ip)} via {url}", flush=True)
        print("Press Ctrl+C to stop; the screen cast and pipeline will be closed.", flush=True)
        finish_at = time.monotonic() + args.duration if args.duration else None
        published = set()
        while not stopped.is_set():
            if hls and args.verbose:
                segments = list(run_dir.glob("seg*.ts"))
                for segment in segments:
                    if segment.name not in published:
                        log(f"HLS published file={segment.name} mtime={segment.stat().st_mtime:.3f}")
                published = {segment.name for segment in segments}
            if finish_at and time.monotonic() >= finish_at:
                break
            if capture.poll() is not None or (hls is not None and hls.poll() is not None):
                raise RuntimeError("capture pipeline exited; mirror stopped")
            time.sleep(0.1)
    finally:
        try:
            soap_call(service, "Stop", {"InstanceID": 0}, args.timeout)
        except (RuntimeError, OSError, urllib.error.URLError):
            pass
        stopped.set()
        for process in (hls, capture):
            if process is not None and process.poll() is None:
                process.terminate()
        for process in (hls, capture):
            if process is not None and process.poll() is None:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        if server:
            server.shutdown()
            server.server_close()
        if fifo_keeper is not None:
            os.close(fifo_keeper)
        if fifo.exists():
            fifo.unlink()
        if created_output and not args.keep_headless:
            try:
                hyprctl(env, "output", "remove", args.output)
            except (RuntimeError, OSError, subprocess.TimeoutExpired):
                pass
        signal.signal(signal.SIGTERM, previous)


def play(args: argparse.Namespace, device: dict[str, Any]) -> None:
    service = find_service(device, "AVTransport")
    server = None
    worker = None
    source = args.source
    scheme = urllib.parse.urlsplit(source).scheme.lower()
    try:
        if scheme not in ("http", "https", "rtsp"):
            path = Path(source).expanduser().resolve()
            if not path.is_file():
                raise FileNotFoundError(f"Media file does not exist: {path}")
            advertised = args.advertise_ip or lan_ip(args.ip)
            # Bind to the advertised LAN address only, and serve only the target
            # screen by default: the file is not exposed to other LAN hosts.
            allowed_client = None if getattr(args, "allow_any_client", False) else args.ip
            server = ThreadingHTTPServer((advertised, args.port),
                                         make_media_handler(path, allowed_client))
            server.daemon_threads = True
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            source = f"http://{advertised}:{server.server_port}/{urllib.parse.quote(path.name, safe='')}"
        print(f"Media URL: {source}", flush=True)
        metadata = ""
        if scheme in ("http", "https") and urllib.parse.urlsplit(source).path.lower().endswith(".m3u8"):
            metadata = build_didl(source)
        soap_call(service, "SetAVTransportURI", {"InstanceID": 0, "CurrentURI": source,
                                                "CurrentURIMetaData": metadata}, args.timeout)
        soap_call(service, "Play", {"InstanceID": 0, "Speed": 1}, args.timeout)
        print("Play accepted.", flush=True)
        if server:
            try:
                time.sleep(args.duration)
            finally:
                if args.stop_at_end:
                    soap_call(service, "Stop", {"InstanceID": 0}, args.timeout)
    finally:
        if server:
            server.shutdown()
            server.server_close()
        if worker:
            worker.join(timeout=2)


def volume(args: argparse.Namespace, device: dict[str, Any]) -> None:
    service = find_service(device, "RenderingControl")
    base = {"InstanceID": 0, "Channel": "Master"}
    if args.mute or args.unmute:
        soap_call(service, "SetMute", {**base, "DesiredMute": int(args.mute)}, args.timeout)
        result = soap_call(service, "GetMute", base, args.timeout)
        print(f"Mute: {result.get('CurrentMute', 'unknown')}")
        return
    value = args.set
    if args.up or args.down:
        current = soap_call(service, "GetVolume", base, args.timeout)
        value = max(0, min(100, int(current["CurrentVolume"]) + (5 if args.up else -5)))
    if value is not None:
        soap_call(service, "SetVolume", {**base, "DesiredVolume": value}, args.timeout)
    result = soap_call(service, "GetVolume", base, args.timeout)
    print(f"Volume: {result.get('CurrentVolume', 'unknown')}")


def positive(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Must be a finite positive number")
    return number


def nonnegative(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("Must be a finite nonnegative number")
    return number


def timestamp(value: str) -> str:
    if not re.fullmatch(r"\d{1,2}:[0-5]\d:[0-5]\d", value):
        raise argparse.ArgumentTypeError("Provide a position as HH:MM:SS (MM and SS below 60)")
    return value


def ipv4(value: str) -> str:
    try:
        return str(ipaddress.IPv4Address(value))
    except ipaddress.AddressValueError as exc:
        raise argparse.ArgumentTypeError("Provide an IPv4 address") from exc


def lan_ipv4(value: str) -> str:
    normalized = ipv4(value)
    addr = ipaddress.IPv4Address(normalized)
    if addr.is_unspecified or addr.is_loopback or addr.is_multicast or addr.is_link_local:
        raise argparse.ArgumentTypeError("Provide a routable LAN IPv4 address")
    return normalized


def output_name(value: str) -> str:
    if value.startswith("-") or not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", value):
        raise argparse.ArgumentTypeError(
            "Use letters, digits, dot, underscore or dash (max 128, no leading dash)")
    return value


def bounded_integer(value: str, low: int, high: int) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Provide an integer") from exc
    if not low <= number <= high:
        raise argparse.ArgumentTypeError(f"Must be between {low} and {high}")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover LAN screens and cast media using DLNA/UPnP.")
    commands = parser.add_subparsers(dest="command", required=True)
    descriptions = {"discover": "Discover SSDP renderers and mDNS screen services.",
                    "info": "Show device details, services, and control URLs.",
                    "status": "Read playback state, URI, position, and duration.",
                    "play": "Cast a URL or serve one local media file with HTTP Range support.",
                    "pause": "Pause playback and read the resulting state.",
                    "stop": "Stop playback and read the resulting state.",
                    "volume": "Read or change master volume or mute.",
                    "seek": "Seek playback to an absolute position (HH:MM:SS).",
                    "wake": "Send a Wake-on-LAN magic packet to power on a screen.",
                    "monitor": "Mirror a screen via HLS (default) or progressive TS (wf-recorder).",
                    "mice-scan": "Find Miracast-over-Infrastructure advertisements."}
    for name, description in descriptions.items():
        sub = commands.add_parser(name, help=description, description=description)
        sub.add_argument("--timeout", type=positive, default=3, metavar="N",
                         help="Network wait in seconds per scan/request (default: 3).")
        if name in ("discover", "info", "status"):
            sub.add_argument("--json", action="store_true", help="Print structured JSON.")
        if name not in ("discover", "mice-scan", "wake"):
            sub.add_argument("ip", type=ipv4, help="Screen IPv4 address from discovery.")
        if name == "play":
            sub.add_argument("source", help="Local file path or HTTP/HTTPS/RTSP URL.")
            sub.add_argument("--port", type=lambda v: bounded_integer(v, 1, 65535), default=8124,
                             help="Local HTTP server port (default: 8124).")
            sub.add_argument("--advertise-ip", type=lan_ipv4, help="LAN IPv4 address advertised to the screen.")
            sub.add_argument("--duration", type=positive, default=600, metavar="N",
                             help="Keep the local server alive N seconds after Play (default: 600; must be > 0).")
            sub.add_argument("--stop-at-end", action="store_true", help="Stop playback before closing the local server.")
            sub.add_argument("--allow-any-client", action="store_true",
                             help="Allow any LAN host to fetch the file (default: only the target screen).")
        if name == "volume":
            group = sub.add_mutually_exclusive_group()
            group.add_argument("--get", action="store_true", help="Read volume (default action).")
            group.add_argument("--set", type=lambda v: bounded_integer(v, 0, 100), metavar="N", help="Set volume to 0–100.")
            group.add_argument("--up", action="store_true", help="Increase volume by 5, capped at 100.")
            group.add_argument("--down", action="store_true", help="Decrease volume by 5, floored at 0.")
            group.add_argument("--mute", action="store_true", help="Mute the master channel.")
            group.add_argument("--unmute", action="store_true", help="Unmute the master channel.")
        if name == "seek":
            sub.add_argument("position", type=timestamp, metavar="HH:MM:SS",
                             help="Target position (HH:MM:SS).")
        if name == "wake":
            sub.add_argument("target", help="Screen MAC address, or IPv4 address for ARP lookup.")
            sub.add_argument("--broadcast", default="255.255.255.255", type=ipv4,
                             help="Broadcast address (default: 255.255.255.255).")
            sub.add_argument("--port", type=lambda v: bounded_integer(v, 1, 65535), default=9,
                             help="UDP destination port (default: 9).")
        if name == "monitor":
            sub.add_argument("--transport", choices=("ts", "hls"), default="hls",
                             help="Live transport (default: hls; ts bypasses segmentation).")
            sub.add_argument("--ts-mime", choices=("video/mpeg", "video/mp2t"), default="video/mpeg",
                             help="Progressive TS HTTP and DIDL MIME type (default: video/mpeg).")
            sub.add_argument("--verbose", action="store_true", help="Log pipeline timing, requests and byte flow.")
            sub.add_argument("--output", required=True, metavar="NAME", type=output_name,
                             help="Compositor output to capture (e.g. HEADLESS-2).")
            sub.add_argument("--create-headless", action="store_true",
                             help="Create the output with hyprctl if missing (Hyprland only).")
            sub.add_argument("--fps", type=lambda v: bounded_integer(v, 1, 60), default=30,
                             help="Capture framerate (default: 30).")
            sub.add_argument("--port", type=lambda v: bounded_integer(v, 1, 65535), default=8124,
                             help="Local HTTP port (default: 8124).")
            sub.add_argument("--segment", type=positive, default=1, metavar="S",
                             help="HLS segment length in seconds (default: 1).")
            sub.add_argument("--list-size", type=lambda v: bounded_integer(v, 2, 60), default=3,
                             help="Playlist length in segments (default: 3).")
            sub.add_argument("--duration", type=nonnegative, default=0, metavar="N",
                             help="Stop after N seconds (0 = run until interrupted).")
            sub.add_argument("--dir", metavar="PATH",
                             help="Directory for HLS files (default: ~/.cache/remote-display/monitor).")
            sub.add_argument("--capture", metavar="PATH",
                             help="Capture binary (default: wf-recorder from PATH).")
            sub.add_argument("--ffmpeg", dest="ffmpeg_bin", metavar="PATH",
                             help="ffmpeg binary (default: ffmpeg from PATH).")
            sub.add_argument("--advertise-ip", type=lan_ipv4, metavar="IP",
                             help="LAN IPv4 address advertised to the screen.")
            sub.add_argument("--allow-any-client", action="store_true",
                             help="Allow any LAN host to watch the stream (default: only the target screen).")
            sub.add_argument("--keep-headless", action="store_true",
                             help="Keep a headless output created by this run on exit (default: remove it).")
    return parser


def output(value: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, indent=2, ensure_ascii=False))
    elif isinstance(value, list):
        for item in value:
            output(item, False)
            print()
    elif isinstance(value, dict):
        for key, item in value.items():
            print(f"{key}: {json.dumps(item, ensure_ascii=False) if isinstance(item, (list, dict)) else item}")
    else:
        print(value)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "discover":
            devices = discover(args.timeout)
            output(devices, args.json)
            if not devices:
                print("No screens found.", file=sys.stderr)
                return 2
        elif args.command == "mice-scan":
            sinks = mdns_scan(args.timeout, ("_display._tcp.local",))
            if not sinks:
                print("No MICE sinks found; most TVs do not advertise _display._tcp.local.")
                return 2
            output(sinks, False)
            print("Suggested helper command: gnome-network-displays")
        elif args.command == "wake":
            wake(args)
        else:
            device = resolve_device(args.ip, args.timeout)
            if args.command == "info":
                # Enrich UPnP metadata when the optional Tizen API is available.
                if "tizen_keys" not in device:
                    try:
                        data = json.loads(read_http(f"http://{args.ip}:8001/api/v2/", args.timeout))
                        if isinstance(data, dict):
                            device["tizen_keys"] = sorted(data)
                            if isinstance(data.get("device"), dict):
                                device["tizen_device_keys"] = sorted(data["device"])
                    except (OSError, ValueError):
                        pass
                output(device, args.json)
            elif args.command == "status":
                output(get_status(device, args.timeout), args.json)
            elif args.command == "play":
                play(args, device)
            elif args.command == "volume":
                volume(args, device)
            elif args.command == "seek":
                seek(args, device)
            elif args.command == "monitor":
                monitor(args, device)
            else:
                soap_call(find_service(device, "AVTransport"), args.command.title(),
                          {"InstanceID": 0}, args.timeout)
                output(get_status(device, args.timeout), False)
        return 0
    except (NotFound, TimeoutError) as exc:
        print(f"Not found or timed out: {exc}", file=sys.stderr)
        return 2
    except urllib.error.URLError as exc:
        print(f"Network error: {exc.reason}", file=sys.stderr)
        return 2 if isinstance(exc.reason, TimeoutError) else 1
    except (OSError, ValueError, ET.ParseError, RuntimeError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
