"""Offline checks: synthetic protocol data, mocked requests, loopback HTTP only."""
from pathlib import Path
import argparse
import contextlib
import io
import json
import socket
import struct
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from unittest.mock import Mock, mock_open, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import remote_display as rd

FIXTURES = Path(__file__).parent / "fixtures"
LOCATION = "http://renderer.invalid/rootDesc.xml"


def fixture_device():
    return rd.parse_description((FIXTURES / "rootDesc.xml").read_bytes(), LOCATION)


class ParserTests(unittest.TestCase):
    def test_ssdp_fixture(self):
        headers = rd.parse_ssdp_response((FIXTURES / "ssdp_response.txt").read_bytes())
        self.assertEqual(headers["LOCATION"], LOCATION)
        self.assertEqual(headers["ST"], rd.RENDERER)
        self.assertTrue(headers["USN"].startswith("uuid:synthetic-renderer"))
        self.assertEqual(rd.parse_ssdp_response(b"garbage"), {})
        self.assertEqual(rd.parse_ssdp_response(b"HTTP/1.1 404 Missing"), {})

    def test_description_fixture(self):
        device = fixture_device()
        self.assertEqual(device["name"], "Synthetic renderer")
        self.assertEqual(device["model"], "Fixture model")
        self.assertEqual(rd.find_service(device, "AVTransport")["controlURL"],
                         "http://renderer.invalid/control/transport")
        self.assertEqual(rd.find_service(device, "RenderingControl")["controlURL"],
                         "http://renderer.invalid/control/rendering")
        self.assertTrue(device["AVTransport"])
        self.assertTrue(device["RenderingControl"])

    def test_description_urlbase_and_embedded_renderer(self):
        data = '''<root><URLBase>http://fixture.invalid/base/</URLBase><device>
        <friendlyName>Parent</friendlyName><deviceList><device>
        <deviceType>urn:schemas-upnp-org:device:MediaRenderer:1</deviceType>
        <friendlyName>Child</friendlyName><serviceList><service>
        <serviceType>urn:schemas-upnp-org:service:AVTransport:1</serviceType>
        <controlURL>control</controlURL></service></serviceList>
        </device></deviceList></device></root>'''
        device = rd.parse_description(data, LOCATION)
        self.assertEqual(device["name"], "Child")
        self.assertEqual(rd.find_service(device, "AVTransport")["controlURL"],
                         "http://fixture.invalid/base/control")

    def test_soap_escaping(self):
        service = rd.find_service(fixture_device(), "AVTransport")
        metadata = '<title>Audio & video</title>'
        data = rd.build_soap_envelope(service["serviceType"], "SetAVTransportURI",
                                      {"CurrentURIMetaData": metadata})
        self.assertIn(b"&amp;", data)
        values = rd.xml_values(data)
        self.assertEqual(values["CurrentURIMetaData"], metadata)
        root = ET.fromstring(data)
        self.assertTrue(any(e.tag == f"{{{service['serviceType']}}}SetAVTransportURI"
                            for e in root.iter()))

    def test_transport_fixture(self):
        data = (FIXTURES / "transport_info.xml").read_bytes()
        self.assertEqual(rd.xml_values(data)["CurrentTransportState"], "PLAYING")

    def test_dns_compression_and_service_join(self):
        packet = (FIXTURES / "mdns_packet.bin").read_bytes()
        name, next_offset = rd.parse_dns_name(packet, 12)
        self.assertEqual(name, "_display._tcp.local")
        compressed_offset = next_offset + 4
        self.assertEqual(rd.parse_dns_name(packet, compressed_offset), (name, compressed_offset + 2))
        services = rd.mdns_services(rd.parse_mdns_packet(packet), (name,))
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]["name"], "Synthetic._display._tcp.local")
        self.assertEqual(services[0]["target"], "sink.local")
        self.assertEqual(services[0]["port"], 7250)
        self.assertEqual(services[0]["txt"], ["version=1"])
        self.assertEqual(services[0]["ip"], socket.inet_ntoa(bytes(4)))

    def test_malformed_dns(self):
        for packet, offset in [(b'\xc0\x00', 0), (b'\xc0', 0), (b'\xff\xff', 0),
                               (b'\x05abc', 0), (b'\x40', 0)]:
            with self.subTest(packet=packet), self.assertRaises(ValueError):
                rd.parse_dns_name(packet, offset)
        packet = (FIXTURES / "mdns_packet.bin").read_bytes()
        for end in range(len(packet)):
            with self.subTest(end=end), self.assertRaises((ValueError, struct.error)):
                rd.parse_mdns_packet(packet[:end])

    def test_content_types(self):
        for extension, expected in [("mp4", "video/mp4"), ("jpg", "image/jpeg"),
                                     ("mp3", "audio/mpeg"), ("MP4", "video/mp4")]:
            self.assertEqual(rd.content_type_for("media." + extension), expected)

    def test_range_header(self):
        self.assertEqual(rd.parse_range_header("bytes=0-499", 1000), (0, 499))
        self.assertEqual(rd.parse_range_header("bytes=100-", 1000), (100, 999))
        self.assertEqual(rd.parse_range_header("bytes=-20", 1000), (980, 999))
        self.assertEqual(rd.parse_range_header("bytes=0-9999", 1000), (0, 999))
        self.assertIsNone(rd.parse_range_header(None, 1000))
        for header in ("invalid", "bytes=-", "bytes=10-2", "bytes=1000-", "bytes=-0",
                       "bytes=0-1,3-4"):
            with self.subTest(header=header), self.assertRaises(ValueError):
                rd.parse_range_header(header, 1000)
        with self.assertRaises(ValueError):
            rd.parse_range_header("bytes=0-", 0)


