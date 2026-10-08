# Reference details for `computer_use`

Supplements SKILL.md. Action names are the Hermes vocabulary, not the driver's MCP names.

## Capture modes

| `mode` | Returns | Use when |
|---|---|---|
| `som` (default) | Screenshot + indexed element list | Vision models |
| `vision` | Screenshot only | You need pixels; then click with `coordinate=` |
| `ax` | Element list only | Text-only model, or no need to see pixels |

The driver always returns the screenshot and the tree in one call. `mode` only
decides what Hermes hands back. There is no numbered overlay on the image: the
index list is the map. Ground on both and cross-check, because the tree is wrong
on some surfaces.

No vision model: Hermes routes the screenshot through the auxiliary vision model.
Configure it under `auxiliary.vision` in `config.yaml`, or use `mode="ax"` and
drive by element index without a screenshot.

## Drag, scroll, focus

- Drag between elements (preferred): `drag(from_element=3, to_element=17)`.
- Rubber-band selection on empty canvas, by coordinates:
  `drag(from_coordinate=[100, 200], to_coordinate=[400, 500])`.
- Scroll the viewport under an element (most common):
  `scroll(direction="down", amount=5, element=12)`.
- Scroll at a point: `scroll(direction="down", amount=3, coordinate=[500, 400])`.
- `list_apps` returns running apps with bundle IDs or process names, PIDs, and window counts.
- `focus_app` routes input to an app without raising it. Rarely needed: `capture(app=...)`
  targets that app's frontmost window, and every following input action goes there.

## Platform key shortcuts

| Action | macOS | Windows / Linux |
|---|---|---|
| Save | `cmd+s` | `ctrl+s` |
| New tab | `cmd+t` | `ctrl+t` |
| Close tab / window | `cmd+w` | `ctrl+w` |
| Copy / paste | `cmd+c` / `cmd+v` | `ctrl+c` / `ctrl+v` |
| Address bar | `cmd+l` | `ctrl+l` |
| App switcher | `cmd+tab` | `alt+tab` |

When unsure, capture and look for menu hints, or ask the user which shortcut to use.

## Delivering screenshots to the user

When the user is on a messaging platform (Telegram, Discord, etc.) and should see a
screenshot, save it to a durable absolute path and reply with `MEDIA:/absolute/path.png`.
Driver screenshots are PNG or JPEG; the response's mimeType says which. Write the
bytes with `write_file`, or with `base64 -d` in the terminal.

On the CLI, describe what you see. The screenshot stays in conversation context.
