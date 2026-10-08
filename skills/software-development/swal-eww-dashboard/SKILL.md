---
name: swal-eww-dashboard
description: "SWAL Dashboard EWW — panel flotante derecho con tarjetas de sistema, rings circulares, clima, calendario, media player, toggles y acciones"
version: 1.1.0
author: Hermes Agent
tags: [eww, dashboard, widget, hyprland, swal, gtk3, yuck]
---

# SWAL EWW Dashboard — Panel Flotante Derecho

Arquitectura completa del dashboard EWW para SWAL, inspirado en Noctalia Shell, DankMaterialShell y Celestia Shell.

## 📁 Estructura de Archivos

```
~/.config/eww/
├── eww.yuck           # Layout widgets (ventanas, contenedores, polls)
├── eww.scss           # Estilos GTK3 CSS (solo props válidas)
└── scripts/
    ├── system_stats.py    # JSON: CPU/RAM/Disk para rings
    ├── resource_history.py # Sparklines + raw percentages
    ├── calendar_gen.py    # Calendario en Pango markup
    ├── media_daemon.py    # Playerctl → JSON streaming
    ├── weather.sh         # wttr.in con caché
    ├── toggles.sh         # WiFi/BT/Night/Dark/DND toggle + estado
    ├── sys_info.sh        # Volumen, brillo, sys stat
    ├── task_tree.py       # Árbol de tareas Hermes
    ├── swal_tasks.py      # API para actualizar tareas
    ├── gpu_stats.sh       # GPU temp + VRAM
    ├── netspeed.sh        # Velocidad de red
    ├── osd.sh             # OSD volume/brightness
    └── ai_status_json.sh  # Estado de agents
```

## 📐 Layout (eww.yuck)

### Ventanas
- **dashboard** — 360px x 1020px, anclada top-right, `wm-type dock`
- **osd** — 240px overlay centrado-abajo

### Scroll Content (dentro de dashboard)
1. **Profile** — Avatar (⛈) + nombre + uptime + layout button + KANBAN button
2. **Quick Toggles** — Net, BT, Night, Theme, DND — cada uno con estado activo visual
3. **System Resources** — 3 rings (circular-progress): CPU/RAM/Disk + GPU temp/vram + network
4. **AI Agents** — HRM, COD, GEM badges + task tree
5. **Controls** — Volume slider only
6. **Now Playing** — Cover art (playerctl mpris:artUrl) + title/artist + prev/play-pause/next
7. **Weather** — Icon + temp + desc + feels + humidity
8. **Calendar** — Mes actual con Pango markup (mes actual coloreado)
9. **Clock** — Hora + fecha
10. **System Actions** — Lock, Logout, Hibernate, Reboot, Poweroff con confirmación inline

### Widgets Custom
- `action_btn` — Botón de acción con icono
- `spark_row` — Fila con sparkline (legacy, no usado actualmente)
- `sys_ring` — Circular progress con icono (48x48)
- `agent_badge` — Badge de agente con name + stat

### Variables (47 defpolls/defvars)
- **System Stats**: `EWW_CPU.avg`, `EWW_RAM.used_mem_perc`, `EWW_DISK["/"].used_perc`
- **GPU**: `gpu_temp`, `gpu_vram`
- **Network**: `netspeed`
- **Media**: `media_info.status/title/artist/cover` (deflisten)
- **Calendar**: `cal_widget` (Pango markup)
- **Clock**: `time`, `date`
- **Toggles**: `toggle_net/toggle_bt/...` + `net_active/bt_active/...`
- **Weather**: `weather_icon/temp/desc/feels/humidity`
- **Agents**: `hermes_stat`, `opencode_stat`, `gemini_stat`
- **Tasks**: `task_tree`, `task_count`

## 🎨 Paleta SWAL
```scss
$bg:       #0D1117;      // Fondo oscuro
$card:     rgba(22,27,34,0.92); // Tarjetas semi-transparente
$border:   rgba(48,54,61,0.6);  // Borde sutil
$fg:       #E6EDF3;      // Texto principal
$dim:      #8B949E;      // Texto secundario
$neon:     #00FF88;      // Verde neón SWAL
$cyan:     #00CCFF;      // Cian
$purple:   #BB9AF7;      // Púrpura
$red:      #F85149;      // Rojo error/sistema
$green:    #3FB950;      // Verde OK
```

