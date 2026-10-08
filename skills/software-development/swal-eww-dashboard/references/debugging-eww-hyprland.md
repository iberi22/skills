# SWAL EWW Dashboard — Debugging Reference

Session: 2026-05-22 — Panel sin estilo / ventanas invisibles, daemon corrupto

### 9. CSS parse errors → windows open but invisible (no style applied)
**Symptom:** User reports "se quedaron sin style", "no los puedo cerrar", "ventana bloqueada". Windows appear transparent or not visible at all, but daemon reports them as active.

**Root cause in log:**
```
error: unknown value for property
    ┌─ eww.scss:861
861 │   font-weight: 850;

error: 'line-height' is not a valid property name
    ┌─ eww.scss:863
863 │   line-height: 1.4;
```
When SCSS parsing fails, EWW falls back to no styles — windows render as bare GTK containers (often transparent or white).

**Specific invalid properties found:**
| Property | Invalid value | Fix |
|----------|---------------|-----|
| `font-weight` | `850` | Use `800` max (GTK standard) |
| `line-height` | `1.4` | **Remove entirely** — not valid in GTK CSS |

**Critical:** Do NOT rapid-toggle windows while CSS is broken. The daemon's internal window state desynchronizes from the compositor, causing:
- `eww close agent_admin` → "Tried to close window... but no such window was open"
- `eww active-windows` → reports window as open
- `hyprctl clients` → window not listed
- The invisible window may still capture mouse/keyboard events

**Recovery procedure:**
```bash
# 1. Kill everything eww
pkill -9 -f "eww" 2>/dev/null; sleep 2

# 2. Remove stale socket
rm -f /run/user/1000/eww-server_* 2>/dev/null

# 3. Verify/fix CSS before restart
# Check ~/.cache/eww/eww_*.log for "error:" lines, fix eww.scss

# 4. Restart daemon with WAYLAND env
export WAYLAND_DISPLAY=wayland-1
cd ~/.config/eww && eww daemon 2>/tmp/eww.log &
sleep 3

# 5. Verify no CSS errors in fresh log
grep -i "error:" /tmp/eww.log

# 6. Only then open windows
eww open agent_admin
eww open dashboard
```

### 10. WAYLAND_DISPLAY missing → daemon starts but can't render windows
**Symptom:** `eww daemon` starts (process exists), `eww ping` works, but `eww open agent_admin` either does nothing or produces:
```
ERROR eww::error_handling_ctx > Failed to connect to daemon
```
or windows open and immediately close.

**Root cause:** When started from a context without `WAYLAND_DISPLAY` (cron, systemd service, or a terminal session that lost the env var), GTK can't initialize the Wayland backend.

**Diagnóstico:**
```bash
# Check daemon env
cat /proc/$(pgrep -f "eww daemon")/environ | tr '\0' '\n' | grep WAYLAND
# If empty, that's the problem

# Check available Wayland socket
ls /run/user/1000/wayland-*
# Usually: wayland-1
```

**Fix:** Always set `WAYLAND_DISPLAY` before starting daemon:
```bash
export WAYLAND_DISPLAY=wayland-1
eww daemon
```
In NixOS home-manager `exec-once`, use:
```nix
exec-once = "systemctl --user import-environment WAYLAND_DISPLAY && eww daemon";
```
Or in Hyprland config:
```hyprlang
exec-once = dbus-update-activation-environment --systemd WAYLAND_DISPLAY DISPLAY && eww daemon
```

---

## Session: 2026-05-21 — Panel Kanban (`agent_admin`) fixes

## Problem Report
- Panel Kanban (`agent_admin`) bloqueaba teclado y mouse
- SUPER + TAB no funcionaba
- Ventana se desbordaba en altura
- Panel era muy angosto (540px)
- La ventana no cerraba con el botón ✕

## Root Causes & Fixes

### 1. Bloqueo de input (teclado + mouse)
**Causa:** `:focusable true` con `wm-type "dialog"` captura todo el input del compositor Wayland.
**Fix:** Cambiar a `:focusable false`.
```yuck
;; ANTES (bloquea input)
(defwindow agent_admin
  :wm-type "dialog"
  :focusable true)

;; DESPUÉS (no bloquea)
(defwindow agent_admin
  :wm-type "dialog"
  :focusable false)
```

### 2. Ventana no cierra con `eww close`
**Causa:** Cuando hay errores de render en el widget (propiedades inválidas), EWW puede quedar en estado donde `close` no elimina la ventana del compositor aunque `list-windows` la siga reportando.
**Fix:** Usar `eww open --toggle <window>` en vez de `eww close <window>`.
```yuck
;; ANTES (falla silenciosamente)
(button :onclick "eww close agent_admin")

;; DESPUÉS (siempre funciona)
(button :onclick "eww open --toggle agent_admin")
```

