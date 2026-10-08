---
name: web-visual-verification
description: 'Use when shipping web UI: screenshot and review first.'
version: 1.0.0
---

# Web Visual Verification — ninguna entrega web sin evidencia visual

Toda entrega web (página, hero, componente visible) se valida así ANTES de
reportarla como lista. `curl 200` y `build 0` NO bastan: no ejecutan JS ni
muestran lo que ve el usuario.

## Protocolo (en orden)

1. **Rama real del dev**: `git status -sb` + confirma qué sirve el puerto.
   Si el CSS en browser no coincide con el fuente (markup nuevo + estilos
   viejos), el dev tiene caché stale: mátalo, borra `node_modules/.vite` y
   reinícialo. Verifica el módulo servido con curl antes de seguir.
2. **Playwright con Chromium del sistema**: script que capture por viewport
   (1440x900 desktop, 390x844 móvil): errores `console` tipo error +
   `pageerror`, métricas (fondo computado, elementos clave) y screenshot PNG.
   Cero errores de consola es requisito.
3. **Revisión con visión**: pasa CADA screenshot por `vision_analyze` pidiendo
   lista brutal de defectos (roto, desalineado, ilegible, poco contraste).
   Si da 500, reintenta con imagen reducida al 50%; si persiste, delega a
   subagente con visión; en último caso, análisis por píxeles programático.
4. **Fix loop**: corrige lo encontrado, rebuild, re-screenshot, re-revisa.
5. **Reporta con evidencia**: consola (0 errores), capturas revisadas, hallazgos
   y qué quedó pendiente fuera de scope.

## Pitfalls registrados

- Dev server Astro/Vite puede servir markup nuevo con CSS viejo (transform
  cache). Síntoma: `getComputedStyle` no coincide con el fuente. Fix: kill +
  `rm -rf node_modules/.vite` + restart + verificar módulo de estilos por curl.
- El navegador-herramienta cachea agresivo y mezcla versiones: no lo uses como
  ground truth; usa Playwright con contexto fresco + curl del CSS servido.
- Iconos vía CDN externo (Font Awesome) pueden no cargar: prefiere SVG inline
  para iconos críticos (FAB, checks).
- FAB fijo tapa CTAs full-width en móvil al hacer scroll: achícalo en móvil
  (56px) y documenta que el solape parcial es inherente al patrón fijo.
- Huérfanas tipográficas en H1 fluido: pega la conjunción con `&nbsp;` hacia
  adelante (`y&nbsp;Toma`) + `text-wrap: balance`; verifica con crop del H1.
- La toolbar de Astro aparece en screenshots de dev: es solo-dev, ignórala en
  la revisión (prod no la trae).
- `browser_exec`/`capture_screenshot` pueden dar timeout en páginas con
  animaciones pesadas: prefiere el script Playwright para capturas.
- **"El DOM lo ve pero la captura no" (medido 2026-09-30).** El DOM reporta valores de
  campo (`options`, `input.value`) con independencia de la visibilidad, así que el agente
  "sabe" que el formulario existe aunque esté bajo el fold. Medido en fixture con hero de
  1200px: sin scroll, `inViewport=false` (top 1216 en viewport 720) y la imagen NO contenía
  el formulario; con `scrollIntoView({block:'center'})` + 500 ms de espera, la imagen lo
  tenía. **Chrome y Obscura se comportan IGUAL (delta 0px): no es un bug del motor, es
  la secuencia de captura.** Regla: hacer scroll al objetivo, esperar, y recién ahí capturar.
  Preferir `scrollIntoView` sobre `scrollTo` cuando se sabe qué elemento importa.
- **Midiendo contraste, componer el ALFA (medido 2026-10-01).** Comparar el color
  declarado contra el color de fondo da falsos positivos enormes:
  `rgba(6,182,212,.12)` leído como `#06b6d4` reporta `1.34:1` cuando el contraste real
  ronda `4:1`, y `color(srgb 0.87 0.87 0.85 / 0.6)` trae canales en 0-1 que hay que
  multiplicar por 255. Con la medición ingenua aparecieron `1.04:1` y `1:1` en elementos
  perfectamente legibles. Regla: componer `fg*a + bg*(1-a)` subiendo por los ancestros
  hasta encontrar un fondo opaco, y normalizar los canales 0-1. Un ratio rondando 1.0 es
  señal de error de medición, no de diseño — investigar el parser antes de tocar el color.
- **Auditar contra TODOS los fondos del tema, no solo el de la tarjeta (medido 2026-10-01).**
  El token `muted` daba 4.21:1 sobre el fondo de página y 3.45:1 sobre `elevated`. El
  sitio tenía 4 superficies distintas (page, card, elevated, elevated-850) y la peor es la
  que manda. Calcular el mínimo entre todas antes de elegir el tono de reemplazo.
- **Un token puede tener que partirse en dos (medido 2026-10-01).** El violeta de acento
  daba `4.52:1` como texto de enlace sobre superficie pero `4.23:1` con texto blanco como
  fondo de botón: subirlo arreglaba un uso y rompía el otro. Regla: antes de tocar un
  token de color, listar sus usos (texto sobre superficie, fondo con texto encima, borde,
  sombra) y tratar cada uno por separado. Un token que sirve para dos roles con requisitos
  opuestos necesita dos variables.
- **`!important` para lo que viene de un paquete (medido 2026-10-01).** Los tokens de
  `--swal-text-muted` / `--swal-accent` venían de `@swal/ui`, un tarball externo no
  editable desde el repo. Sobreescribir la variable CSS es preferible a parchear el
  paquete: sobrevive a la próxima actualización de la dependencia.
- **El detalle de un token puede tapar el fix de verdad.** Cambiar 3 selectores locales a
  un color más fuerte y LUEGO arreglar el token global deja el override como ruido con un
  comentario que cita valores ya obsoletos. Regla: al revisar el propio trabajo, comprobar
  si cada cambio local sigue siendo necesario después del arreglo global. Un commit de
  limpieza que devuelve código a su forma anterior y borra el comentario obsoleto vale
  más que el commit original.
- **La palabra "ONLINE" o el spinner pueden ser falsos positivos.** Antes de diagnosticar
  un bloqueo, medir estilo computado, `getBoundingClientRect()` y `display`: un elemento
  con `display:none` no es el culpable aunque exista en el DOM.
