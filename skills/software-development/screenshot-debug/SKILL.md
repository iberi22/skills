---
name: screenshot-debug
description: "Debug errores visibles en pantalla tomando un screenshot completo y analizándolo con un modelo de visión (Qwen3.6-Plus via OpenCode Go)."
version: 1.0.0
author: Hermes Agent
tags: [debug, screenshot, vision, grim, hyprland, wayland, opencode-go]
---

# Screenshot Debug — Depuración Visual con OpenCode Go

Usa este skill cuando el usuario reporte errores visibles en pantalla — overlays de Hyprland, ventanas de error, notificaciones, waybar con errores, etc. Toma un screenshot completo y analízalo con el modelo **Qwen3.6-Plus** (visión) a través de OpenCode Go.

## Requisitos

- `grim` instalado (para capturar pantalla en Wayland)
- `slurp` instalado (para seleccionar región, opcional)
- WAYLAND_DISPLAY accesible (usar `WAYLAND_DISPLAY=wayland-1` si no está en PATH)

## Paso 0: Verificar disponibilidad de modelo con visión

ANTES de tomar screenshot, verifica si el modelo activo soporta imágenes. El modelo se lista en el primer mensaje del turno (`Model: <name>`). Si NO soporta visión:

- `delegate_task` con `toolsets=["vision"]` puede funcionar si existe otro modelo con visión configurado
- **Si delegate_task también falla** (ej. HTTP 404 desde OpenCode Go), NO hay modelo de visión disponible
- SALTA inmediatamente al análisis programático (Paso 3 → Opción C) en lugar de intentar ver el screenshot

## Procedimiento

### Paso 1: Tomar Screenshot

Siempre con las variables de entorno correctas para Wayland (el agente NO tiene `$WAYLAND_DISPLAY` por defecto):

```bash
WAYLAND_DISPLAY=wayland-1 XDG_RUNTIME_DIR=/run/user/1000 grim /tmp/screenshot_debug.png
```

Verifica que el archivo se creó y su tamaño (generalmente 300-900KB):
```bash
ls -la /tmp/screenshot_debug.png
```

Si el terminal tiene PATH corrupto, usa `execute_code` con `subprocess` en vez de `terminal`.

### Paso 2: Analizar con Visión

Usa `vision_analyze` para examinar la imagen. Enfócate en la **parte superior** de la pantalla — ahí aparecen los overlays de Hyprland:

```
vision_analyze(
  image_url="/tmp/screenshot_debug.png",
  question="Describe TODOS los errores, warnings y notificaciones visibles en la pantalla. Enfócate en la PARTE SUPERIOR (overlays de Hyprland, notificaciones, waybar). ¿Qué mensajes de error específicos ves? ¿Hay una barra roja indicadora? ¿Cuántos errores se muestran?"
)
```

### Paso 3: Si `vision_analyze` falla porque el modelo activo no soporta imágenes

#### Opción A ✅ RECOMENDADA: Usar `delegate_task` con herramientas de visión

Esto funciona porque el subagente puede usar `vision_analyze` con su propio modelo:

```
delegate_task(
  goal="Analiza el screenshot en /tmp/screenshot_debug.png y describe todos los errores visibles en la pantalla. Enfócate en la PARTE SUPERIOR (overlays de Hyprland, notificaciones, errores de barra). Describe coordenadas, texto exacto, colores.",
  context="El screenshot está en /tmp/screenshot_debug.png (ruta absoluta). Tiene aprox 600KB. El sistema es NixOS con Hyprland. Busca específicamente errores de configuración de Hyprland, ventanas de error, notificaciones.",
  toolsets=["vision","file","terminal"]
)
```

**Nota**: El subagente con `toolsets=["vision"]` puede usar `vision_analyze` internamente para examinar la imagen.

#### Opción B: Cambiar modelo temporalmente (requiere modificar ~/.hermes/config.yaml)

