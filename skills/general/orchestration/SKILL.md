---
name: orchestration
description: "Use Orca orchestration for structured multi-agent coordination: Orca worktrees/terminals/handoffs, routing to Gestalt or Qwen dispatches. Router delgado."
version: 1.1.0-reconstructed
author: Hermes Agent (RECONSTRUCTED 2026-09-07 tras incidente skills 2026-09-06 — validar)
tags: [orchestration, orca, multi-agent, worktrees, coordination]
related_skills: [orca-cli, gestalt-orchestration, multi-agent-orchestration-workflow]
---

# Orchestration (router)

> ⚠️ RECONSTRUCTED 2026-09-07 — cuerpo original irrecuperable tras el
> incidente de skills. Reconstruido desde skills hermanos. Belal: validar.

## Elegir el orquestador

- **Orca** (worktrees aislados, terminales, handoffs entre agentes,
  browser embebido): skill `orca-cli`. Estado en `~/.orca/workspaces/`;
  hooks en `~/.orca/agent-hooks/`. Preferir sobre `git worktree` manual
  cuando hay estado Orca de por medio.
- **Gestalt** (VFS, conflictos, bus de eventos → Xavier): skill
  `gestalt-orchestration` (Hermes orquesta, Gestalt ejecuta, Xavier
  persiste).
- **Dispatch directo por cuota** (QwenCloud, reglas de asignacion,
  monitoreo): skill `multi-agent-orchestration-workflow`.

## Reglas comunes

- Trazabilidad: eventos de agente → Xavier (`agent-event-bus-traceability`
  en esta misma categoria).
- Trabajo en worktrees/ramas aisladas; merge por el flujo del orquestador
  elegido, nunca directo a main sin verify.
- Handoffs explicitos ("give this to another agent") con contexto
  autocontenido: objetivo + archivos + criterios de verificacion.