## ⚠️ GTK3 CSS Reglas
- **NO** usar `max-width`, `max-height`, `overflow`, `transform`, `transition`, `opacity`, `box-shadow` — no son válidos
- **SÍ** usar `min-width`, `min-height`, `padding`, `margin`, `border`, `border-radius`, `font-size`, `color`, `background`
- Inline `:style` en yuck soporta `width`, `min-width` pero NO `max-width` (se ignora)
- Scroll con `hscroll false` + `:width 360` + box interno `width: 340px` para overflow clipping

## ⚠️ CSS errors = windows invisible / no style
When EWW fails to parse the SCSS, windows still "open" (the daemon reports them active) but GTK renders them without any style — they appear transparent, white, or completely invisible. The user sees nothing and thinks the window didn't open, but it's actually there stealing input or blocking interaction.

**Check the daemon log first** (`~/.cache/eww/eww_<hash>.log`) for lines like:
```
error: unknown value for property
    ┌─ eww.scss:861
861 │   font-weight: 850;

error: 'line-height' is not a valid property name
    ┌─ eww.scss:863
863 │   line-height: 1.4;
```

**Common GTK CSS properties that break EWW SCSS parsing:**
- `font-weight: 850` → GTK only accepts standard weights (400, 700, 800). Use `800` max.
- `line-height: 1.4` → **Not a valid GTK3 property at all**. Remove it entirely.
- `width: 48px` / `height: 48px` on most widgets → GTK ignores these. Use `min-width`/`min-height`.
- `display: flex`, `position: absolute`, `z-index`, `overflow`, `box-shadow` → GTK rejects or ignores.

**Recovery when CSS is broken:**
1. Kill the daemon (`pkill -9 -f "eww daemon"`)
2. Remove stale socket (`rm -f /run/user/1000/eww-server_*`)
3. Fix the CSS error in `eww.scss`
4. Restart daemon with correct env:
   ```bash
   export WAYLAND_DISPLAY=wayland-1
   eww daemon
   ```
5. Verify log has **zero** `error:` lines before opening windows
6. Only then open windows: `eww open agent_admin`

**Never** rapid-fire toggle windows when CSS is broken — it corrupts daemon state and you'll get "Tried to close window... but no such window was open" even after fixing the CSS.

## ⚠️ Propiedades de widget en yuck (comunes)
- **NO** usar `:width` ni `:height` como propiedades de widget — EWW las rechaza con error `'width' is not a valid property name`
- **SÍ** usar `:style "min-width: 48px; min-height: 48px;"` dentro del widget
- **NO** usar `:rounded` en `circular-progress` — no es atributo válido. Ignorarlo produce warnings que llenan logs.
- **SÍ** usar `:start-at 75` para rotar el inicio del ring.

## ⚠️ Ventanas overlay / popup sin bloquear input
Si una ventana overlay (`agent_admin`, popup, panel secundario) bloquea teclado y mouse en Hyprland:

1. **Nunca usar** `:focusable true` con `wm-type "dialog"` — captura todo el input del compositor
2. **Configuración correcta para overlay no-focus:**
   ```yuck
   (defwindow agent_admin
     :wm-type "dialog"
     :focusable false
     ;; o para panels tipo dock:
     ;; :wm-type "dock"
     ;; :exclusive false
     ;; :focusable false
   )
   ```
3. **Si el cierre falla** (`eww close agent_admin` no hace nada), usar `eww open --toggle agent_admin` en el botón de cierre — es idempotente y nunca falla silenciosamente.

4. **Panel ancho para datos densos** (Kanban, monitor, tablas): cuando el usuario pide "más ancho, no importa que tape el escritorio", usar `:width "1200px"` o más. El dashboard principal puede quedarse en 360px, pero ventanas secundarias de datos (agent_admin, kanban, monitor) se benefician de 1000px+.
   ```yuck
   (defwindow agent_admin
     :geometry (geometry :width "1200px" :height "95%" :anchor "top right")
     ...)
   ```
   - `:height "95%"` se adapta a la pantalla sin desbordarse.
   - `:anchor "top right"` + `:x "20px"` para pegarla al borde derecho.

5. **Texto truncado en cards**: aumentar `:limit-width` en labels dentro de cards. Default 38 → 55 para aprovechar el ancho extra.
   ```yuck
   (label :text {item.title} :limit-width 55 :show-truncated true)
   ```

