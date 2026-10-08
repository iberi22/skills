---
name: bateria-de-testing
description: "Bateria de testing completa para apps local-first (Astro/Svelte): unit, plantillas, E2E (offline, tema y movil), barrido visual, QA exploratoria y cierre. Router sobre vitest, Playwright y tester-army/e2e."
version: 1.2.0
author: Hermes Agent (RECONSTRUCTED 2026-09-07 tras incidente skills 2026-09-06; actualizado 2026-10-02)
tags: [testing, local-first, astro, svelte, e2e, offline, qa, visual]
related_skills: [gentleman-playwright, test-writer-fixer, test-results-analyzer, agentic-e2e, delivery-verification-gate, threejs-qa-release]
---

# Bateria de Testing (apps local-first)

> Reconstruido 2026-09-07 (el cuerpo original se perdio en el incidente de skills). 2026-10-02: se quitaron
> las referencias a `testing-battery`, `vitest-testing` y `playwright-e2e-patterns`, que no existen, y se
> agregaron las capas que la puesta a punto de GARA-G demostro necesarias.

## Capas (en orden)

1. **Unit (vitest)**: logica pura, stores, utils, rutas API llamando al handler real. No mockear lo que se testea.
2. **Plantillas**: compilar todo `.astro` con el compilador de Astro en un test (GARA-G
   `tests/astro-compile.test.ts`); un parentesis de mas en un componente compartido tumbo siete paginas.
   Para Svelte, montar componentes en jsdom cuando tengan logica de interaccion.
3. **E2E deterministico (Playwright)**: flujos criticos con sesion via un solo helper; offline real
   (bloquear red y repetir flujos) en apps local-first. Reglas en `gentleman-playwright` → Hardening rules.
4. **Matriz de tema y dispositivo**: claro/oscuro × escritorio/movil tactil, con el tema fijado antes de la
   primera pintura. Barrido visual de todas las rutas con deteccion de capturas en blanco (GARA-G
   `scripts/visual-sweep.mjs`) y revision humana de hojas de contacto.
5. **Storage**: IndexedDB/transaccional — migraciones, corrupcion, cuota llena.
6. **Locales**: si la app es multi-idioma, smoke por locale (strings faltantes = fallo).
7. **QA exploratoria antes de una demo o release**: bug bash con `agentic-e2e` (tester-army/e2e), charters por
   persona del cliente real; solo cuentan los hallazgos que un test de repro hace fallar.
8. **Cierre**: build de produccion + suite completa + matriz de rutas + escaneo de logs
   (`delivery-verification-gate`). Juegos/3D: `threejs-qa-release`.

## Reglas

- Rojo en cualquier capa = no hay release.
- Prohibido editar/borrar tests para hacerlos pasar; cada fallo se clasifica con evidencia (`test-writer-fixer`).
- Se prueba el commit que se entrega: SHA en el informe.
- Corridas largas o en paralelo contra un build de produccion, no contra el dev server.