No intentes cambiar `~/.hermes/config.yaml` durante la sesión — es frágil y puedes perder la conexión.

#### Opción C ⚠️ Análisis programático sin visión (cuando A y B fallan)

Cuando NO hay ningún modelo de visión disponible (tanto `vision_analyze` como `delegate_task` con toolsets vision fallan):

1. **Determinar geometría de la ventana via IPC** (Hyprland):
   ```bash
   # Para ventanas regulares (xdg-shell)
   hyprctl clients -j | python3 -c "import json,sys; [print(f'Class:{c.get(\"class\")} Size:{c.get(\"size\")} At:{c.get(\"at\")}') for c in json.load(sys.stdin) if 'eww' in c.get('class','').lower() or 'dashboard' in c.get('title','').lower()]"
   
   # Para ventanas layer-shell (EWW dock mode), NO aparecen en hyprctl clients
   # Usar eww directamente:
   eww list-windows
   eww state | grep -E "width|height|geometry"
   ```

2. **Verificar ancho/constraints desde el código fuente**:
   ```bash
   # Buscar width constraints en window geometry
   grep -n "geometry\|:width\|:height" ~/.config/eww/eww.yuck
   
   # Buscar min-width, max-width, width en styles
   grep -n "min-width\|max-width\|width" ~/.config/eww/eww.yuck
   
   # Verificar SCSS por propiedades de overflow
   grep -n "max-width\|max-height\|overflow" ~/.config/eww/eww.scss
   ```

3. **Verificar dimensiones del screenshot** (solo validación básica de archivo):
   ```bash
   # Leer dimensiones PNG sin PIL (Python stdlib)
   python3 -c "import struct; f=open('/tmp/ss.png','rb'); f.seek(16); w=struct.unpack('>I',f.read(4))[0]; h=struct.unpack('>I',f.read(4))[0]; print(f'{w}x{h}')"
   ```

4. **Usar `eww debug` para inspeccionar la jerarquía de widgets**:
   ```bash
   eww debug | grep -E "VarName|width|min_width|max_width" | head -30
   ```

5. **Reportar al usuario que no se pudo obtener análisis visual** y pedir confirmación textual:
   - Describe exactamente qué cambios hiciste
   - Pregunta si el problema persiste
   - Adjunta la ruta del screenshot para que el usuario lo vea manualmente

### Paso 4: Debuggear según lo que se vea

#### Overlay de Hyprland (más común)
El overlay cuenta TODOS los errores de parseo. Acción inmediata:

```bash
# 1. Encontrar la instancia de Hyprland
HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr/)

# 2. Buscar errores de config
grep -i "no such option\|does not exist\|Invalid dispatcher" /run/user/1000/hypr/$HYPRLAND_INSTANCE_SIGNATURE/hyprland.log

# 3. Contar errores reales vs ruido de inicio
echo "ERR (config): $(grep -c 'ERR \]:' /run/user/1000/hypr/$HYPRLAND_INSTANCE_SIGNATURE/hyprland.log)"
echo "ERR (aquamarine/DRM): $(grep -c 'ERR from aquamarine' /run/user/1000/hypr/$HYPRLAND_INSTANCE_SIGNATURE/hyprland.log)"
echo "WARN: $(grep -c 'WARN' /run/user/1000/hypr/$HYPRLAND_INSTANCE_SIGNATURE/hyprland.log)"
```

#### Validar cada opción del config contra Hyprland en ejecución

```bash
for opt in "general:cursor_inactive_timeout" "decoration:drop_shadow" "decoration:shadow_range" "decoration:col.shadow" "misc:vfr" "misc:render_ahead_of_time" "misc:no_direct_scanout"; do
  echo -n "$opt: "
  hyprctl getoption $opt 2>&1 | head -1
done
```

- `"no such option"` = **removida** — buscar reemplazo o eliminar
- Devuelve un valor = **válida**

#### Notificaciones de Dunst
```bash
cat ~/.config/dunst/dunstrc 2>/dev/null
dunstctl history 2>/dev/null | head -20
```

