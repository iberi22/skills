# Hyprland 0.55 Version Migration — Opciones Deprecadas y Reemplazos

Este archivo documenta los cambios entre Hyprland < 0.55 y >= 0.55 encontrados en sesiones de debugging reales.

## Opciones Eliminadas vs Renombradas

| Sección | Opción antigua | Estado | Reemplazo |
|---------|---------------|--------|-----------|
| `general` | `cursor_inactive_timeout` | 🟡 Movido | `cursor { inactive_timeout = N; }` |
| `decoration` | `drop_shadow` | 🔴 Eliminado | `shadow { enabled = true/false; }` |
| `decoration` | `shadow_range` | 🔴 Eliminado | `shadow { range = N; }` |
| `decoration` | `shadow_render_power` | 🔴 Eliminado | `shadow { render_power = N; }` |
| `decoration` | `col.shadow` | 🔴 Eliminado | `shadow { color = rgba(...); }` |
| `misc` | `vfr` | 🔴 Eliminado | Quitar — ya no existe |
| `misc` | `render_ahead_of_time` | 🔴 Eliminado | Quitar |
| `misc` | `no_direct_scanout` | 🔴 Eliminado | Quitar |
| `misc` | `vrr` | ✅ Válido | `misc { vrr = 1; }` |
| `misc` | `focus_on_activate` | ✅ Válido | Sin cambios |
| `misc` | `enable_swallow` | ✅ Válido | Sin cambios |

## Dispatcher `togglesplit`

- **Estado**: Eliminado como dispatcher directo
- **Dwindle layout**: `layoutmsg, togglesplit` (funciona)
- **Master layout**: `layoutmsg, togglesplit` → **NO funciona**, usar `layoutmsg, orientationcycle`

Layoutmsg válidos para master layout:
- `orientationcycle` / `orientationcycle prev` / `orientationcycle next`
- `cyclenext`
- `swapwithmaster`
- `focusmaster`
- `addmaster`
- `mfact 0.5`

## Cómo Detectar en el Log

```bash
# Buscar errores de parseo
grep -E "no such option|does not exist|Invalid dispatcher" \
  /run/user/1000/hypr/*/hyprland.log

# Verificar versión
hyprctl version | grep "Hyprland"
```

## Cómo Probar Cada Opción

```bash
for opt in \
  "general:cursor_inactive_timeout" \
  "decoration:drop_shadow" \
  "decoration:shadow_range" \
  "decoration:col.shadow" \
  "misc:vfr" \
  "misc:render_ahead_of_time" \
  "misc:no_direct_scanout"; do
  echo -n "$opt: "
  hyprctl getoption "$opt" 2>&1 | head -1
done
```

## Ejemplo: Config Antes vs Después

### Antes (Hyprland < 0.55)
```conf
general {
    gaps_in = 4
    gaps_out = 8
    border_size = 2
    cursor_inactive_timeout = 3
}

decoration {
    rounding = 8
    blur { enabled = true size = 6 passes = 2 }
    drop_shadow = true
    shadow_range = 12
    shadow_render_power = 3
    col.shadow = rgba(00aa6640)
}

misc {
    vfr = true
    render_ahead_of_time = false
    no_direct_scanout = false
}
```

### Después (Hyprland >= 0.55)
```conf
cursor {
    inactive_timeout = 3
}

decoration {
    rounding = 8
    blur { enabled = true size = 6 passes = 2 }
    shadow {
        enabled = true
        range = 12
        render_power = 3
        color = rgba(00aa6640)
    }
}

misc {
    # vfr, render_ahead_of_time, no_direct_scanout removidos
}
```

## Interpretación del Error Overlay

El overlay de Hyprland muestra errores individuales. Si ves mensajes como:
```
<general:cursor_inactive_timeout> does not exist
<decoration:drop_shadow> does not exist
(26 more...)
```

Eso significa que CADA opción deprecada genera su propio error. 7 opciones deprecadas ≈ 7+ errores en el overlay. El conteo puede ser mayor si Hyprland reporta múltiples errores por línea malformada.

**Una vez corregido y recargado** (`hyprctl reload`), el overlay se reinicia. Si persiste visualmente, es de la sesión anterior — cerrar sesión o reiniciar Hyprland lo elimina completamente.
