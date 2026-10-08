---
name: gitcore-swal-workflow
description: "SWAL workflow from idea to verified wave: organic routing (direct inline / delegated direct / optional SDD), local GitCore issues, SRS mapping. Thin router over gitcore."
version: 1.1.0
author: Hermes Agent
tags: [gitcore, swal, workflow, routing, sdd, orchestration]
related_skills: [gitcore, gestalt-orchestration, sdd-hibrido]
---

# GitCore SWAL Workflow (router)

## Organic routing (gentle-ai v2.3.0)

Apply routing before creating `.gitcore/sdd/`:

- **Direct inline**: 1–3 trivial files → do it inline, no delegation, no SDD.
- **Delegated direct**: 4+ files or 2+ non-trivial → `delegate_task`, no SDD.
- **Optional SDD**: high ambiguity → offer an optional SDD; if yes, create
  `.gitcore/sdd/specs/###-feat/onepage.md` (one-page P1 spec, minimal HOW plan,
  and [P] tasks).
- `rm -rf .gitcore/sdd` cleans up without touching `features.json`.
- See `sdd-hibrido` (`references/routing.md`).

## SDD one-page + SRS mapping

- The ephemeral spec in `.gitcore/sdd/` references the durable `REQ-xxx` in
  `docs/SRS/REQUIREMENTS.md`.
- The drift detector `srs-src-drift-detector` keeps the traceability.
- Stable human docs live in `docs/`; AI specs stay isolated in `.gitcore/sdd/`.

## Waves (delegated execution)

The design and detail of waves live in `gitcore` (phases PRE-wave → design →
issues → Gestalt → merge + verify), and execution lives in `gestalt-orchestration`.
This skill only decides the routing.
