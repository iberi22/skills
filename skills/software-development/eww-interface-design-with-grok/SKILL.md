---
name: eww-interface-design-with-grok
description: "Redisenar interfaces EWW usando OpenCode CLI con  (diseno) + deepseek-v4-flash-0731 (implementacion). Flujo: captura de pantalla → investigacion web →  critica → deepseek-v4-flash-0731 escribe archivos."
version: 2.0.0
author: Hermes Agent
tags:
  - eww
  - css
  - gtk3
  - opencode
  - qwencloud
  - ui-design
  - hyprland
---

# EWW Interface Design with OpenCode

Flujo completo para rediseñar interfaces EWW usando OpenCode CLI con modelos
QwenCloud Token Plan (provider `opencode-go`).

## Flujo de Trabajo

### Fase 1: Capturar estado actual
```bash
# Tomar screenshot de la ventana EWW actual
WAYLAND_DISPLAY=wayland-1 grim -g "$(slurp -o)" ~/Pictures/eww-panel-actual.png
```

### Fase 2: Investigar tecnicas modernas
```bash
web_search("EWW elkowars widgets modern UI design techniques")
web_search("eww yuck widget beautiful dashboard design examples hyprland")
web_search("gtk3 css eww widget styling tips tricks glassmorphism")
```

Crear prompt con:
1. Contexto del sistema (NixOS, Hyprland, EWW, GTK3 CSS)
2. Limitaciones CRITICAS de GTK3+EWW (NO transform/transition/box-shadow en clases)
3. Contenido actual de los archivos (eww.yuck, eww.scss)
4. Screenshot del estado actual
5. Requerimientos del usuario
6. Formato de respuesta esperado

```bash
cat > /tmp/eww-design-prompt.md << 'EOF'
... prompt completo ...
EOF

opencode run -f /tmp/eww-design-prompt.md --model opencode-go/deepseek-v4-pro 2>/tmp/eww-design-errors.log
```

### Fase 4: deepseek-v4-flash-0731 LOW - Implementacion

```bash
cat > /tmp/eww-impl-prompt.md << 'EOF'
IMPLEMENTA estos cambios directamente en los archivos:
... codigo exacto a escribir ...
EOF

opencode run -f /tmp/eww-impl-prompt.md --model opencode-go/deepseek-v4-flash 2>/tmp/eww-impl-errors.log
```

### Fase 5: Verificacion
```bash
# Verificar Python
python3 -c "import py_compile; py_compile.compile('scripts/mouse_config.py', doraise=True); print('Python OK')"

# Verificar balance de parentesis en YUCK
python3 -c "
with open('eww.yuck') as f: c = f.read()
o, cl = c.count('('), c.count(')')
print(f'Balance: {\"OK\" if o==cl else f\"OFF by {o-cl}\"}')
"

# Verificar caracteres no-ASCII en SCSS (causan error @charset)
python3 -c "
with open('eww.scss') as f: c = f.read()
non_ascii = [(i, repr(ch)) for i, ch in enumerate(c) if ord(ch) > 127]
print(f'Non-ASCII chars: {len(non_ascii)}')
"

# Recargar EWW
WAYLAND_DISPLAY=wayland-1 eww reload

# Probar ventana
WAYLAND_DISPLAY=wayland-1 eww open --toggle <window_name>
```

## Limitaciones CRITICAS de GTK3 CSS en EWW

| Propiedad | Soportada | Alternativa |
|-----------|-----------|-------------|
| `box-shadow` | ❌ NO | Usar `border` con color |
| `transform` | ❌ NO | Usar layout boxes |
| `transition` | ❌ NO | Usar `revealer` widget con `:transition` |
| `opacity` | ❌ NO (clase) | ✅ SI inline `:style` |
| `line-height` | ❌ NO | Usar `padding` vertical |
| `max-width` / `max-height` | ❌ NO | Usar `min-width`/`min-height` |
| `overflow` | ❌ NO | Usar `scroll` widget |
| `animation` / `@keyframes` | ❌ NO | Usar `revealer` con duracion |
| `border-radius` | ✅ SI | Esquinas redondeadas |
| `background` | ✅ SI | Fondos con `rgba()` |
| `border` | ✅ SI | Bordes con colores |
| `padding` / `margin` | ✅ SI | Espaciado |
| `font-size` / `color` | ✅ SI | Tipografia |

## Modelos OpenCode (QwenCloud Token Plan)

| Modelo | Uso | Tools |
|--------|-----|-------|
| `opencode-go/deepseek-v4-pro` | Diseno, critica, analisis, planeacion | ✅ SI (opencode run) |
| `opencode-go/deepseek-v4-flash` | Implementacion, escritura archivos | ✅ SI |
| `opencode-go/deepseek-v4-pro` | Default — trabajo general | ✅ SI |

## Pitfalls

- **Correr desde el repo del dashboard**: `cd` al directorio con eww.yuck/eww.scss antes de `opencode run` para que el agente lea los archivos reales.
- **deepseek-v4-flash-0731 puede timeout en logica compleja**: Dividir en sub-tareas atomicas.
- **Prompts largos con caracteres especiales**: Usar archivo con `-f` en vez de inline.
- **Tareas >300s**: usar `timeout=600` explícito o `background=true` + `notify_on_complete=true`.
- **Siempre verificar que los archivos fueron escritos**: el agente puede reportar "completado" sin escribir nada — `test -f <ruta>` después.
- **`opencode run` es headless**: no mezclar con la TUI interactiva para automatización.
