---
name: garage3d-game-hud
description: Build or change the GARA-G garage HUD — the game-style Svelte 5 UI around the 3D vehicle (side indicators, fleet selector arrows, commitments notifier, monitoring strip, bottom dock with parts/history/upcoming/wiki/forum/shop panels), mobile-first PWA and Flutter WebView ready. Use when touching packages/app-pwa/src/components/garage/ or src/pages/fleet/garage/.
---

# Garage HUD (game-style UI over the 3D vehicle)

## Layout

```
DESKTOP (≥ 1024 px)                                   MOBILE (< 768 px, portrait)
┌──────────────────────────────────────────────┐      ┌───────────────────────┐
│ ◉ Garage        2/5  [🔔3]        [view: ◐ ▣ ✚]│      │ ◉ Garage  2/5   [🔔3] │
│┌────────┐                          ┌────────┐ │      │ chips: salud km soat →│ (scroll-x)
││ salud  │                          │consumo │ │      │                       │
││ km     │  ◀    [ 3D VEHICLE ]   ▶  │gasto   │ │      │ ◀   [3D VEHICLE]   ▶  │ 55svh
││ próx.  │                          │alertas │ │      │   Nombre · placa      │
││ docs   │     Nombre · placa · v.  │APK ●   │ │      │ ┌ notifier (3) ─────┐ │
│└────────┘                          └────────┘ │      │ └───────────────────┘ │
│ [compromiso 1] [compromiso 2] [compromiso 3]   │      │ monitoreo strip       │
│ [monitoreo: ● APK en línea · rpm · temp · V]   │      │                       │
│ [Estado][Historial][Próximos][Wiki][Foro][Shop]│      │ dock (6 icons, fixed) │
└──────────────────────────────────────────────┘      └───────────────────────┘
```
Panels open as a right-side drawer (desktop, 420 px) or a bottom sheet with 3 snap points
(mobile: 35 % / 70 % / 95 %) **over** the canvas; the 3D keeps rendering (e.g. "Estado" focuses
the selected part). Only one panel open at a time.

## Behavior

- **Fleet selector**: ◀ ▶ buttons, ←/→ keys, horizontal swipe on the canvas (> 60 px, mostly
  horizontal, not starting on a control). Wraps around. Counter "2/5". Calls
  `engine.showVehicle(spec, { direction })` and updates all panels from `GarageVehicle`.
- **Notifier**: on every vehicle switch (and on first load) slide in a card with the 3 most
  urgent `commitments` (overdue first), auto-dismiss after 6 s unless hovered/focused; the bell
  keeps the count and reopens it. Use `aria-live="polite"`.
- **Indicators**: `vehicle.indicators.left/right` rendered as glass tiles with a ring/bar when
  `progress` exists; tone → color token. On mobile they collapse into a horizontal chip row.
- **Monitoring strip**: shows APK/OBD connection (● en línea / ○ última señal hace X), speed, rpm,
  coolant, battery V, DTC count; polls `GET /api/garage/telemetry/:vin` every 5 s only while the
  tab is visible (`document.visibilityState`), and also listens to `window` event
  `gara:telemetry` (pushed by the Flutter WebView bridge — see `src/garage/telemetry/bridge.ts`).
- **Part selection**: picking a part in 3D opens "Estado" scrolled to that part; selecting a part
  in the list calls `engine.focusPart(slot)`. Contextual sponsored ad (`slot=part_context`)
  appears under a part whose status is warn/critical/overdue — labeled "Patrocinado".

## Visual language

Dark glass HUD over the 3D: `background: color-mix(in oklab, var(--surface) 72%, transparent)`,
`backdrop-filter: blur(14px)`, 1 px hairline borders, 12–16 px radius, numbers in
JetBrains Mono (already in the app via @fontsource), labels in Inter uppercase 11 px with
letter-spacing .12em (the "WAYNE / BATPOD" spec-sheet feel). Accent color = health tone; one
orange highlight color for interactive focus. Respect the app tokens in `src/tokens/` and both
light/dark themes. Motion: 150–250 ms ease-out; `prefers-reduced-motion` → no slides, no pulses.

## Hard requirements

- Svelte 5 runes (`$state`, `$derived`, `$effect`, `$props`) like the rest of `src/components/`.
- The canvas host imports the engine with dynamic `import()` inside `onMount`; the page uses
  `client:only="svelte"`. Nothing from `three` in SSR.
- Text content from users (forum, wiki, ads) is rendered as text (Svelte `{...}`), never `{@html}`.
- Touch targets ≥ 44 px; safe areas with `env(safe-area-inset-*)`; `100svh`, not `100vh`.
- **WebView mode**: `?embed=app` or `navigator.userAgent` containing `GaraGApp` hides the site
  chrome (FleetLayout nav), disables overscroll (`overscroll-behavior: none`) and keeps the dock
  above the Android gesture bar.
- Offline: if `/api/garage/vehicles` fails, use the last snapshot cached in `localStorage`
  (`garage:snapshot:v1`, wrapped in try/catch) and show a small "sin conexión" badge.
- Accessibility: arrows and dock are `<button>`s with labels; panels are `role="dialog"` with
  focus trap and Esc to close; the canvas has an `aria-label` describing the vehicle and its
  overall health; everything shown in 3D (health) is also listed as text in "Estado".
- Expose `window.__garage = { ready: true, vehicleId, stats }` and set
  `document.body.dataset.ready = '1'` after the first vehicle renders (screenshots/e2e rely on it).

> **Dev server en paralelo (obligatorio):** Astro 7 detecta que lo corre un agente y fuerza UN servidor de fondo
> global por usuario: `pnpm astro dev` en tu worktree puede quedar conectado al servidor de OTRO agente, y
> `astro dev stop` o `--force` apagan el de otro. Arranca el tuyo aislado y en primer plano:
> `ASTRO_DEV_BACKGROUND=0 npx astro dev --port <puerto-unico> --host 127.0.0.1 --ignore-lock & echo $! > /tmp/<tu-id>.pid`
> y paralo solo con `kill $(cat /tmp/<tu-id>.pid)`. PROHIBIDO `pkill`/`killall`/`astro dev stop`/`--force`.

## Verify

```bash
cd packages/app-pwa && npx tsc --noEmit -p tsconfig.json 2>&1 | grep -E "components/garage|pages/fleet/garage"
npx vitest run src/garage
ASTRO_DEV_BACKGROUND=0 npx astro dev --port <port> --host 127.0.0.1 --ignore-lock &   # ver nota
node scripts/garage-shot.mjs --base http://127.0.0.1:<port> --path /fleet/garage --out /tmp/hud-desktop.png
node scripts/garage-shot.mjs --base http://127.0.0.1:<port> --path /fleet/garage --mobile --out /tmp/hud-mobile.png
```
Open both PNGs and check layout, overlap, contrast and the notifier before reporting.
