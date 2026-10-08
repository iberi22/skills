# Troubleshooting `computer_use`

Read when a short failure entry in SKILL.md is not enough.

| Symptom | Likely cause | Remedy |
|---|---|---|
| `cua-driver not installed` | Driver binary missing | `hermes computer-use install`, or `hermes tools` → enable Computer Use. Override the binary path with `HERMES_CUA_DRIVER_CMD`. |
| Captures empty, "no on-screen window" | Linux: `DISPLAY` unset (X11) or pure Wayland. Windows: Session 0 (SSH) instead of the interactive desktop. | Ask the user to run `hermes computer-use doctor`. For Windows Session 0, see the driver's `WINDOWS.md` (see `driver-platforms.md`). |
| `code: stale` / "element_token is stale" | Index belongs to an older snapshot | Re-`capture`, read the new indices, then act. Never reuse an index across captures. |
| "bare element_index is not accepted" / `snapshot_id_required` | Index sent without its token. A wrapper defect; there is no `snapshot_id` argument in Hermes. | Re-capture once. If it repeats, ask the user to run `hermes update`. Meanwhile use `coordinate=[x, y]` from the capture's bounds. |
| "no reviewed risk classification" / `Unknown tool` | Driver MCP vocabulary was called directly | Use only `computer_use(action=...)` from SKILL.md. |
| Click had no effect | Verdict not read, or wrong rung | Read `effect`. `unverifiable` → fresh capture first. `suspected_noop` or a refusal → coordinate, then foreground. |
| Typed text disappears into a terminal emulator | Terminal detection failed on an older driver | Ask the user to run `hermes computer-use doctor`. Recent drivers route terminals (Ghostty, iTerm2, Terminal.app, Windows Terminal, mintty, etc.) through key-event synthesis. |
| `blocked pattern in type text` | Shell command matches the dangerous-pattern list | Split the command or reconsider it. |
| Windows: `doctor` says "could not be started … Access is denied" | Hermes venv cannot execute a binary under `C:\Program Files\WindowsApps` | Reinstall the driver with the upstream installer (installs under the user profile), or set `HERMES_CUA_DRIVER_CMD` to a copy outside `WindowsApps`. The same denial repeats in `errors.log` for other `WindowsApps` binaries. |
| Anything else | Unknown | Ask the user to run `hermes computer-use doctor`. It runs the driver's `health_report` and prints a per-check matrix. |
