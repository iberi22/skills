# Hermes TUI Rendering Pipeline

## Overview

Hermes has two rendering systems for its terminal UI:

1. **Classic CLI** (default `hermes` command) — prompt_toolkit layout with Rich Console for scrollback output
2. **Ink TUI** (`hermes --tui`) — React/TypeScript via Ink, rendered in alternate screen buffer

This document focuses on the **classic CLI** rendering pipeline, which is where resize-related rendering bugs usually surface.

---

## Classic CLI: Two Render Paths

### 1. Scrollback Rendering (Rich Console → prompt_toolkit)

When the agent prints content to "scrollback" (the conversation history above the prompt), it flows through:

```
your_code → ChatConsole().print() → Rich Console (ANSI) → _cprint() → prompt_toolkit's print_formatted_text(ANSI(...))
```

**ChatConsole** (`cli.py:2274`):
- Wraps a `rich.Console` writing to an in-memory buffer
- At print time, sets `self._inner.width = shutil.get_terminal_size().columns` so Rich wraps content to the current terminal width
- Captures Rich's ANSI output, splits by newlines, sends each line through `_cprint()`

**_cprint** (`cli.py:1754`):
- Routes ANSI text through prompt_toolkit's `print_formatted_text(ANSI(...))`
- Inside the interactive loop, this correctly renders colors and markup
- Uses `_record_output_history()` so content survives full-screen clear / resize replay

**Key pitfall: hardcoded widths are invisible to Rich's auto-width.** If you pass a fixed-width string like `'─' * 40` to `ChatConsole().print()`, Rich doesn't expand it — it just wraps 40 characters at the current terminal width. The fix is to always compute width dynamically:

```python
# BAD: always 40 chars
ChatConsole().print(f"[red]{'─' * 40}[/]")

# GOOD: fills terminal width (with safety floor)
w = self._scrollback_box_width(self._get_tui_terminal_width())
ChatConsole().print(f"[red]{'─' * max(10, w - 2)}[/]")
```

### 2. Live TUI Rendering (prompt_toolkit Layout)

The live prompt area (input, status bar, separator rules) is built from prompt_toolkit `Layout` components in `HermesCLI._build_tui_layout()` (`cli.py:13304`):

```
HSplit layout (top to bottom):
  ──────────────────────────
  sudo/secret/approval/clarify widgets
  model_picker
  spinner_widget
  spacer
  status_bar              ← ConditionalContainer(Window(FormattedTextControl(...)))
  input_rule_top          ← Window(char='─')
  image_bar
  input_area
  input_rule_bot          ← Window(char='─')
  voice_status_bar
  completions_menu
  ──────────────────────────
```

**Status bar** (`_get_status_bar_fragments`, `cli.py:3379`):
- Returns prompt_toolkit `(style, text)` fragments
- Reads width from `_get_tui_terminal_width()` (prompt_toolkit's output object)
- Trims overflow fragments to fit; `wrap_lines=False` on the Window prevents double-line overflow
- Renders pattern: `⚕ model │ ctx used/max │ [░▓▓▓▓░░░░░] % │ duration │ ⏲ elapsed`

**Input rules** (`input_rule_top` / `input_rule_bot`, `cli.py:13236`):
- `Window(char='─')` — prompt_toolkit auto-fills the full container width with `─`
- Height gated by `_tui_input_rule_height()` (1 on normal terminals, 0 on narrow/minimal)
- Suppressed after resize by `_status_bar_suppressed_after_resize` flag (prevents rendering glitches during TUI recovery)

---

## Common Resize-Related Bugs

### 1. Scrollback separators at wrong width

**Symptom:** The `────` line between user messages in scrollback is shorter than the terminal width, or gets progressively "longer" as you resize.

**Root cause:** A hardcoded width like `'─' * 40` in `_print_user_message_preview()`.

**Fix:** Use dynamic width via `_scrollback_box_width()` + `_get_tui_terminal_width()`.

**Why it looks "progressive":** Each call to `_print_user_message_preview()` renders a separator. If you resize between calls, each separator gets a different width from `shutil.get_terminal_size()` at the moment of rendering. The scrollback shows all of them side by side with inconsistent widths.

### 2. Status bar overflows to a second line

**Root cause:** `shutil.get_terminal_size()` returns a stale fallback width (especially on SSH) that differs from prompt_toolkit's actual rendering width. The fragments don't fit the true terminal width and wrap.

**Fix in place:** `_get_status_bar_fragments()` now reads width from prompt_toolkit's output object (`get_app().output.get_size().columns`), and the Window has `wrap_lines=False`.

### 3. Input rule separator doesn't resize

**Unlikely with prompt_toolkit.** `Window(char='─')` with no explicit width auto-fills the parent container, which is the root `HSplit` (always full terminal width). prompt_toolkit re-renders the full layout on every resize event, so width updates automatically.

---

## Tracing Rendering Bugs

### Classic CLI (Python)

1. **Identify which render path:** Is the artifact in scrollback history (above the prompt line) or in the live TUI area (status bar, input rules)?

   - Scrollback → look at `_print_user_message_preview()`, `_stream_delta()`, or any `ChatConsole().print()` / `_cprint()` call
   - Live TUI → look at `_get_status_bar_fragments()`, `_build_tui_layout_children()`, or `Window(char=...)`

2. **Check for hardcoded widths:** Search for `'─' * \d+`, fixed-length `' ' * N`, or `f"..."[:N]"` patterns in rendering functions.

3. **Verify terminal width source:** Is the width coming from `shutil.get_terminal_size()` (can be stale) or prompt_toolkit's `get_app().output.get_size()` (always current)?

4. **Test after resize:** Reproduce with `hermes`, resize terminal, send a message, check separator width in scrollback.

### Ink TUI (TypeScript)

1. **Identify the component:** The TUI layout tree is in `ui-tui/src/components/`. Common entry points:
   - `appLayout.tsx` — `StatusRule` (status bar), `TranscriptPane` (message list), `ComposerPane` (input area)
   - `appChrome.tsx` — `StatusRule` component, `TranscriptScrollbar`, `FaceTicker`
   - `messageLine.tsx` — `MessageLine` component (individual message rendering with `───` separator between turns)

2. **Check `cols` propagation:** The `cols` value originates in `useMainApp.ts` from `stdout?.columns` and flows through `appComposer.cols` → `StatusRule` / `MessageLine`. Verify resize events update the state:
   ```typescript
   // useMainApp.ts:76-98
   const [cols, setCols] = useState(stdout?.columns ?? 80)
   stdout.on('resize', () => setCols(stdout.columns ?? 80))
   ```

3. **Look for hardcoded widths:** Search for literal numbers in JSX `width` props or Text content like `───` that should be dynamic.

---

## References

- `cli.py:2274` — `ChatConsole` class
- `cli.py:1754` — `_cprint()` function
- `cli.py:3192` — `_get_tui_terminal_width()` 
- `cli.py:3206` — `_scrollback_box_width()`
- `cli.py:3379` — `_get_status_bar_fragments()`
- `cli.py:13236` — `input_rule_top` / `input_rule_bot` Windows
- `cli.py:3732` — `_print_user_message_preview()`
- `ui-tui/src/app/useMainApp.ts` — `cols` state and resize handling
- `ui-tui/src/components/appChrome.tsx` — `StatusRule` component
- `ui-tui/src/components/appLayout.tsx` — `TranscriptPane` separator rendering
