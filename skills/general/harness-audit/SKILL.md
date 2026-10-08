---
name: harness-audit
description: "Auditar el arnes Hermes (cron jobs, skills activos vs uso real, presupuesto de memoria, reglas) con clasificacion rojo/amarillo/verde y plan de accion. Usar antes de cambios al harness."
version: 1.1.0-reconstructed
author: Hermes Agent (RECONSTRUCTED 2026-09-07 tras incidente skills 2026-09-06 — validar)
tags: [audit, harness, hermes, cron, skills, quality]
related_skills: [phase-audit, skill-library-maintenance, harness-context-auditor]
---

# Harness Audit

> ⚠️ RECONSTRUCTED 2026-09-07 — cuerpo original irrecuperable tras el
> incidente de skills. Reconstruido desde skills hermanos. Belal: validar.

## Alcance (solo lectura primero)

1. `~/.hermes/cron/jobs.json` — jobs, skills referenciadas, ultimas salidas.
2. `~/.hermes/skills/.usage.json` — `last_used_at` real vs skills cargados.
3. Memoria (`memory` tool): % usado, entradas obsoletas candidatas.
4. Reglas (`SYSTEM_RULES.md`) vs comportamiento observado.

## Metodo (patron phase-audit)

1. Revision paralela (jobs + uso + memoria) y web research si aplica.
2. Clasificar hallazgos: ROJO (roto/riesgo) / AMARILLO (deuda) / VERDE (ok).
3. Seguridad runtime del arnes: delegar detalle a `harness-context-auditor`.
4. Limpieza de skills: delegar criterio a `skill-library-maintenance`
   (nunca `rm` directo; `.archive/` + commit antes).

## Entrega

- Tabla hallazgo → severidad → evidencia (comando/output) → accion.
- Plan con pasos reversibles; cambios al harness solo con OK de Belal
  si tocan cron activo, secretos o memoria.
