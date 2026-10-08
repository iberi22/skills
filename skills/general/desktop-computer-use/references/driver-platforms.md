# Driver platform deep-dives

The driver (cua-driver) ships a skill pack with platform detail. It documents the
driver's own MCP tools (`get_window_state`, `element_token`, `snapshot_id`, …).
Read it for platform context only. Keep calling the `computer_use` actions in
SKILL.md; the wrapper translates them.

## Install the pack

```
cua-driver skills install
```

This links the pack into the Hermes skills directory. `cua-driver skills status`
shows the link state. Requires the driver binary; not available until
`hermes computer-use install` has run.

## Files in the pack

- `SKILL.md`: cross-platform core (snapshot invariant, no-foreground contract,
  click dispatch, AX tree mechanics).
- `MACOS.md`: no-foreground contract, AXMenuBar navigation, SkyLight click
  dispatch, Apple Events JavaScript bridge.
- `WINDOWS.md`: UIA tree, UWP / ApplicationFrameHost hosting, Session 0
  isolation, autostart pattern for SSH.
- `LINUX.md`: AT-SPI tree, X11 / Wayland, terminal emulator detection.
- `RECORDING.md`: trajectory and video recording semantics.
- `WEB_APPS.md`: browser page interaction tips (page content belongs to the
  `browser_*` tools, not `computer_use`).
- `TESTS.md`: replay-by-trajectory workflow.

Note: the pack's file list was not verified in this audit (driver not installed).