class ProtocolTests(unittest.TestCase):
    def test_soap_headers_version_and_status(self):
        device = fixture_device()
        with patch.object(rd, "read_http", return_value=(FIXTURES / "transport_info.xml").read_bytes()) as call:
            rd.soap_call(rd.find_service(device, "AVTransport"), "GetTransportInfo", {"InstanceID": 0})
            self.assertEqual(call.call_args.args[3]["SOAPACTION"],
                             '"urn:schemas-upnp-org:service:AVTransport:2#GetTransportInfo"')
        with patch.object(rd, "soap_call", side_effect=[{"CurrentTransportState": "PLAYING"},
                {"TrackURI": "http://media.invalid/movie.mp4", "RelTime": "00:00:12", "TrackDuration": "00:01:00"}]):
            result = rd.get_status(device, 1)
            self.assertEqual(result["TransportState"], "PLAYING")
            self.assertEqual(result["position"], "00:00:12")
            self.assertEqual(result["duration"], "00:01:00")

    def test_soap_fault(self):
        fault = b'<Envelope><Body><Fault><detail><errorDescription>Unsupported action</errorDescription></detail></Fault></Body></Envelope>'
        with patch.object(rd, "read_http", return_value=fault), self.assertRaisesRegex(RuntimeError, "Unsupported action"):
            rd.soap_call(rd.find_service(fixture_device(), "AVTransport"), "Play", {})
        error = urllib.error.HTTPError(LOCATION, 500, "Failure", {}, io.BytesIO(fault))
        with patch.object(rd, "read_http", side_effect=error), self.assertRaisesRegex(RuntimeError, "Unsupported action"):
            rd.soap_call(rd.find_service(fixture_device(), "AVTransport"), "Play", {})

    def test_read_http_rejects_non_http_schemes(self):
        for url in ("file:///etc/passwd", "ftp://host/x", "data:text/plain,hi"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                rd.read_http(url, 1)

    def test_url_opener_has_no_file_or_ftp_dispatch(self):
        for url in ("file:///etc/hostname", "ftp://127.0.0.1/any"):
            with self.subTest(url=url), self.assertRaises(urllib.error.URLError):
                rd.HTTP.open(url, timeout=1)

    def test_description_url_scheme_restrictions(self):
        bad_base = ('<root><URLBase>file:///etc/</URLBase><device><friendlyName>X</friendlyName>'
                    '<serviceList><service><serviceType>urn:schemas-upnp-org:service:AVTransport:1'
                    '</serviceType><controlURL>control</controlURL></service></serviceList>'
                    '</device></root>')
        with self.assertRaises(ValueError):
            rd.parse_description(bad_base, LOCATION)
        bad_service = ('<root><device><friendlyName>X</friendlyName><serviceList><service>'
                       '<serviceType>urn:schemas-upnp-org:service:AVTransport:1</serviceType>'
                       '<controlURL>file:///etc/passwd</controlURL></service></serviceList>'
                       '</device></root>')
        with self.assertRaises(ValueError):
            rd.parse_description(bad_service, LOCATION)
        ok_service = ('<root><URLBase>https://fixture.invalid/base/</URLBase><device>'
                      '<friendlyName>Ok</friendlyName><serviceList><service>'
                      '<serviceType>urn:schemas-upnp-org:service:AVTransport:1</serviceType>'
                      '<controlURL>control</controlURL></service></serviceList></device></root>')
        device = rd.parse_description(ok_service, LOCATION)
        self.assertEqual(rd.find_service(device, "AVTransport")["controlURL"],
                         "https://fixture.invalid/base/control")

    def test_xml_documents_reject_doctype_and_entities(self):
        payload = b'<!DOCTYPE a [<!ENTITY e "expanded">]><a><b>&e;</b></a>'
        with self.assertRaises(ValueError):
            rd.xml_values(payload)
        with self.assertRaises(ValueError):
            rd.parse_description(payload, LOCATION)
        padded = b"<!-- " + b"x" * 5000 + b" --><!DOCTYPE a><a/>"
        with self.assertRaises(ValueError):
            rd.xml_values(padded)

    def test_discovery_deduplicates_and_keeps_services(self):
        device = fixture_device()
        services = [{"ip": device["ip"], "name": "instance", "target": "target",
                     "type": kind, "port": 1, "txt": []} for kind in rd.MDNS_TYPES[:2]]
        with patch.object(rd, "ssdp_search", return_value=[LOCATION, LOCATION + "?other"]), \
             patch.object(rd, "fetch_description", return_value=device), \
             patch.object(rd, "mdns_scan", return_value=services):
            result = rd.discover(1)
            self.assertEqual(len(result), 1)
            self.assertEqual(len(result[0]["mdns"]), 2)

    def test_ssdp_scan_skips_bad_location_and_deduplicates(self):
        address = socket.inet_ntoa(bytes(4))
        good = (FIXTURES / "ssdp_response.txt").read_bytes()
        bad = b"HTTP/1.1 200 OK\r\nLOCATION: http://[invalid/\r\n"
        with patch.object(rd.socket, "socket") as factory:
            sock = factory.return_value.__enter__.return_value
            sock.recvfrom.side_effect = [(bad, (address, 1900)), (good, (address, 1900)),
                                        (good, (address, 1900)), socket.timeout()]
            self.assertEqual(rd.ssdp_search(1), [LOCATION])

    def test_direct_probe_fallback(self):
        address = socket.inet_ntoa(bytes(4))
        with patch.object(rd, "ssdp_search", return_value=[]), \
             patch.object(rd, "fetch_description", side_effect=OSError("not UPnP")), \
             patch.object(rd, "read_http", return_value=b'{"device":{"modelName":"Fixture"},"type":"fixture"}'):
            device = rd.resolve_device(address, 1)
            self.assertEqual(device["model"], "Fixture")
            self.assertEqual(device["tizen_keys"], ["device", "type"])
            with self.assertRaises(rd.NotFound):
                rd.find_service(device, "AVTransport")

    def test_exit_codes_and_json(self):
        for failure, expected in [(rd.NotFound("missing"), 2), (TimeoutError("wait"), 2),
                                  (OSError("network"), 1),
                                  (urllib.error.URLError(TimeoutError("wait")), 2)]:
            with patch.object(rd, "discover", side_effect=failure), \
                 contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(rd.main(["discover"]), expected)
                self.assertNotIn("Traceback", errors.getvalue())
        with patch.object(rd, "discover", return_value=[]), \
             contextlib.redirect_stdout(io.StringIO()) as out, \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(rd.main(["discover", "--json"]), 2)
            self.assertEqual(json.loads(out.getvalue()), [])

    def test_url_play_never_starts_server(self):
        args = argparse.Namespace(source="http://media.invalid/movie.mp4", timeout=1)
        with patch.object(rd, "soap_call") as soap, patch.object(rd, "ThreadingHTTPServer") as server, \
             contextlib.redirect_stdout(io.StringIO()):
            rd.play(args, fixture_device())
            server.assert_not_called()
            self.assertEqual([c.args[1] for c in soap.call_args_list], ["SetAVTransportURI", "Play"])
            self.assertEqual(soap.call_args_list[0].args[2]["CurrentURIMetaData"], "")

    def test_local_play_cleanup_and_stop(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / "movie.mp4"
            path.write_bytes(b"media")
            args = argparse.Namespace(source=str(path), timeout=1, ip=socket.inet_ntoa(bytes(4)),
                                      port=0, advertise_ip="localhost", duration=0, stop_at_end=True)
            with patch.object(rd, "soap_call") as soap, contextlib.redirect_stdout(io.StringIO()) as out:
                rd.play(args, fixture_device())
                self.assertEqual([c.args[1] for c in soap.call_args_list],
                                 ["SetAVTransportURI", "Play", "Stop"])
                self.assertIn("movie.mp4", out.getvalue())
                url = soap.call_args_list[0].args[2]["CurrentURI"]
                with self.assertRaises(urllib.error.URLError):
                    rd.read_http(url, 0.2)

    def test_volume_clamping_and_mute(self):
        args = argparse.Namespace(timeout=1, set=None, up=True, down=False, mute=False, unmute=False)
        with patch.object(rd, "soap_call", side_effect=[{"CurrentVolume": "99"}, {}, {"CurrentVolume": "100"}]) as call, \
             contextlib.redirect_stdout(io.StringIO()):
            rd.volume(args, fixture_device())
            self.assertEqual(call.call_args_list[1].args[2]["DesiredVolume"], 100)
        args.mute = True
        with patch.object(rd, "soap_call", side_effect=[{}, {"CurrentMute": "1"}]) as call, \
             contextlib.redirect_stdout(io.StringIO()) as out:
            rd.volume(args, fixture_device())
            self.assertEqual(call.call_args_list[0].args[1], "SetMute")
            self.assertEqual(out.getvalue().strip(), "Mute: 1")

    def test_mdns_scan_skips_malformed_packet(self):
        packet = (FIXTURES / "mdns_packet.bin").read_bytes()
        with patch.object(rd.socket, "socket") as factory:
            sock = factory.return_value.__enter__.return_value
            sock.recvfrom.side_effect = [(b"broken", ("localhost", 5353)),
                                        (packet, ("localhost", 5353)), socket.timeout()]
            services = rd.mdns_scan(1, ("_display._tcp.local",))
            self.assertEqual(len(services), 1)
            sock.bind.assert_called_once_with(("", 5353))
            self.assertIn(unittest.mock.call(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255),
                          sock.setsockopt.call_args_list)


class MediaServerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.path = Path(self.directory.name) / "media clip.mp4"
        self.path.write_bytes(b"0123456789")
        self.server = rd.ThreadingHTTPServer(("localhost", 0), rd.make_media_handler(self.path))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://localhost:{self.server.server_port}/media%20clip.mp4"
        self.client = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.directory.cleanup()

    def request(self, method="GET", path=None, range_header=None):
        headers = {"Range": range_header} if range_header else {}
        return self.client.open(urllib.request.Request(path or self.url, headers=headers, method=method), timeout=2)

    def test_full_get_and_head(self):
        with self.request() as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Content-Type"], "video/mp4")
            self.assertEqual(response.read(), b"0123456789")
        with self.request("HEAD") as response:
            self.assertEqual(response.headers["Content-Length"], "10")
            self.assertEqual(response.read(), b"")

    def test_range_get_head_and_suffix(self):
        for method in ("GET", "HEAD"):
            with self.request(method, range_header="bytes=2-5") as response:
                self.assertEqual(response.status, 206)
                self.assertEqual(response.headers["Content-Range"], "bytes 2-5/10")
                self.assertEqual(response.headers["Content-Length"], "4")
                self.assertEqual(response.read(), b"2345" if method == "GET" else b"")
        with self.request(range_header="bytes=-3") as response:
            self.assertEqual(response.read(), b"789")
        with self.request(range_header="bytes=7-") as response:
            self.assertEqual(response.read(), b"789")

    def test_invalid_range_and_other_path(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request(range_header="bytes=999-")
        self.assertEqual(caught.exception.code, 416)
        self.assertEqual(caught.exception.headers["Content-Range"], "bytes */10")
        caught.exception.close()
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request(path=self.url + "/../other")
        self.assertEqual(caught.exception.code, 404)
        caught.exception.close()

    def test_client_restriction_403(self):
        server = rd.ThreadingHTTPServer(("localhost", 0),
                                        rd.make_media_handler(self.path, allowed_client="192.0.2.9"))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(
                    f"http://localhost:{server.server_port}/media%20clip.mp4", timeout=2)
            self.assertEqual(caught.exception.code, 403)
            caught.exception.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


class WakeTests(unittest.TestCase):
    @contextlib.contextmanager
    def _fake_socket(self, sent):
        class FakeSocket:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def setsockopt(self, *args):
                pass

            def sendto(self, data, destination):
                sent.append((data, destination))

        with patch.object(rd.socket, "socket", return_value=FakeSocket()):
            yield

    def test_magic_packet_for_mac_target(self):
        args = argparse.Namespace(target="AA:BB:CC:DD:EE:FF", broadcast="255.255.255.255", port=9)
        sent = []
        with self._fake_socket(sent), contextlib.redirect_stdout(io.StringIO()) as out:
            rd.wake(args)
        expected = b"\xff" * 6 + bytes.fromhex("aabbccddeeff") * 16
        self.assertEqual(sent, [(expected, ("255.255.255.255", 9))])
        self.assertIn("aa:bb:cc:dd:ee:ff", out.getvalue())

    def test_magic_packet_for_ip_target_uses_arp(self):
        args = argparse.Namespace(target="192.0.2.10", broadcast="192.0.2.255", port=7)
        sent = []
        with patch.object(rd, "mac_from_arp", return_value="aa:bb:cc:dd:ee:ff"), \
             self._fake_socket(sent), contextlib.redirect_stdout(io.StringIO()):
            rd.wake(args)
        self.assertEqual([dest for _, dest in sent], [("192.0.2.255", 7), ("192.0.2.10", 7)])

    def test_wake_ip_without_arp_entry_raises_not_found(self):
        args = argparse.Namespace(target="192.0.2.10", broadcast="255.255.255.255", port=9)
        with patch.object(rd, "mac_from_arp", return_value=None), self.assertRaises(rd.NotFound):
            rd.wake(args)

    def test_wake_ip_with_invalid_arp_mac_raises_not_found(self):
        args = argparse.Namespace(target="192.0.2.10", broadcast="255.255.255.255", port=9)
        with patch.object(rd, "mac_from_arp", return_value="not-a-mac"), self.assertRaises(rd.NotFound):
            rd.wake(args)

    def test_wake_rejects_invalid_target(self):
        args = argparse.Namespace(target="not-a-mac-or-ip", broadcast="255.255.255.255", port=9)
        with self.assertRaises(ValueError):
            rd.wake(args)

    def test_mac_from_arp_table(self):
        table = ("IP address       HW type     Flags       HW address            Mask     Device\n"
                 "192.0.2.10       0x1         0x2         aa:bb:cc:dd:ee:ff     *        eth0\n"
                 "192.0.2.11       0x1         0x0         00:00:00:00:00:00     *        eth0\n")
        with patch("builtins.open", mock_open(read_data=table)):
            self.assertEqual(rd.mac_from_arp("192.0.2.10"), "aa:bb:cc:dd:ee:ff")
            self.assertIsNone(rd.mac_from_arp("192.0.2.11"))
            self.assertIsNone(rd.mac_from_arp("192.0.2.99"))


class TransportExtrasTests(unittest.TestCase):
    def test_seek_sends_rel_time_and_reads_status(self):
        args = argparse.Namespace(position="00:01:30", timeout=1)
        side = [{}, {"CurrentTransportState": "PLAYING"},
                {"TrackURI": "http://media.invalid/movie.mp4", "RelTime": "00:01:30",
                 "TrackDuration": "00:02:00"}]
        with patch.object(rd, "soap_call", side_effect=side) as call, \
             contextlib.redirect_stdout(io.StringIO()) as out:
            rd.seek(args, fixture_device())
        self.assertEqual(call.call_args_list[0].args[1], "Seek")
        self.assertEqual(call.call_args_list[0].args[2],
                         {"InstanceID": 0, "Unit": "REL_TIME", "Target": "00:01:30"})
        self.assertIn("00:01:30", out.getvalue())

    def test_seek_parser_requires_hh_mm_ss(self):
        parser = rd.build_parser()
        self.assertEqual(parser.parse_args(["seek", "192.0.2.1", "01:02:03"]).position, "01:02:03")
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(["seek", "192.0.2.1", "90:00"])

    def test_wake_parser_defaults(self):
        parser = rd.build_parser()
        args = parser.parse_args(["wake", "AA:BB:CC:DD:EE:FF"])
        self.assertEqual((args.broadcast, args.port), ("255.255.255.255", 9))

    def test_build_didl_protocol_and_escape(self):
        didl = rd.build_didl("http://192.0.2.1:8124/live.m3u8", "Desk & TV")
        self.assertIn("application/x-mpegurl", didl)
        self.assertIn("Desk &amp; TV", didl)
        plain = rd.build_didl("http://192.0.2.1/movie.mp4")
        self.assertIn("video/mp4", plain)

    def test_url_play_sends_didl_for_m3u8(self):
        args = argparse.Namespace(source="http://media.invalid/live.m3u8", timeout=1)
        with patch.object(rd, "soap_call") as soap, contextlib.redirect_stdout(io.StringIO()):
            rd.play(args, fixture_device())
        metadata = soap.call_args_list[0].args[2]["CurrentURIMetaData"]
        self.assertIn("application/x-mpegurl", metadata)

    def test_monitor_parser_defaults(self):
        args = rd.build_parser().parse_args(["monitor", "192.0.2.7", "--output", "HEADLESS-9"])
        self.assertEqual((args.fps, args.port, args.list_size), (30, 8124, 3))
        self.assertEqual(args.duration, 0)
        self.assertEqual((args.transport, args.segment, args.ts_mime), ("hls", 1, "video/mpeg"))
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            rd.build_parser().parse_args(["monitor", "192.0.2.7"])

    def test_parser_security_validations(self):
        parser = rd.build_parser()
        for argv in (["play", "192.0.2.7", "x.mp4", "--advertise-ip", "0.0.0.0"],
                     ["play", "192.0.2.7", "x.mp4", "--advertise-ip", "127.0.0.1"],
                     ["monitor", "192.0.2.7", "--output", "-bad"],
                     ["monitor", "192.0.2.7", "--output", "bad/name"],
                     ["play", "192.0.2.7", "x.mp4", "--duration", "0"],
                     ["seek", "192.0.2.7", "00:60:00"],
                     ["seek", "192.0.2.7", "0\u0660:00:00"],
                     ["wake", "AA:BB:CC:DD:EE:FF", "--broadcast", "not-an-ip"]):
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()), \
                 self.assertRaises(SystemExit):
                parser.parse_args(argv)

    def test_monitor_new_flags_and_handler_timeouts(self):
        args = rd.build_parser().parse_args(["monitor", "192.0.2.7", "--output", "HEADLESS-9",
                                             "--keep-headless", "--allow-any-client"])
        self.assertTrue(args.keep_headless)
        self.assertTrue(args.allow_any_client)
        self.assertEqual(rd.make_media_handler(Path("x")).timeout, 10)
        self.assertEqual(rd.make_hls_handler(Path("/tmp")).timeout, 10)
        self.assertEqual(rd.make_ts_handler(Path("/tmp/f"), threading.Event()).timeout, 10)
        self.assertIsNone(rd.HLS_NAME.fullmatch("live.m3u8\n"))


class HlsServerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.root = Path(self.directory.name)
        (self.root / "live.m3u8").write_bytes(b"#EXTM3U\n#EXTINF:1.0,\nseg00001.ts\n")
        (self.root / "seg00001.ts").write_bytes(b"\x47" * 188)
        (self.root / "notes.txt").write_bytes(b"private")
        self.server = rd.ThreadingHTTPServer(("localhost", 0), rd.make_hls_handler(self.root))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://localhost:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.directory.cleanup()

    def test_serves_playlist_with_hls_mime(self):
        with urllib.request.urlopen(self.base + "/live.m3u8", timeout=2) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            self.assertEqual(response.headers["Content-Type"], "application/x-mpegurl")
            self.assertIn(b"#EXTM3U", response.read())

    def test_serves_segment_with_ts_mime(self):
        with urllib.request.urlopen(self.base + "/seg00001.ts", timeout=2) as response:
            self.assertEqual(response.headers["Content-Type"], "video/mp2t")

    def test_rejects_anything_else(self):
        for path in ("/notes.txt", "/../live.m3u8", "/", "/sneaky"):
            with self.subTest(path=path):
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(self.base + path, timeout=2)
                self.assertEqual(caught.exception.code, 404)
                caught.exception.close()

    def test_missing_segment_is_404(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(self.base + "/seg00099.ts", timeout=2)
        self.assertEqual(caught.exception.code, 404)
        caught.exception.close()

    def test_client_restriction_403_and_match(self):
        for allowed, expect_ok in (("192.0.2.9", False), ("127.0.0.1", True)):
            with self.subTest(allowed=allowed):
                server = rd.ThreadingHTTPServer(("localhost", 0),
                                                rd.make_hls_handler(self.root, allowed_client=allowed))
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    url = f"http://localhost:{server.server_port}/live.m3u8"
                    if expect_ok:
                        with urllib.request.urlopen(url, timeout=2) as response:
                            self.assertEqual(response.status, 200)
                    else:
                        with self.assertRaises(urllib.error.HTTPError) as caught:
                            urllib.request.urlopen(url, timeout=2)
                        self.assertEqual(caught.exception.code, 403)
                        caught.exception.close()
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join()




class TsServerTests(unittest.TestCase):
    def test_metadata_matches_both_mime_variants(self):
        for mime in ("video/mpeg", "video/mp2t"):
            root = ET.fromstring(rd.build_didl("http://example/live.ts", mime=mime))
            res = root.find(".//{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}res")
            self.assertEqual(res.attrib["protocolInfo"], f"http-get:*:{mime}:{rd.DLNA_TS}")

    def test_live_stream_head_exclusion_and_shutdown(self):
        import os
        with tempfile.TemporaryDirectory() as directory:
            fifo = Path(directory) / "capture.fifo"
            os.mkfifo(fifo)
            keeper = os.open(fifo, os.O_RDWR | os.O_NONBLOCK)
            stopped = threading.Event()
            server = rd.ThreadingHTTPServer(("localhost", 0), rd.make_ts_handler(fifo, stopped))
            server.daemon_threads = True
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            url = f"http://localhost:{server.server_port}/live.ts"
            try:
                with urllib.request.urlopen(urllib.request.Request(url, method="HEAD"), timeout=2) as head:
                    self.assertEqual(head.headers["contentFeatures.dlna.org"], rd.DLNA_TS)
                    self.assertEqual(head.headers["Cache-Control"], "no-store")
                with urllib.request.urlopen(url, timeout=2) as first:
                    with self.assertRaises(urllib.error.HTTPError) as caught:
                        urllib.request.urlopen(url, timeout=2)
                    self.assertEqual(caught.exception.code, 409)
                    caught.exception.close()
                    payload = b"\x47" * 188
                    os.write(keeper, payload)
                    self.assertEqual(first.read(188), payload)
                    stopped.set()
                    self.assertEqual(first.read(), b"")
            finally:
                stopped.set()
                server.shutdown()
                server.server_close()
                thread.join()
                os.close(keeper)


class MonitorLifecycleTests(unittest.TestCase):
    def test_ts_needs_no_ffmpeg_and_cleans_up_on_cast_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            args = rd.build_parser().parse_args([
                "monitor", "192.0.2.7", "--output", "HEADLESS-9", "--transport", "ts",
                "--capture", "/fake/capture", "--advertise-ip", "192.0.2.7", "--dir", directory])
            capture = Mock()
            capture.poll.return_value = None
            server = Mock()
            with patch.object(rd, "display_env", return_value={}), \
                 patch.object(rd, "ensure_output", return_value=False), \
                 patch.object(rd.shutil, "which", return_value=None), \
                 patch.object(rd.subprocess, "Popen", return_value=capture) as spawn, \
                 patch.object(rd, "ThreadingHTTPServer", return_value=server), \
                 patch.object(rd, "soap_call", side_effect=RuntimeError("cast rejected")):
                with self.assertRaisesRegex(RuntimeError, "cast rejected"):
                    rd.monitor(args, fixture_device())
                self.assertEqual(spawn.call_count, 1)
                command = spawn.call_args.args[0]
                self.assertIn("x264-params=rc-lookahead=0:sync-lookahead=0:bframes=0", command)
                self.assertIn("g=30", command)
                capture.terminate.assert_called_once()
                capture.wait.assert_called_once()
                server.server_close.assert_called_once()
                self.assertFalse((Path(directory) / "capture.fifo").exists())

    def test_hls_spawn_failure_reaps_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            args = rd.build_parser().parse_args([
                "monitor", "192.0.2.7", "--output", "HEADLESS-9", "--transport", "hls",
                "--capture", "/fake/capture", "--ffmpeg", "/fake/ffmpeg",
                "--advertise-ip", "192.0.2.7", "--dir", directory])
            capture = Mock()
            capture.poll.return_value = None
            with patch.object(rd, "display_env", return_value={}), \
                 patch.object(rd, "ensure_output", return_value=False), \
                 patch.object(rd.subprocess, "Popen", side_effect=[capture, OSError("spawn failed")]), \
                 patch.object(rd, "soap_call"):
                with self.assertRaisesRegex(OSError, "spawn failed"):
                    rd.monitor(args, fixture_device())
                capture.terminate.assert_called_once()
                capture.wait.assert_called_once()
                self.assertFalse((Path(directory) / "capture.fifo").exists())

    def test_ensure_output_timeout_removes_created_output(self):
        with patch.object(rd, "output_present", return_value=False), \
             patch.object(rd, "hyprctl") as hyprctl, \
             patch.object(rd.time, "time", side_effect=[0, 0, 11]), \
             patch.object(rd.time, "sleep"):
            with self.assertRaisesRegex(RuntimeError, "did not appear"):
                rd.ensure_output({}, "HEADLESS-9", create=True)
        self.assertIn(unittest.mock.call({}, "output", "remove", "HEADLESS-9"),
                      hyprctl.call_args_list)

    def test_monitor_refuses_symlinked_run_dirs(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "real" / "sub").mkdir(parents=True)
            (base / "link").symlink_to(base / "real", target_is_directory=True)
            (base / "plink").symlink_to(base / "real", target_is_directory=True)
            for target in (base / "link", base / "plink" / "sub"):
                with self.subTest(target=str(target)):
                    args = rd.build_parser().parse_args([
                        "monitor", "192.0.2.7", "--output", "HEADLESS-9",
                        "--capture", "/fake/capture", "--ffmpeg", "/fake/ffmpeg",
                        "--dir", str(target)])
                    with patch.object(rd, "display_env", return_value={}), \
                         patch.object(rd.shutil, "which", return_value=None):
                        with self.assertRaisesRegex(RuntimeError, "symlinked run directory"):
                            rd.monitor(args, fixture_device())


if __name__ == "__main__":
    unittest.main()
