# Incidentes Reales de Referencia — Ola 6

Estos casos documentan problemas reales encontrados durante Ola 6 que el template
profesional previene. Úsarlos como ejemplos al entrenar a otros agentes.

## #810 — ACs Incorrectas (SRC.md por módulo)

**Problema:** El issue pedía crear `src/*/SRC.md` (un archivo por módulo).
La convención real del GitCore Protocol es un solo `.gitcore/SRC.md`.

**Causa raíz:** El creador del issue asumió estructura basada en proyectos anteriores.
No verificó la estructura real del repo.

**Prevención:** Anti-Hallucination Guard punto 2: "SRC.md → `.gitcore/`; NEVER in `src/*/`".

## #801 — Body Vacío

**Problema:** El issue fue creado solo con título y labels, body completamente vacío.
Jules recibió cero instrucciones.

**Causa raíz:** `gh issue create --title "..." --label "..."` sin `--body "..."`
El template no se aplicó.

**Prevención:** Body validation pre-submit: verificar `gh issue view --json body --jq '.body | length'` > 0.

## #798 — Falso Positivo de Jules

**Problema:** Jules reportó "Completed" pero no produjo branches, PRs, ni commits.
El código ya estaba completo pero features.json decía 50%.

**Causa raíz:** La sesión de Jules corrió verificación, determinó que no había cambios
necesarios, y completó sin actualizar features.json.

**Prevención:** Post-completion verification: buscar branches + PRs. Si no hay cambios,
verificar manualmente y actualizar features.json.

## Características con Caveats Reales (features.json vs realidad)

| Feature | Progreso Declarado | Realidad | Gap |
|---------|-------------------|----------|-----|
| feat-mesh-network | 100% | MVP: HTTP+libp2p+ACL | Iroh/Tor/on-chain = Phase 2 |
| feat-telegram-bot | 100% | MVP: teloxide básico | Extra commands pendientes |
| feat-auto-improvement | 100% | Phase 1: engine + CLI | Phase 2: experiment policy |
| feat-unified-storage | 100% | SQLite productivo | Columnar/VACUUM polish out of MVP |
| feat-hybrid-search | 100% | BM25+Vector funcionando | AMD GPU local embedding fallback |
| feat-encryption-at-rest | 100% | AES-256-GCM integrado | No testeado desde 2026-06-16 |
| feat-openclaw-scanner | 100% | Implementado PR #342 | No testeado desde 2026-06-25 |
| feat-agent-cli-commands | 100% | Status/Sync subcommands | No testeado desde 2026-06-25 |

## Métrica de Riesgo Real (Scoring)

Cada feature se evaluó con:
- **3 puntos** = MVP (no production-ready)
- **2 puntos** = Stale (>1 mes sin testear) o Incomplete phases
- **1 punto** = Optional polish pending o No tests listed (en features.json)

Total risk score Ola 6: 33/75. Features más críticas: mesh-network, telegram-bot, unified-storage.
