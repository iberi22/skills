---
name: garage3d-webgpu-engine
description: Build or change the GARA-G 3D garage engine (three.js r186 WebGPURenderer + TSL, WebGL2 fallback) at a steady 60 fps on mid-range phones. Use when touching packages/app-pwa/src/garage/engine/, the garage scene, camera, part picking, health/x-ray view modes, adaptive quality, or the Svelte/Astro mounting of the canvas.
---

# Garage 3D engine (WebGPU, 60 fps)

The engine is a facade (`GarageEngineApi` in `src/garage/contracts.ts`). The UI talks only to
that interface; nothing outside `src/garage/engine/` imports `three` except templates and the lab.

## Stack facts (verified on three 0.186.1)

- `import { WebGPURenderer, MeshPhysicalNodeMaterial, PMREMGenerator, ... } from 'three/webgpu'`
  and TSL from `'three/tsl'`. Addons: `three/addons/controls/OrbitControls.js`,
  `three/addons/environments/RoomEnvironment.js`, `three/addons/tsl/display/OutlineNode.js`,
  `three/addons/tsl/display/BloomNode.js`.
- `new WebGPURenderer({ canvas, antialias: true })` picks WebGPU and falls back to WebGL2 by
  itself; `forceWebGL: true` forces the fallback (use it for `?gl=1`). **`await renderer.init()`
  before the first render** (r186 throws on an uninitialized renderer).
- Backend: `(renderer.backend as any).isWebGPUBackend ? 'webgpu' : 'webgl2'`.
- Stats: `renderer.info.render.drawCalls`, `renderer.info.render.triangles`.
- Headless Chromium in this repo **does** get WebGPU (verified: lab reports `backend: "webgpu"`).
- Post-processing: `new RenderPipeline(renderer)` (r186 name; `PostProcessing` is the old alias)
  with `pass(scene, camera)` nodes. Only on the `high` tier.

## Frame budget (60 fps = 16.7 ms; mid-range Android ≈ Adreno 610 / Mali-G57)

| Item | Budget |
|---|---|
| Scene draw calls | ≤ 120 (`RENDER_BUDGET.sceneDrawCalls`) |
| Vehicle triangles | ≤ 90k high / ≤ 35k low LOD |
| Pixel ratio | start `min(dpr, 1.5)` on touch devices, `min(dpr, 2)` desktop; governor may drop to 1.0 |
| Shadows | one directional shadow map, 1024 (medium) / 2048 (high), **off on low** (use the blob contact shadow) |
| Shadow updates | `light.shadow.autoUpdate = false`; set `needsUpdate = true` only when the vehicle or its pose changes |
| Environment | PMREM from `RoomEnvironment` once, sigma 0.04; never regenerate per frame |
| Post | none on low/medium; on high at most outline (selection) + light bloom on emissive strips |
| Materials | from the shared kit only (`templates/common/materials.ts`); each new material = a new pipeline compile |

## Rules

1. **Render on demand.** Run `setAnimationLoop` while something moves (controls damping, camera
   tween, carousel transition, pulsing overdue part); after ~1.5 s with no change, stop the loop
   and re-arm it on input/resize/state change. Idle garages must not burn battery.
2. **Adaptive quality governor**: exponential moving average of frame time; if EMA > 18.5 ms for
   ~45 frames step down (dpr → shadows → tier), if < 12 ms for ~120 frames step up. Hysteresis
   both ways, never oscillate faster than every 2 s. Expose the tier in `getStats()`.
3. **Disposal is mandatory.** On vehicle switch dispose geometries of the outgoing vehicle (the
   material kit is shared and survives); on `dispose()` free everything: renderer, PMREM target,
   controls, listeners, ResizeObserver. Svelte remounts the page on SPA navigation (Astro
   ClientRouter): leaks show up as GPU memory growth after 5 navigations.
4. **Picking** with a single `Raycaster` against the vehicle root only; read `object.userData.slotId`
   walking up parents. Ignore drags (pointerdown→pointerup moved > 6 px). Hover highlight only on
   devices with `matchMedia('(hover: hover)')`.
5. **View modes**
   - `beauty`: original materials; slots marked `internal` in `src/garage/parts.ts` hidden.
   - `health`: every part gets one of 5 shared status materials (ok/warn/critical/overdue/unknown);
     keep the original in `mesh.userData.baseMaterial` and restore it. `overdue` pulses
     (TSL `sin(time)` on emissive) – this is the only thing allowed to keep the loop alive.
   - `xray`: body panels (`category: 'carroceria'`) switch to one shared translucent fresnel
     material (TSL: `normalView`/`positionView` dot → alpha), internals become visible.
6. **Carousel transition** for `showVehicle(spec, { direction })`: outgoing slides/rotates out on
   the turntable while the incoming one slides in (≈450 ms, ease-in-out). Build the incoming model
   *before* starting the animation so the build cost is not inside the transition. Respect
   `prefers-reduced-motion` (cut instead of slide).
7. **Camera**: `OrbitControls` with damping, polar angle clamped (no going under the floor),
   distance clamped to the vehicle size. `focusPart(slot)` tweens target and distance to the
   template's `focusPoints[slot]` (fallback: bounding-box center of the part). Double-tap/`null`
   resets.
8. **Never block the main thread > 50 ms**: building a template is ~5–30 ms; precompile with
   `await renderer.compileAsync(scene, camera)` after adding a new vehicle when available.
9. **SSR safety**: the engine module must only be imported in the browser (dynamic `import()` from
   `onMount`, component rendered with `client:only="svelte"`). Contracts/parts are SSR-safe.

## Garage scene look ("game" garage, not a CAD viewer)

Dark-to-mid neutral room: polished concrete floor (roughness ~0.35 with subtle noise), a raised
circular turntable with a thin emissive rim, two or three emissive light strips on the back wall
(they also read well with bloom on high tier), a soft key light + hemisphere fill. The vehicle
must read clearly against the background in both light and dark UI themes — test with the lab
backgrounds `#dfe3e8` and `#0e1116`.

> **Dev server en paralelo (obligatorio):** Astro 7 detecta que lo corre un agente y fuerza UN servidor de fondo
> global por usuario: `pnpm astro dev` en tu worktree puede quedar conectado al servidor de OTRO agente, y
> `astro dev stop` o `--force` apagan el de otro. Arranca el tuyo aislado y en primer plano:
> `ASTRO_DEV_BACKGROUND=0 npx astro dev --port <puerto-unico> --host 127.0.0.1 --ignore-lock & echo $! > /tmp/<tu-id>.pid`
> y paralo solo con `kill $(cat /tmp/<tu-id>.pid)`. PROHIBIDO `pkill`/`killall`/`astro dev stop`/`--force`.

## Verify (all three, every change)

```bash
# 1. types (scoped)
cd packages/app-pwa && npx tsc --noEmit -p tsconfig.json 2>&1 | grep src/garage
# 2. unit tests of the island
npx vitest run src/garage
# 3. real render: dev server + screenshot, then LOOK at the png
ASTRO_DEV_BACKGROUND=0 npx astro dev --port <port> --host 127.0.0.1 --ignore-lock &   # ver nota
node scripts/garage-shot.mjs --base http://127.0.0.1:<port> --path /fleet/garage --out /tmp/g.png
```
Reading the PNG is part of the job: "tests green" says nothing about whether the scene looks right.
Report backend, fps sample, draw calls and triangles from `window.__garage.stats` in your REPORT.