6. **SUPER+Tab para panel secundario**: si el usuario quiere que SUPER+Tab abra el panel de datos (agent_admin) en vez del dashboard principal, cambiar el bind en `hypr/hyprland.conf` (source del flake, NO `/etc/config/hyprland.conf` que es read-only en NixOS):
   ```hyprlang
   bind = SUPER, Tab, exec, eww open --toggle agent_admin
   ```
   Luego `sudo nixos-rebuild switch --flake .#swal` para aplicar.

## ⚠️ scss NO-ASCII → error @charset → TODOS los estilos mueren (verificado 2026-08-05)

grass (compilador scss de EWW) auto-inserta `@charset "UTF-8";` cuando el archivo contiene
CUALQUIER byte no-ASCII (comentarios con ──, ·, —, …, iconos). grass NO soporta @charset →
`error: unknown @ rule` en `eww reload` → el scss COMPLETO falla → ventanas SIN estilo
(sin márgenes, transparentes, "no se ve bien") aunque el yuck esté correcto. El daemon log
queda limpio; el error solo aparece en el stderr del reload.

Fix: mantener `eww.scss` 100% ASCII (comentarios en ASCII, sin box-drawing/em-dashes).
PROBADO con experimento aislado: 1 solo char no-ASCII → error @charset; ASCII puro → reload
limpio. Sanear: `python3 -c "s=open('eww.scss',encoding='utf-8').read(); open('eww.scss','w').write(''.join(c if ord(c)<128 else '-' for c in s))"`

## ⚠️ EWW 0.6.0 sizing: hexpand + 3er hijo y min-width inline INFLAN el ancho de ventana

Una ventana con `:geometry :width "620px"` se renderiza MÁS ancha cuando su contenido usa:
1. Fila con 3+ hijos donde uno es hexpand (label o spacer vacío) → suma el ancho expandido
   (~260px en headers; el dashboard sufre +22px por esto sin que se note).
2. Un box hijo con `:style "min-width: Npx;"` inline → suma N al ancho de la ventana.
3. Widget `progress` dentro de un box hexpand → NO infla (usarlo para barras).

Fix verificado:
- Headers: usar `(centerbox :orientation "h" ...)` con 3 hijos (start/center/end) — rinde
  exactamente el ancho de la geometría. NO usar `(box :hexpand true)` como spacer + 3er hijo.
- Barras de progreso: `(progress :value {0-1} :orientation "h")` + CSS
  `.clase progressbar trough/progress { ... }` (el trough transparente, progress con color).
- Labels con `:hexpand true :xalign 0` SOLO dentro de scrolls (allí no inflan, verificado).
- La bisección del ancho: `hyprctl layers | grep gtk-layer-shell` muestra xywh real de la
  ventana EWW (es layer-shell, no aparece en `hyprctl clients`).

## ⚠️ EWW 0.6.0 NO re-renderiza widgets dinámicos con defpoll (verificado 2026-08-05)

La variable defpoll SÍ se actualiza (visible con `eww get <var>` y `eww state`), PERO en
el render solo funcionan:
- ✅ Labels con `:text` + texto plano (reloj, vol_pct, y `{var}` de JSON) — SE actualizan.
- ❌ `(for item in {var} ...)` — no genera filas al actualizar (agente_admin afectado).
- ❌ `(progress :value ...)` — no repinta el fill.
- ❌ `(literal :content {var})` — no re-renderiza.
- ❌ `(label :markup {var})` — no re-renderiza el markup (chat/calendar afectados).
- ❌ `:vexpand true` en un label con muchas líneas — corta el texto a ~9 líneas.

1. Script genera TEXTO PLANO (sin markup) y lo imprime en modo propio:
   `python3 script.py body` → solo el texto multilinea.
2. defpoll independiente: `(defpoll ram_body :interval "3s" :initial "" "python3 ./scripts/script.py body")`
3. Label: `(label :text {ram_body} :wrap true :xalign 0 :yalign 0 :style "...")` — SIN vexpand.
4. Barras de progreso en texto plano: `'█'*n + '░'*(30-n)` (monospace).

## 🆕 Adding a New AI Agent Badge to the Dashboard

When a new AI CLI (e.g., `agy`, `codex`, `claude`) is installed, it must be wired into the dashboard so its status appears in the AGENTS section alongside the existing badges.

