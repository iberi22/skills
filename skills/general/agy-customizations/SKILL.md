---
name: agy-customizations
description: "Customizar Antigravity/agy: donde viven skills, rules, agentes y hooks, formato .skill-lock.json y como agregar personalizaciones sin romper updates."
version: 1.1.0-reconstructed
author: Hermes Agent (RECONSTRUCTED 2026-09-07 tras incidente skills 2026-09-06 — validar)
tags: [antigravity, agy, customizations, skills, rules, hooks]
related_skills: [agy, antigravity_guide, orca-cli]
---

# Agy Customizations

> ⚠️ RECONSTRUCTED 2026-09-07 — cuerpo original irrecuperable tras el
> incidente de skills. Reconstruido desde layout observado + skill `agy`.
> Belal: validar antes de confiar detalles.

## Donde vive cada customizacion (observado en disco)

- Skills: `~/.agents/skills/<nombre>/SKILL.md` (+ `references/`).
- Reglas: `~/.agents/rules/` (dir; si esta vacio no hay rules activas).
- Lock: `~/.agents/.skill-lock.json` — schema por skill:
  `source` (repo), `sourceType: github`, `sourceUrl`, `skillPath`
  (ej. `skills/orca-cli/SKILL.md`), `skillFolderHash`, `installedAt`.
- Skills espejo de Antigravity IDE: `~/.gemini/config/skills/`.
- Uso del agente: skill `agy` (flags Go-style con `=`, print vs
  interactivo, `--dangerously-skip-permissions`).

## Reglas

1. Lo instalado por lock (source github) NO se edita a mano: se reinstala
   desde upstream o se hace override en `rules/`.
2. Lo autorado por Belal (sin entrada en lock) vive como dirs reales y se
   versiona en repo propio si debe sobrevivir reinstalaciones.
3. Hooks de agente: `~/.orca/agent-hooks/` (ej. `codex-hook.sh`) — leer
   antes de modificar; un hook roto silencia al agente.
4. Tras agregar/quitar skills, verificar que el agente los lista
   (`agy agent` / listado de skills del IDE) antes de dar por hecho.
