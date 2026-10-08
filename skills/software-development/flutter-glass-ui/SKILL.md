---
name: flutter-glass-ui
description: Use when building glassmorphism UIs in Flutter apps.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms:
- linux
- macos
- windows
- android
- ios
metadata:
  hermes:
    tags:
    - flutter
    - glassmorphism
    - cupertino
    - ui
    - design
    - macos
    related_skills:
    - flutter-development
---

# Flutter Glass UI (Glassmorphism + Apple-style)

## Verdict (verified 2026-09-06, L2 research)

Building iPhone/Mac-inspired glass UIs in Flutter is VIABLE with zero extra
packages. The look is 90% achievable; true iOS-26 Liquid Glass refraction
is NOT (no refraction shader in Flutter core — approximate with gradients
+ inner highlights). Hand-roll the glass card: packages (`glassmorphism`,
`glass_kit`, `glassmorphic_ui_kit`) are thin wrappers over the same
`BackdropFilter` and add dependency weight for nothing.

## When to Use

- Glassmorphic cards, sidebars,一晚 floating panels, control-center style sheets
- iPhone-style apps on any platform (Cupertino widgets, SF-like type)
- macOS-style desktop windows (sidebar + toolbar + inspector)
- Deciding Cupertino vs Material vs `macos_ui` for a new screen

## Glass Card Recipe (copy-paste)

```dart
import 'dart:ui';
import 'package:flutter/material.dart';

class GlassCard extends StatelessWidget {
  final Widget child;
  final double radius;
  final double sigma;
  const GlassCard({
    super.key,
    required this.child,
    this.radius = 20,
    this.sigma = 14,
  });

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return ClipRRect(
      borderRadius: BorderRadius.circular(radius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: sigma, sigmaY: sigma),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(radius),
            // translucent fill: white 8-14% (dark bg) / 40-60% (light bg)
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.white.withValues(alpha: 0.14),
                Colors.white.withValues(alpha: 0.06),
              ],
            ),
            border: Border.all(
              color: Colors.white.withValues(alpha: 0.22),
              width: 1,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.25),
                blurRadius: 24,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}
```

Rules: sigma 10-20 (above 24 looks milky and costs GPU); top highlight
via a 1px inner `Border(top: ...white 30%)` sells the glass edge;
animate OPACITY/position, never sigma per-frame.

## Apple-style Mapping

| Apple pattern | Flutter implementation |
|---|---|
| Frosted nav bar / tab bar | `CupertinoNavigationBar` / `CupertinoTabBar` (built-in blur) |
| Grouped lists, cards | `CupertinoListSection` + GlassCard |
| Action sheets, popovers | `showCupertinoModalPopup` / `CupertinoPopover` |
| Segmented control, switches | `CupertinoSegmentedControl`, `CupertinoSwitch`, `CupertinoSlider` |
| macOS sidebar+toolbar+inspector | `macos_ui` package (`MacosWindow`, `Sidebar`, `ToolBar`) |
| SF font on Linux | NOT available — use Inter (closest metrics) via `google_fonts` or bundled TTF |
| SF Symbols | NOT available — use `cupertino_icons` + custom SVGs |

`macos_ui` renders on Linux too, but its value is macOS fidelity; on
Hyprland/GNOME prefer Cupertino + custom glass (native feel comes from
the compositor, not the widget set).

## Linux Transparency (glass over the real desktop)

1. `window_manager`: `await windowManager.setBackgroundColor(Colors.transparent)`
   (+ `setAsFrameless()` for borderless floating panels).
2. Scaffold background MUST be transparent too (`backgroundColor:
   Colors.transparent`), else the blur samples an opaque canvas.
3. Hyprland bonus: compositor-side blur behind transparent windows via
   `layerrule = blur, <class>` — real desktop glass for free.
4. Verify visually (grim screenshot) — no unit test can assert blur.

## Performance Rules (Impeller/Skia, AMD iGPU class hardware)

- Bound blur regions: small cards, never fullscreen sheets.
- NEVER nest `BackdropFilter` (cost multiplies per layer).
- One shared sigma per screen; reuse the GlassCard widget.
- Animate opacity/offset/scale; animating sigma re-rasterizes every frame.
- Profile on the target GPU (`flutter run --profile` + DevTools shader tab);
  first-run jank = shader compilation, warms up after 1-2 presentations.

## Accessibility

- Text on glass needs contrast: dark scrim (`black 20-35%`) behind labels
  or `MediaQuery.highContrast` fallback to solid surfaces.
- Honor reduced motion: `MediaQuery.disableAnimations` → skip parallax/
  spring entrances, show final state.

## Viability Checklist (run before committing to the style)

1. Target GPU renders 2-3 simultaneous blurred cards at 60fps in profile mode?
2. Transparent window works under the target compositor (Hyprland: yes +
   layerrule blur; GNOME: yes via RGBA visual; tiling WMs may force opaque)?
3. Fonts/icons licensed for the platform (Inter + cupertino_icons on Linux)?
4. Contrast ratios pass on real wallpapers (test 3 light + 3 dark)?
5. No fullscreen blur anywhere in the design?

If any answer is no, scope glass to accents (nav bars, chips, dialogs)
and keep content surfaces solid.

## References

- [Glassmorphism effects in Flutter (Vibe Studio)](https://vibe-studio.ai/insights/implementing-glassmorphism-effects-in-flutter-uis)
- [Glassmorphic UI packages (Flutter Gems)](https://fluttergems.dev/glassmorphic-ui/)
- [macos_ui first app codelab](https://macosui.dev/docs/getting_started/first_app)
- [Cupertino design docs](https://docs.flutter.dev/ui/design/cupertino)
