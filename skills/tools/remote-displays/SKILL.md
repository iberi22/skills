---
name: remote-displays
id: remote-displays
category: tools
description: Discover, cast to, and control screens on the LAN.
version: 0.4.0
authors: [Brahyan Belalcazar (iberi22), Hermes Agent]
license: MIT
platforms: [linux]
tags: [displays, dlna, upnp, casting, smart-tv, ssdp, mdns, hls]
goals:
  - "Find smart TVs and UPnP/DLNA renderers on a LAN and cast files, URLs, or live streams to them."
  - "Control playback, volume, seeking, and Wake-on-LAN power-on from an agent or terminal."
  - "Mirror a virtual desktop output to a screen over the network via live HLS."
metadata:
  hermes:
    tags: [displays, dlna, upnp, casting, smart-tv, ssdp, mdns, hls]
    related_skills: []
---

# Remote Displays

Discover LAN screens with SSDP/mDNS, cast files or URLs through DLNA/UPnP
AVTransport, control playback and master volume, wake screens with Wake-on-LAN,
and mirror a whole compositor output (for example a virtual second monitor) to a
screen as a live HLS stream. Everything is Python standard library; the `monitor`
command additionally drives `wf-recorder` and `ffmpeg` when present.
It does not do Miracast/Wi-Fi-Direct (that needs a Wi-Fi Direct radio), and
Miracast-over-Infrastructure (MICE) needs a sink advertising `_display._tcp` plus
a helper such as GNOME Network Displays; AirPlay screen-sending has no practical
Linux sender in this workflow. An mDNS advertisement alone does not prove that a
screen supports DLNA control.

## When to Use

- Find Samsung Tizen, LG webOS, or generic UPnP MediaRenderer screens on the LAN.
- Send a supported media file or reachable media URL to a screen.
- Inspect the current media URI, playback state, position, and duration.
- Pause, stop, seek, adjust volume, or mute a renderer.
- Power on a sleeping screen with a Wake-on-LAN magic packet.
- Mirror a whole compositor output (e.g. a virtual second monitor) to a screen as a
  live stream over the network.
- Check whether a screen advertises MICE before trying an external helper.

Don't use for:

- Low-latency mirroring or gaming streams (HLS segmentation adds seconds of latency).
- Pairing, authentication, or proprietary TV remote buttons.
- Assuming AirPlay or Google Cast discovery implies protocol playback support.

## Prerequisites

- Linux with Python 3.10 or newer; no pip packages are required.
- Computer and screen reachable on the same LAN, without client isolation.
- A DLNA-enabled screen exposing AVTransport for playback and RenderingControl
  for volume; enable media sharing/casting in the screen settings if necessary.
- A readable local media file, or a URL the screen itself can retrieve.
- For `monitor`: `wf-recorder` (Wayland/wlroots capture; override with `--capture`),
  `ffmpeg` on PATH for HLS, and on Hyprland the `hyprctl` helper for `--create-headless`.
  Inbound TCP on the chosen `--port` (default 8124) must be allowed from the screen.
  Video only; audio is not captured.
- For `wake`: Wake-on-LAN enabled in the screen's network settings. Give it an IP
  with a fresh ARP entry or pass its MAC address directly.
- Inbound firewall access for discovery replies and the media server; see Pitfalls.
- Run commands through Hermes `terminal` from this skill's root directory.
- Set `SCREEN_IP` to an address returned by discovery, rather than guessing.
- For local playback, give the terminal sufficient time to cover `--duration`.
  The foreground process must stay alive while the screen fetches the file.

## Quick Reference

- `python3 scripts/remote_display.py --help`
- `python3 scripts/remote_display.py discover --timeout 3 --json`
- `python3 scripts/remote_display.py info "$SCREEN_IP" --timeout 3 --json`
- `python3 scripts/remote_display.py status "$SCREEN_IP" --timeout 3 --json`
- `python3 scripts/remote_display.py play "$SCREEN_IP" ./movie.mp4 --port 8124 --duration 600`
- `python3 scripts/remote_display.py play "$SCREEN_IP" "$MEDIA_URL" --timeout 3`
- `python3 scripts/remote_display.py play "$SCREEN_IP" ./movie.mp4 --advertise-ip "$LAN_IP" --stop-at-end`
- `python3 scripts/remote_display.py pause "$SCREEN_IP" --timeout 3`
- `python3 scripts/remote_display.py stop "$SCREEN_IP" --timeout 3`
- `python3 scripts/remote_display.py volume "$SCREEN_IP" --get`
- `python3 scripts/remote_display.py volume "$SCREEN_IP" --set 30`
- `python3 scripts/remote_display.py volume "$SCREEN_IP" --up`
- `python3 scripts/remote_display.py volume "$SCREEN_IP" --down`
- `python3 scripts/remote_display.py volume "$SCREEN_IP" --mute`
- `python3 scripts/remote_display.py volume "$SCREEN_IP" --unmute`
- `python3 scripts/remote_display.py seek "$SCREEN_IP" 00:10:00`
- `python3 scripts/remote_display.py wake "$SCREEN_MAC_OR_IP"`
- `python3 scripts/remote_display.py monitor "$SCREEN_IP" --output HEADLESS-2 --create-headless`
- `python3 scripts/remote_display.py monitor "$SCREEN_IP" --output HEADLESS-2 --transport hls --segment 1 --list-size 3 --verbose`
- `python3 scripts/remote_display.py monitor "$SCREEN_IP" --output HEADLESS-2 --transport ts --ts-mime video/mpeg --verbose`
- `python3 scripts/remote_display.py mice-scan --timeout 3`

