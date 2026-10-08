---
name: swal-t3-pr-babysitter
title: SWAL T3 PR Babysitter & Rate-Limit Shield
description: Protocolo de monitoreo y babysitting reactivo de Pull Requests para agentes en T3 Code y CLI. Basado en el motor de Theo Browne (10% de reserva GraphQL, 0 bucles de polling, inspeccion por fingerprint y despertar por eventos).
tags:
  - t3-code
  - github
  - pr
  - rate-limit
  - orchestration
category: orchestration
---

# SWAL T3 PR Babysitter & Rate-Limit Shield

> **CANÓNICO:** Inspirado en la implementación de Theo Browne en T3 Code (`src/sourceControl/githubGraphQlBudget.ts` y `src/orchestration-v2/PullRequestWatchReactor.ts`).
> Reduce el consumo de cuota de GitHub en más de 75%, elimina procesos CLI zombies (`gh pr checks` en loop) y evita bloqueos secundarios (403).

---

## 1. Reglas de Operación

1. **En T3 Code (Modo Nativo MCP):**
   - **PROHIBIDO:** Hacer polling con scripts bash o comandos `sleep`.
   - **OBLIGATORIO:** Usar `watch_pull_request` y finalizar el turno inmediatamente:
     ```markdown
     Llamar: watch_pull_request(url="https://github.com/owner/repo/pull/123")
     Fin de turno: T3 Code despertará automáticamente al agente cuando:
     - Los checks de CI terminen (PASS / FAIL).
     - Alguien comente o envíe una revisión.
     - La rama entre en conflicto con base.
     ```
   - Al terminar la tarea o entregarla al usuario, llamar a `unwatch_pull_request`.

2. **En Terminal CLI / Subagentes Pi / Hermes:**
   - Usar el módulo `~/.hermes/scripts/swal-pr-watch.py`.
   - **Protección de Reserva:** Mantiene siempre una reserva del 10% de cuota GraphQL (`GRAPHQL_RESERVE_RATIO = 0.1`).
   - **Fingerprint de 1 punto:** Lee únicamente la huella del commit y estado; si la huella no ha variado, **no descarga detalles ni actividad**.
   - **Fail-Safe:** Tras 8 fallos consecutivos de red o API, el watcher aborta limpiamente sin saturar la máquina.

---

## 2. Comandos Canónicos CLI

```bash
# Snapshot determinista de un PR (1 punto GraphQL):
~/.hermes/scripts/swal-pr-watch.py --repo iberi22/xavier --pr 2845

# Salida estructurada JSON para subagentes y analizadores:
~/.hermes/scripts/swal-pr-watch.py --repo iberi22/xavier --pr 2845 --json

# Babysitter en background para tareas de larga duración (cada 120s):
~/.hermes/scripts/swal-pr-watch.py --repo iberi22/xavier --pr 2845 --watch --interval 120
```

---

## 3. Matriz de Estados de Wakeup

| Evento Observado | Acción del Agente / Pipeline |
| :--- | :--- |
| `check_state == "SUCCESS"` | Verificar gate localmente y proceder con merge o siguiente PR de la cadena. |
| `check_state == "FAILURE"` | Despertar especialista `test-writer` o `rust-fixer` en worktree aislado. |
| `comments > prev_comments` | Leer nuevo feedback y verificar si requiere aclaración del dueño (`owner`). |
| `mergeable == "CONFLICTING"` | Rebase en rama local; nunca mergear ramas en conflicto. |
