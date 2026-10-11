# Remote Displays — Extensions & Provenance

Beyond the shipped commands (`discover`, `info`, `status`, `play`, `pause`, `stop`,
`seek`, `volume`, `wake`, `monitor`, `mice-scan`), these are the vetted directions
for further capability. They were surveyed against widely used community projects
(credits below) and tested where noted.

## Verified: desktop → TV over LAN (the `monitor` recipe)

The `monitor` command was validated end-to-end against a Samsung TU7000-series
Tizen TV (2020) over wired Ethernet:

1. Create a virtual output (Hyprland: `hyprctl output create headless NAME`), or
   reuse any existing output.
2. Capture it: `wf-recorder -o NAME -D -r 30 -m mpegts -c libx264 -p preset=veryfast
   -p tune=zerolatency -p g=30 -f <fifo>` (a FIFO hands the stream to ffmpeg).
3. Re-segment to live HLS: `ffmpeg -f mpegts -i <fifo> -an -c:v copy -f hls
   -hls_time 1 -hls_list_size 6 -hls_flags delete_segments+omit_endlist+independent_segments`.
4. Serve playlist/segments with MIME `application/x-mpegurl` and `video/mp2t`.
5. Cast with DIDL-Lite metadata whose
   `<res protocolInfo="http-get:*:application/x-mpegurl:*">` matches the served MIME —
   several Samsung models reject the cast ("Illegal MIME-type") when the MIME or the
   metadata is missing.

Findings worth keeping:

- `rtsp://` URIs are rejected by this TV's AVTransport ("Resource not found"); RTSP is
  not a lower-latency option on this model — HLS (~2–6 s latency) is the working path.
- Progressive (`video/mp2t` non-HLS) streaming can freeze on some Samsung models; HLS
  is the safer transport (consistent with community reports — see credits).
- Audio is not captured by `monitor`; capture a PipeWire monitor source alongside the
  video if audio is required.

## Possible extensions (not shipped)

- **Vendor app launching / browser open** — Samsung Tizen REST:
  `http://<ip>:8001/api/v2/applications/<appId>` launches apps (and can open the TV
  browser on a URL). Needs the TV's "Device Connection Manager" permission on first use.
- **Remote key events** via the vendor WebSocket remote API (pairing tokens involved;
  not stdlib-friendly).
- **Subtitle side-loading** — extend the DIDL metadata with caption info and serve
  `.srt/.vtt` next to the media; renderer support varies by model.
- **Transcoding fallback** — when a renderer refuses a file, pre-transcode with ffmpeg
  to H.264/AAC MP4 before casting.
- **UPnP event subscriptions (GENA)** — replace status polling with AVTransport event
  subscriptions (see `async_upnp_client`) for push-style state tracking.
- **Proxy casting** — serve remote URLs through the local HTTP server for screens that
  cannot fetch https or reach the internet directly (dlnap-style proxy).

## Security notes

- The HTTP servers bind to the advertised LAN address and serve only a fixed
  file/name whitelist; keep them on trusted networks.
- SSDP/mDNS discovery trusts LAN advertisements; do not treat discovered descriptions
  as authoritative outside a trusted network (see `evil-ssdp` for the attack class).
- `wake` sends standard magic packets; no credentials involved.

## Credits / inspiration (surveyed 2026-10)

- [fluxcast](https://github.com/IlyaP358/fluxcast) — desktop → TV via WFD/DLNA/Chromecast;
  source of the HLS + `application/x-mpegurl` + DIDL recipe and Samsung TU-series notes.
- [dlna-cast](https://github.com/link89/dlna-cast) — ffmpeg screen capture → HLS → DLNA.
- [dlnap](https://github.com/cherezov/dlnap) — minimal Python DLNA player (proxy pattern).
- [nano-dlna](https://github.com/gabrielmagno/nano-dlna) — minimal UPnP streamer; subtitles.
- [go2tv](https://github.com/alexballas/go2tv) — casting tool (transcoding, subtitles).
- [samsung-tv-ws-api](https://github.com/xchwarze/samsung-tv-ws-api) — Samsung Tizen
  WS/REST control (apps, keys, art mode, Wake-on-LAN).
- [gnome-network-displays](https://github.com/benzea/gnome-network-displays) — Miracast/MICE sender.
- [evil-ssdp](https://github.com/initstring/evil-ssdp) / [upnp_info](https://github.com/tenable/upnp_info)
  — SSDP spoofing and UPnP surface analysis.