## Procedure

1. Discover candidates using `python3 scripts/remote_display.py discover --json`.
   SSDP searches for MediaRenderer devices and fetches each unique description;
   mDNS queries AirPlay, RAOP, Google Cast, MICE, Samsung, and service enumeration.
   Records with the same A-IP are grouped, retaining their mDNS service details.
   If an advertisement lacks A records, its IP is null; do not invent an address.
   **Complete when:** the intended screen appears with its IP, or discovery
   explicitly reports no screens and exits with code 2.

2. Set `SCREEN_IP` from discovery and run
   `python3 scripts/remote_display.py info "$SCREEN_IP" --json`.
   Inspect name, model, services, and resolved control URLs.
   Samsung fallback probes use port 9197 `/dmr` and port 8001 `/api/v2/`.
   A Tizen API response alone provides identification, not a DLNA control URL.
   **Complete when:** the intended screen is identified and its AVTransport
   service has a control URL, or the absence of that service is recorded.

3. (Optional) Power on a sleeping screen with
   `python3 scripts/remote_display.py wake "$SCREEN_IP"`; it resolves the MAC from
   the kernel ARP table (pass a MAC address directly when there is no ARP entry).
   **Complete when:** the command reports the magic packet destination (the screen
   powers on only if Wake-on-LAN is enabled in its settings).

4. Select media that the screen supports and can reach.
   For local files, choose a server port allowed by the host firewall.
   The script detects the outgoing LAN address through a UDP socket route;
   set `--advertise-ip "$LAN_IP"` when multiple interfaces choose the wrong route.
   For URLs, use HTTP, HTTPS, or RTSP; the script does not download or transcode them.
   **Complete when:** the source exists locally or is reachable from the screen,
   and the chosen local server port is allowed when serving a file.

5. Start casting with
   `python3 scripts/remote_display.py play "$SCREEN_IP" ./movie.mp4 --duration 600`.
   The local HTTP server exposes only the chosen file, supports HEAD and GET
   byte ranges, and advertises its URL before sending SetAVTransportURI and Play.
   Adjust duration to cover playback; default is 600 seconds after Play succeeds
   (must be greater than 0).
   Add `--stop-at-end` to send Stop before the local server closes.
   Direct URL casting starts no server and returns after Play is accepted.
   **Complete when:** the terminal prints the media URL and `Play accepted.`.

6. In another terminal, run
   `python3 scripts/remote_display.py status "$SCREEN_IP" --json` twice,
   a few seconds apart, while the serving process remains alive.
   Compare TransportState, CurrentURI, position, and duration.
   **Complete when:** state is PLAYING and position advances for the selected URI.

7. Use `pause`, `stop`, `seek`, or `volume` as needed.
   Pause and Stop read back playback state; `seek` takes `HH:MM:SS` and reads
   back the position; volume changes read back volume.
   Up/down move by five within 0–100; mute/unmute read back CurrentMute.
   **Complete when:** the displayed readback matches the requested change.

8. If desktop sharing is required, run
   `python3 scripts/remote_display.py mice-scan`.
   This only discovers `_display._tcp.local` PTR/SRV/TXT/A records.
   If a sink appears, the script suggests `gnome-network-displays`; configure
   that helper separately and open the firewall required by the helper/sink.
   **Complete when:** a sink's name, target, port, and TXT appear, or the output
   clearly says no MICE sinks were found.

9. To mirror a whole screen output to the screen as a live stream, run
   `python3 scripts/remote_display.py monitor "$SCREEN_IP" --output HEADLESS-2 --create-headless`.
   The default is tuned HLS: 1 s segments and a 3-segment playlist.
   `--transport ts` bypasses ffmpeg and serves progressive MPEG-TS at `/live.ts`;
   use `--ts-mime video/mp2t` if the renderer needs that MIME type.
   It captures the output with wf-recorder, serves the stream on `--port` to the
   target screen only, and casts with the DIDL metadata strict renderers require.
   Ctrl+C stops the screen and closes the pipeline; a headless output created by
   the run is removed on exit unless `--keep-headless` is passed.
   **Complete when:** `status` shows `PLAYING` on the `live.m3u8` URL and fetch
   activity continues while the command runs.

## Pitfalls

- Inbound firewall rules must allow TCP on the selected media server port
  (default 8124) from the screen, UDP 5353 for mDNS, and SSDP reply traffic
  arriving from UDP source port 1900 to the search socket's ephemeral port.
  Opening only inbound destination port 1900 does not cover those replies.