### 1. Update status scripts

**`scripts/ai_status.sh`** — Add a `case` arm for the new agent:
```bash
  agy)
    if command -v agy >/dev/null 2>&1; then
      echo "Active"
    else
      echo "Inactive"
    fi
    ;;
```

**`scripts/ai_status_json.sh`** — Extend `get_status`, `get_model`, and the `case` blocks:
```bash
get_status() {
  case "$1" in
    hermes)  pgrep -f "hermes" >/dev/null 2>&1 && echo "Active" || echo "Standby" ;;
    opencode) pgrep -f "opencode" >/dev/null 2>&1 && echo "Active" || echo "Standby" ;;
    gemini)  pgrep -f "gemini" >/dev/null 2>&1 && echo "Active" || echo "Standby" ;;
    agy)     pgrep -f "agy.bin" >/dev/null 2>&1 && echo "Active" || echo "Standby" ;;
    *)       echo "Offline" ;;
  esac
}

get_model() {
  case "$1" in
    hermes)  echo "Hermes-3" ;;
    opencode) echo "DeepSeek-V4" ;;
    gemini)  echo "Gemini 2.5" ;;
    agy)     echo "AGY Pro" ;;
    *)       echo "--" ;;
  esac
}

case "$agent" in
  hermes|opencode|gemini|agy)
    echo "{\"status\":\"$(get_status $agent)\",\"model\":\"$(get_model $agent)\"}"
    ;;
  hermes_stat|opencode_stat|gemini_stat|agy_stat)
    base=${agent%_stat}
    get_status "$base"
    ;;
  hermes_model|opencode_model|gemini_model|agy_model)
    base=${agent%_model}
    get_model "$base"
    ;;
  *)
    echo "{\"status\":\"Offline\",\"model\":\"--\"}"
    ;;
esac
```

### 2. Add badge to `eww.yuck`

In the AGENTS section, insert a new `agent_badge` widget:
```yuck
(box :orientation "h" :space-evenly true :spacing 4
  (agent_badge :name "HRM" :stat hermes_stat :action "eww close && ghostty -e hermes &")
  (agent_badge :name "COD" :stat opencode_stat :action "eww close")
  (agent_badge :name "AGY" :stat agy_stat :action "eww close")
  (agent_badge :name "GEM" :stat gemini_stat :action "eww close"))
```

### 3. Add `defpoll` variable

Near the other agent `defpoll`s:
```yuck
(defpoll agy_stat :interval "10s" "./scripts/ai_status_json.sh agy_stat")
```

### 4. Verify after reload
```bash
cd ~/.config/eww && WAYLAND_DISPLAY=wayland-1 eww reload
# Test:
bash scripts/ai_status_json.sh agy_stat   # → Active
bash scripts/ai_status.sh agy             # → Active
```

### 5. NixOS binary wrapper (if needed)

If the CLI is a generic Linux binary (not packaged in nixpkgs), it may fail with missing `.so` libraries. On NixOS, wrap it with `steam-run` (from `nixpkgs#steam-run`):
```bash
# Create wrapper script
cat > ~/.local/bin/agy << 'EOF'
#!/usr/bin/env bash
exec steam-run "$HOME/.local/bin/agy.bin" "$@"
EOF
chmod +x ~/.local/bin/agy
```
Make sure `~/.local/bin` is in `PATH`.

**See also:** `references/antigravity-agy-integration.md` for AGY-specific auth, token paths, and NixOS wrapper details.

## 🔧 Scripts Clave

### system_stats.py
```
Usage: system_stats.py <cpu|ram|disk>
Output: JSON con campos para dot notation de EWW
  cpu → {"avg": 12.5}
  ram → {"used_mem_perc": 16.1}
  disk → {"/": {"used_perc": 30.5}}
```

### media_daemon.py
Usa `deflisten` (streaming continuo, no polling):
```yuck
(deflisten media_info :initial '{"status":"Stopped","title":"","artist":"","cover":""}'
  "./scripts/media_daemon.py")
```
Accede a campos con `{media_info.title}` en yuck.

### toggles.sh
5 toggles: `network`, `bt`, `nightlight`, `darkmode`, `dnd`
Subcomandos: `icon` (ícono Nerd Font), `active` ("true"/"false")
Toggle buttons usan `{net_active == "true" ? "swal-toggle-btn active" : "swal-toggle-btn"}`
