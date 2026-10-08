---
name: swal-network-launch
description: Guía maestra para coordinar y priorizar el desarrollo y auditoría del ecosistema SWAL para el lanzamiento de la red (v1.0), basado en Readiness Scan v1.0 y GitCore 3.8.0.
---

# SWAL Network Launch (v1.0) Skill

You are an agent assigned to the SWAL Network Launch team. Your primary objective is to execute, monitor, or review code changes that push the SWAL ecosystem closer to the v1.0 mainnet launch.

## 1. Prioritization Framework
When assigning resources or selecting which repository to process next, strictly follow this priority queue based on current launch readiness:

1. **[P0] EDGE MESH (84% Ready)** 
   - **Goal:** Hardening phase. It's the core P2P library and currently the closest to 100%.
   - **Checklist:**
     - Finalize P2P Node Lifecycle (enviar/transmitir).
     - Harden Governance (thresholds and crypto verification).
     - Integrate Mesh Gossip.
     - Ensure GitHub Actions (CI) passes.

2. **[P1] SYNAPSE PROTOCOL (93% Ready - high complexity)**
   - **Goal:** Core integration.
   - **Checklist:**
     - Complete the Cognitive Layer orchestration.
     - Build out the Tauri Desktop Shell.
     - Finalize $KIND Tokenomics test vectors.

3. **[P2] XAVIER (99% Ready - Core Infra)**
   - **Goal:** Stable dependency.
   - **Checklist:**
     - Must remain in "stable" state.
     - No breaking changes allowed without cross-ecosystem PR reviews. 
     - Only process bug fixes, documentation, or security patches here.

4. **[P3] GARA-G (35% Ready)**
   - **Goal:** Long-term integration (v1.x).
   - **Checklist:**
     - Create the mandatory GitCore `SRC.md`.
     - Generate `implementation-score.json`.
     - Improve Marketplace features (Dir A + B).

## 2. GitCore 3.8.0 Compliance Rules
Before submitting ANY Pull Request that claims a feature is "v1.0 Ready", you must verify:
- The project has a `SRC.md` file detailing the domain models.
- Tests are passing (`pnpm test`, `cargo test`, `vitest`, depending on the stack).
- `features.json` is updated to reflect the new completion percentage.

## 3. Implementation Scores
Whenever you finish a wave of issues or a major PR on any project, you MUST trigger or run the script to update `.gitcore/implementation-score.json`. A project cannot be flagged as "Ready for Launch" unless this score matches reality.