### 3. Propiedad `:width` inválida en widget
**Causa:** EWW no acepta `:width` ni `:height` como propiedades de widget.
**Error:** `<data>:2:7'width' is not a valid property name`
**Fix:** Usar `:style` con `min-width` / `min-height`.
```yuck
;; ANTES (error)
(box :width 48 :height 48)

;; DESPUÉS (válido)
(box :style "min-width: 48px; min-height: 48px;")
```

### 4. Atributo `:rounded` inválido en `circular-progress`
**Causa:** `:rounded` no es atributo válido de `circular-progress` en esta versión de EWW.
**Error:** `warning: Unknown attribute rounded`
**Fix:** Eliminar `:rounded true` del widget.
```yuck
;; ANTES
(circular-progress :value value :thickness 6 :rounded true :start-at 75 :class class)

;; DESPUÉS
(circular-progress :value value :thickness 6 :start-at 75 :class class)
```

### 5. Valores vacíos en `circular-progress`
**Causa:** Cuando el poll devuelve string vacía, `:value` no puede parsearse a `f64`.
**Error:** `Failed to turn `` into a value of type f64`
**Fix:** Agregar guard de fallback en el widget.
```yuck
;; ANTES
(circular-progress :value value ...)

;; DESPUÉS
(circular-progress :value {value == "" ? 0 : value} ...)
```

### 6. Valor `null` en indexación de disco
**Causa:** `EWW_DISK["/"]` puede ser `null` si el script no devuelve datos aún.
**Error:** `Unable to index into value null`
**Fix:** EWW no soporta `null` como literal en expresiones. Se recomienda asegurar que el script siempre devuelva JSON válido con default:
```python
# En system_stats.py, asegurar que siempre haya clave "/"
result = {"/": {"used_perc": 0.0}}  # default
```

### 7. Panel angosto para datos densos (Kanban / monitor)
**Causa:** Cards con títulos largos se truncan demasiado en `:width "420px"`. El usuario quiere ver más datos.
**Fix:** Expandir a `:width "1200px"` (o el ancho que pida) y aumentar `:limit-width` de labels.
```yuck
;; ANTES (angosto, truncado)
(defwindow agent_admin
  :geometry (geometry :width "420px" :height "91%" ...))
(label :text {item.title} :limit-width 38)

;; DESPUÉS (ancho, aprovecha espacio)
(defwindow agent_admin
  :geometry (geometry :width "1200px" :height "95%" :anchor "top right" ...))
(label :text {item.title} :limit-width 55)
```
- `:height "95%"` usa porcentaje del monitor — evita desbordamiento en monitores pequeños.
- `:anchor "top right"` + `:x "20px"` la deja pegada al borde derecho.

### 8. SUPER+Tab no levanta panel (daemon caído o binding desactualizado)
**Causa:** Puede ser (a) daemon de EWW sin `WAYLAND_DISPLAY` murió, o (b) el bind en Hyprland apunta a ventana equivocada.
**Diagnóstico:**
```bash
eww ping                          # ¿daemon vivo?
eww active-windows                # ¿qué ventanas están abiertas?
grep "SUPER, Tab" ~/.config/hypr/hyprland.conf   # ¿qué ventana apunta?
```
**Fix (binding):** En NixOS, editar el SOURCE del flake (`~/swal-private/hypr/hyprland.conf`), NO `~/.config/hypr/hyprland.conf` (generado, read-only).
```hyprlang
bind = SUPER, Tab, exec, eww open --toggle agent_admin
```
Luego: `sudo nixos-rebuild switch --flake .#swal`

**Fix (daemon caído):** Si `eww ping` falla, reiniciar con env correcto:
```bash
pkill -9 -f "eww" 2>/dev/null; sleep 2
export DISPLAY=:0; export WAYLAND_DISPLAY=wayland-1
eww daemon
sleep 1; eww open agent_admin
```

## Geometría final del panel Kanban
```yuck
(defwindow agent_admin
  :monitor 0
  :geometry (geometry :x "20px"
                      :y "24px"
                      :width "1200px"
                      :height "95%"
                      :anchor "top right")
  :stacking "overlay"
  :wm-type "dialog"
  :focusable false
  (agent_admin_container))
```

## Debugging EWW en Hyprland

### Logs del daemon
```bash
# Ver logs en vivo (bloquea, usar timeout)
timeout 3 eww logs

# Archivo de logs persistente
~/.cache/eww/eww_<socket_hash>.log
```

### Verificar estado de ventanas
```bash
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-1
eww list-windows
eww ping
```

### Ver ventanas en Hyprland
```bash
export HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr/ | head -1)
hyprctl layers
hyprctl clients
```

### Reinicio limpio del daemon
```bash
pkill -9 -f "eww" 2>/dev/null; sleep 2
rm -f /run/user/1000/eww-server_* 2>/dev/null
export DISPLAY=:0; export WAYLAND_DISPLAY=wayland-1
eww daemon
```

## Environment crítico para daemon
EWW daemon hereda env del proceso que lo inicia. Si se inicia sin `DISPLAY`/`WAYLAND_DISPLAY`, GTK falla.
```bash
# Siempre setear antes de iniciar daemon
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-1
```
