---
name: swal-theme-creator
description: "Allows AI agents (Hermes, Antigravity, Jules) to generate, validate, and switch visual themes in SWAL Desktop using declarative JSON tokens."
version: 1.0.0
tags: [swal, theme, desktop, eww, hyprland, styling]
---

# SWAL Theme Creator & Manager Skill

This skill enables agents to customize the visual appearance of the SWAL Desktop environment by generating or editing JSON theme definitions.

## Location of Themes
All themes are stored in `~/.config/swal/themes/<theme_id>.json`.

## Theme Structure (`~/.config/swal/schemas/theme.schema.json`)

```json
{
  "id": "theme-name",
  "name": "Human Readable Theme Name",
  "author": "Hermes Agent",
  "version": "1.0.0",
  "colors": {
    "bg": "rgba(2, 6, 23, 0.97)",
    "elevated": "rgba(15, 23, 42, 0.85)",
    "elevated_850": "rgba(21, 30, 46, 0.90)",
    "void": "#000000",
    "accent_primary": "#06b6d4",
    "accent_secondary": "#f97316",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "border_active": "rgba(6, 182, 212, 0.40)",
    "border_subtle": "rgba(255, 255, 255, 0.08)"
  },
  "hyprland": {
    "active_border": "rgba(06b6d4ff) rgba(f97316ff) 45deg",
    "inactive_border": "rgba(0f172aff)"
  }
}
```

## CLI Commands for Agents

- **List themes**: `swal-theme list`
- **Show current theme**: `swal-theme current`
- **Switch theme**: `swal-theme switch <theme_id>`
- **Create new theme**: `swal-theme create <theme_id> --base hive-dark`

## Guidelines for Agents
1. Always maintain strong contrast between `bg` and `text_primary`.
2. Keep `border_subtle` slightly translucent (`rgba(..., 0.07)`).
3. After creating a new theme file in `~/.config/swal/themes/<id>.json`, run `swal-theme switch <id>` to apply it in real time.
