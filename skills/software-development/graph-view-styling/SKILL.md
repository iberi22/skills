---
name: graph-view-styling
description: "Use when restyling graph or knowledge-map views (sigma.js)."
---

# Graph view styling (paper & ink) — sigma.js + Astro/Svelte

Lenguaje visual de referencia: **aicodingdictionary.com** = three.js + d3-force, monocromo
(papel + tinta), sin bordes, etiquetas mono con halo, jerarquía por grado. Para grafos de
miles de nodos NO hace falta migrar a 3D: se porta el estilo al motor existente (en GOS:
sigma.js 3 / WebGL con posiciones FA2 precomputadas).

## Paleta (2 tonos)

```css
.wrap          { --g-paper:#eaeae8; --g-ink:#171717; --g-rgb:23,23,23;  --g-edge-a:0.26; }
[data-theme="antigravity"] .wrap { --g-paper:#0b0b0c; --g-ink:#dededa; --g-rgb:222,222,218; --g-edge-a:0.2; }
--g-hair:      color-mix(in srgb, var(--g-ink) 16%, transparent)
--g-hair-soft: color-mix(in srgb, var(--g-ink) 9%,  transparent)
```
JavaScript: `node = rgba(inkRgb, 0.22 + 0.64*imp)` · `label = rgba(inkRgb, 0.52 + 0.38*imp)`
· `edge = rgba(inkRgb, edgeAlpha)` donde `imp = sqrt(degree)/sqrt(maxDegree)` (hubs oscuros y
grandes). Sin color por tipo: los tipos se vuelven **filtros de texto** con conteo. Escala mínima
de alfa ~0.2 en claro y 0.24 en oscuro: por debajo, "polvo invisible" (queja recurrente en review).

## Pitfalls que cuestan horas

1. **`autoRescale: false` ⇒ coordenadas en unidades tipo-píxel.** Sigma expande la extensión al
tamaño del contenedor *en unidades de nodo*; si usas coords [0,1] todo colapsa a un punto central
y solo se ve 1 nodo. Normaliza x∈[0,W·0.95], y∈[0,H·0.95] y cámara en (0.5, 0.5, ratio 1).
2. **Encuadre con aspecto real**: estira el layout para que su aspecto = W/H, recorta outliers con
trim percentil ~1% y **ancla los outliers al borde** (quedan visibles y clicables). Los nodos
ocultos van al centro: no se ven y no deforman la extensión que sigma usa para normalizar.
3. **`<style is:global>` en Astro** cuando el componente crea controles por JS (filtros, resultados,
ficha): el scope de Astro NO alcanza nodos creados en runtime → los controles salen sin estilo
(contraste roto) y parece un bug de diseño.
4. **Overlays se comen el ratón**: una capa superior con `pointer-events:auto` en sus *filas*
bloquea hover/click del canvas en esa franja. Deja `pointer-events:none` en las filas y actívalo
solo en los controles (`search`, `filter-btn`).
5. **Sangrado full-bleed**: `width:100vw` deja el borde cortado por la barra de scroll. Mide la
propia caja y corrige: `wrap.style.width = clientWidth; wrap.style.marginLeft = ml - rect.left`.
Re-aplica en `ResizeObserver`, `load` y `document.fonts.ready`.
6. **Etiquetas legibles**: `defaultDrawNodeLabel` propio con `strokeText` del color del papel
(halo) + **anti-colisión por frame** (lista de cajas, reset en `renderer.on('beforeRender')`).
`labelRenderedSizeThreshold ≈ 5.7`, `labelDensity ~0.75`, `labelGridCellSize ~100`.
7. **Fluidez**: `inertiaDuration 520`, `zoomingRatio 1.35`, `zoomDuration 460`,
`enableCameraRotation:false`, `hideLabelsOnMove:true`. Entrada animada ratio 1.6→1.
8. **Cambio de tema**: `MutationObserver` sobre `data-theme` → re-setea color/lcolor de todos los
nodos y `defaultEdgeColor`, luego `refresh()`.
9. **Hooks de verificación**: expón `window.__geDebug()` (camera, extent, bbox normalizado y
`coverage` = bbox/ventana) para que los e2e midan encuadre sin teoría de matrices.

## Batería de verificación (regla del owner: nada web sin esto)

`site/scripts/visual-check.mjs` (capturas desktop+móvil × 2 temas, consola, cobertura) ·
`interaction-check.mjs` (hover→resaltado, búsqueda→ficha, filtros con re-encuadre, repintado de
tema, móvil sin overflow) · `shot-stats.mjs` / `crop-stats.mjs` (percentiles de gris para medir
contraste real) · e2e `tests/e2e/graph-paper-style.spec.ts`.
Convertir la posición de un nodo a píxeles: `renderer.framedGraphToViewport(renderer.getNodeDisplayData(id))`
+ `canvas.getBoundingClientRect()` (NO calcularlo a mano: `getNodeDisplayData` devuelve coords normalizadas).

## Referencia implementada

GOS: `site/src/components/GraphExplorer.astro` (explorador) y `GosGraph.svelte` (mini-mapa del home),
página `site/src/pages/graph.astro`. Informe con medidas: `~/handoffs/2026-09-14-gos-grafo-paper-ink.md`.