#### EWW Dashboard (SWAL)
```bash
# Reiniciar daemon EWW (si se mató)
pkill -9 eww 2>/dev/null; rm -f /run/user/1000/eww-server_*
WAYLAND_DISPLAY=wayland-1 eww daemon; sleep 1; eww open dashboard

# Verificar estado
eww list-windows
eww state | grep -E "EWW_CPU|cal_widget|time " | head -3
```
**Overflow fix:** window 360px + scroll `:hscroll false` + `:width 360` + inner box `style="width:340px;min-width:340px;"`. NO max-width en GTK3 CSS. `margin:0 6px` removido de cards. `cal_widget` usa Pango markup con `#00FF88`. `deflisten media_info` para Now Playing.

#### Waybar con errores
```bash
journalctl --user -u waybar --no-pager -n 50
```

#### Error de compilación NixOS
```bash
nixos-rebuild dry-build --flake /path/to/flake#hostname 2>&1 | grep -iE "error|fail|trace"
```

Para errores de **opciones deprecadas de Hyprland 0.55.x**, ver `references/hyprland-version-migration.md` (incluye tabla completa de opciones antiguas → reemplazos, comandos de diagnóstico, y ejemplo before/after).

### Paso 5: Verificar y cerrar el ciclo

1. **Aplicar fixes** en el source (swal-desktop/hypr/hyprland.conf)
2. **Rebuild**: `nixos-rebuild switch --flake ...`
3. **Recargar Hyprland**: `hyprctl reload`
4. **Verificar** que no hayan nuevos errores:
   ```bash
   grep -c "ERR \]:" /run/user/1000/hypr/$SIGNATURE/hyprland.log
   # Debe ser 0 para el período post-reload
   ```
5. **Captura post-fix** para confirmar visualmente:
   ```bash
   WAYLAND_DISPLAY=wayland-1 XDG_RUNTIME_DIR=/run/user/1000 grim /tmp/screenshot_after_fix.png
   ```

### Paso 6: Si el overlay persiste después del reload

El Error Overlay de Hyprland se crea al **inicio de la sesión** y NO siempre se destruye con `hyprctl reload`. Si el overlay sigue visible aunque el log esté limpio:
- Decirle al usuario que cierre sesión (`SUPER SHIFT + Q` → logout, o `hyprctl dispatch exit`)
- O agregar `disable_error_popups = true` en `misc {}` para prevenirlo en el futuro

## Pitfalls

- **SIEMPRE verificar visualmente antes de reportar un fix**. Si no hay modelo de visión disponible, NO digas "el problema está resuelto" — en su lugar: (a) ejecuta el Paso 3 → Opción C (análisis programático), (b) espera confirmación textual del usuario. Reportar "✅ arreglado" sin verificación visual causa frustración.
- `grim` falla con "failed to create display" → Necesitas `WAYLAND_DISPLAY=wayland-1` y `XDG_RUNTIME_DIR=/run/user/1000`
- `slurp` para screenshot de región puede fallar si no hay monitor conectado
- `vision_analyze` con modelos text-only va a fallar → Usar `delegate_task` con subagente que tenga modelo de visión
- La API de OpenCode Go requiere API key para acceso directo → Siempre usar las herramientas de Hermes (vision_analyze, delegate_task) en lugar de curl directo
- El screenshot puede ser grande (>500KB) → Reducir resolución o convertir a JPEG si es necesario:
  ```bash
  magick /tmp/screenshot_debug.png -resize 50% /tmp/screenshot_small.jpg
  ```

## Modelos con Visión en OpenCode Go

| Modelo | Tipo | Bueno para |
|--------|------|------------|
| `qwen3.6-plus` | Visión general | Debug de UI, texto en pantalla |
| `mimo-v2-omni` | Multimodal completo | Análisis general |
| `glm-5.1` | Visión | Texto chino/español en pantalla |