- On NixOS, arrange the relevant allowed TCP/UDP ports or a scoped rule for
  SSDP replies; this script never modifies firewall configuration.
- Multicast discovery may fail across routed subnets, VPNs, guest Wi-Fi,
  VLAN boundaries, or wireless client isolation despite unicast reachability.
- mDNS binds UDP 5353 with address reuse; if the local responder prevents
  binding or joining the group, discovery warns and still attempts SSDP.
- A larger `--timeout` gives replies more time. Each network operation has
  its own wait; discover performs one SSDP pass then one raw mDNS pass.
  Description fetches are capped at two seconds each.
- Some TVs only accept `video/mp4`; the server chooses Content-Type from the
  extension and does not inspect or convert codecs.
- TVs sometimes require H.264 video plus AAC audio inside an MP4 container.
  Renaming an incompatible file to `.mp4` does not convert it.
- DLNA is not mirroring. It fetches a static file/URL and exposes playback control.
- Classic Miracast needs Wi-Fi Direct hardware and a separate sender stack.
  MICE needs `_display._tcp` advertising, GNOME Network Displays or another
  helper, and appropriate firewall access; most TVs do not advertise MICE.
- `monitor` defaults to tuned HLS (1 s target, 3-segment playlist), because
  Samsung UN65TU7000-series sets disconnected progressive TS with both
  `video/mpeg` and `video/mp2t`. Expect roughly 3–4 s of structural HLS delay;
  absolute display latency requires visual measurement. `--segment 0.5` still
  yields ~1 s segments with the fixed 30-frame GOP at 30 fps. Measured on a
  wired TU7000: first video ≈4 s after Play with these defaults.
- Progressive TS supports only one GET viewer; another GET receives HTTP 409.
  HEAD probes do not consume the viewer slot. It skips ffmpeg and segmentation,
  but renderer buffering and compatibility vary. Do not select it just because
  SOAP Play succeeds: require PLAYING plus sustained byte flow for at least 60 s.
- `--verbose` logs request timing, TS byte counters, HLS bytes and publication
  timestamps. Playlist and stream responses use `no-store`; live reads are at
  most 64 KiB. The stream is video-only; HLS requires wf-recorder plus ffmpeg.
- `wake` requires Wake-on-LAN enabled on the screen; without a fresh ARP entry
  pass the MAC address. The magic packet goes to the broadcast address and,
  when known, the IP.
- Some renderers reject `Seek`; expect an error when the service lacks support.
- The HLS server serves only the playlist and its segments (fixed name whitelist);
  nothing else in the directory is exposed.
- AirPlay/RAOP/Google Cast/Samsung mDNS records are discovery hints only.
  This script implements UPnP SOAP control, not those proprietary protocols.
- The local servers are unauthenticated and bind to the advertised LAN address;
  `play` and `monitor` additionally serve only the target screen's IP by default
  (other hosts receive HTTP 403; override deliberately with `--allow-any-client`).
  Keep them on a trusted network.
- `monitor` streams the captured desktop output to the screen while it runs:
  treat it as sensitive screen content and stop the command when done. A
  headless output created by that run is removed on exit unless `--keep-headless`
  is passed.
- A server URL is useful only while the casting process is alive.
  When duration expires, later seeking or fetching may fail unless Stop was sent.
- `--stop-at-end` applies to locally served files. Direct URL playback has
  no local lifetime timer; use the separate `stop` command when needed.
- Single byte ranges, including suffix ranges, are supported. Multiple ranges
  and unsatisfiable ranges receive HTTP 416.
- Renderers without RenderingControl cannot provide volume operations.
  Some vendor APIs offer identification without an AVTransport service.
- Errors are concise and go to stderr; JSON success data goes to stdout.
  Exit 0 means success, 2 means not-found/timeout, and 1 means another error.
  Argparse also uses 2 for invalid command syntax.

## Verification

Use `python3 scripts/remote_display.py status "$SCREEN_IP" --json` twice
with a few seconds between reads. Confirm TransportState is `PLAYING`,
CurrentURI matches the printed media URL, and position advances.
A successful SOAP Play response alone is insufficient proof of visible playback.
Check the screen itself for the expected picture/audio and verify pause,
stop, seek, volume, and mute through their readback and the screen's behavior.
For `monitor`, repeat the two-read check against the `live.m3u8` URL: the screen
keeps fetching the playlist and new segments while the pipeline runs (visible with
`ss -tn`). For `wake`, success is the printed destination plus the screen powering on.

For offline implementation checks, run:

```sh
python3 -m py_compile scripts/remote_display.py
python3 -m unittest discover -s scripts/tests -v
```

These checks use synthetic fixtures and mocks plus a local HTTP test server;
they do not discover or control a real screen.

## Extensions

See `references/extensions.md` for possible extensions and provenance: the verified
desktop-streaming recipe used by `monitor`, vendor app launching, subtitle
side-loading, transcoding, and event subscriptions.
