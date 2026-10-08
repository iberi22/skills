# Análisis Programático de Screenshots (sin modelo de visión)

Cuando no hay modelo de visión disponible (vision_analyze falla, delegate_task con vision falla con HTTP 404), usa estas técnicas para diagnosticar visualmente sin ver la imagen.

## 1. Medir ventanas vía Hyprland IPC

```bash
# Todas las ventanas con posición y tamaño
hyprctl clients -j | python3 -c "
import json, sys
data = json.load(sys.stdin)
for c in data:
    sz = c.get('size', [0,0])
    at = c.get('at', [0,0])
    cls = c.get('class','')
    print(f'{cls}: {sz[0]}x{sz[1]} @ ({at[0]},{at[1]})')
"
```

**Limitación**: Layer-shell surfaces (EWW `:wm-type "dock"`) NO aparecen en `hyprctl clients`. Para EWW, usa:

```bash
# Verificar ventanas activas de EWW
eww list-windows
# Verificar todas las variables de estado (incluye dimensiones implícitas)
eww state
```

## 2. Leer dimensiones de imagen PNG (Python stdlib)

```python
import struct

def get_png_size(path):
    with open(path, 'rb') as f:
        sig = f.read(8)
        if sig != b'\x89PNG\r\n\x1a\n':
            raise ValueError("Not a valid PNG")
        f.read(4)  # chunk length
        f.read(4)  # chunk type (IHDR)
        width = struct.unpack(">I", f.read(4))[0]
        height = struct.unpack(">I", f.read(4))[0]
        return width, height

print(f"Screenshot: {w}x{h}")
```

**Limitación**: Solo dimensiones — no puede analizar contenido visual ni detectar overflow.

## 3. Inspeccionar jerarquía de widgets EWW

```bash
# Mostrar estructura de widgets con dimensiones
eww debug | grep -E "VarName|width|min_width|max_width" | head -30
```

## 4. Verificar constraints de ancho en código fuente

```bash
# Buscar todas las constraints de ancho
grep -rn "width\|max-width\|min-width" ~/.config/eww/
# Verificar window geometry
grep -A3 "defwindow" ~/.config/eww/eww.yuck
# Verificar propiedades CSS inválidas
grep -n "max-width\|max-height\|overflow\|transition\|transform\|box-shadow" ~/.config/eww/eww.scss
```

## 5. Cuándo pedir confirmación al usuario

Si después de todo el análisis programático no puedes confirmar visualmente:

1. **Describe los cambios exactos que hiciste** (con diff si es posible):
   ```bash
   diff -u eww.yuck.bak eww.yuck
   ```
2. **Adjunta la ruta del screenshot**: `MEDIA:/tmp/screenshot.png`
3. **Pregunta específicamente**: "¿Sigue desbordado o se ve correcto?"

## Herramientas faltantes (instalar si es necesario)

- **ImageMagick**: `nix-shell -p imagemagick` → `identify`, `convert`
- **PIL/Pillow**: `nix-shell -p python3Packages.pillow` → lectura de píxeles
- **slurp**: `nix-shell -p slurp` → selección de región para grim
