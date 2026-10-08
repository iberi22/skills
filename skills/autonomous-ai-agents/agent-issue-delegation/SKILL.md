---
title: "Agent Issue Delegation — Template Profesional para Delegar Issues a Agentes"
name: agent-issue-delegation
description: "Crear GitHub Issues de calidad profesional para delegar a agentes autónomos (Jules, Claude Code, Codex, OpenCode). Template con Current State medible, Anti-Hallucination Guard, Acceptance Criteria verificables, y pre-flight validation. Previene issues con body vacío, paths incorrectos, y ACs no verificables."
type: WORKFLOW
id: agent-issue-delegation
created: 2026-07-21
updated: 2026-07-21
summary: |
  Protocolo para crear issues de alta calidad para delegación a agentes.
  Incluye: template con Current State/Delt State, Anti-Hallucination Guard,
  Acceptance Criteria verificables por comando, body validation pre-submit,
  y file ownership map anti-conflicto.
keywords: [issues, delegation, template, agents, jules, claude-code, codex, opencode, anti-hallucination]
tags: ["#issues", "#delegation", "#template", "#agents", "#professional"]
---

# Agent Issue Delegation — Professional Issue Templates

> ⚠️ **CANONICAL TEMPLATE:** `gitcore-jules-issues` v3.0+ (unifica 6 skills previos, Jul 2026).
> Este skill contiene **reglas generales de delegación** válidas para cualquier agente.
> Para el template section-by-section exacto, cargar `gitcore-jules-issues`.

> ⚠️ **Rule:** Label `jules` triggers Jules. For other agents use their convention.
>
> ⚠️ **Language:** Issues, documentation, and code examples MUST be in English. Only user-facing conversation may be in the user's language. When the user writes in Spanish, respond in Spanish but keep code comments, issue bodies, documentation, and PR descriptions in English.
>
> ⚠️ **Wave Size = 14-15 issues:** Jules takes issues with the `jules` label up to ~14-15 simultaneously. Create waves of exactly 14-15 with disjoint file islands.
> - Less than 10 wastes parallel capacity
> - More than 16 becomes unmanageable for review/merge
> - Issue #15 = reconciliation (features.json update) — ALWAYS last
> - Each issue = single action. 1 issue = 1 file = 1 change. Multi-feature issues fail 100%.
>
> ⚠️ **features.json NOT modified during the wave.** Each issue writes progress to `.gitcore/ola8-progress/<feature-id>.json` (individual file). The reconciliation issue at wave end unifies all into features.json.
>
> ⚠️ **Single Action = Success:** Single-action issues (verify + update progress file) have ~70% success rate. Multi-feature issues have 0%. Always split.
>
> ⚠️ **Delivery binding:** Every issue delegated to an agent MUST result in committed+push to GitHub. Local-only changes are not a valid delivery.
>
> ⚠️ **Repo boundary:** Xavier (Rust) and isar_agent_memory (Dart) are separate repos. Do not cross-contaminate issues. They communicate via MCP/HTTP only.

## ⚠️ MANDATORY RULES FOR EVERY ISSUE


### 🔍 Web Research Required (MANDATORY — in EVERY issue)

⚠️ **The user WILL correct you if this section is missing. Always include it.**

Every issue MUST contain a Web Research Required section. This is non-negotiable.

The agent must research the most current approaches BEFORE implementing. Without this section, the agent implements with potentially outdated knowledge.

Include **3-4 specific, searchable queries**:
```markdown
## Web Research Required
1. `search: "[primary technology] best practices 2026"`
2. `search: "[alternative library/pattern] comparison"`
3. `search: "[crate/package] documentation latest API"`
4. `search: "[algorithm/approach] modern implementation"`
```

Failure to include this section = issue is INCOMPLETE. Do not delegate without it. Use `gitcore-jules-issues` skill for the exact template.

### ✅ Tests + Lint (MANDATORY)
**Every delivery MUST include:**
- Tests validating the functionality (unit + integration where applicable)
- Lint passes with 0 errors (use correct command per stack):
  - **Rust:** `cargo clippy -p xavier --all-targets -- -D warnings`
  - **Dart/Flutter:** `dart analyze lib/`
  - If the agent cannot pass lint, document why in the PR

Without tests + green lint → the PR will NOT be merged.

### 📍 Documentation Language (MANDATORY)
All code comments, variable names, issue bodies, PR descriptions, README, docs, and commit messages MUST be in English. Only user-facing conversation may be in the user's language (e.g. Spanish when the user writes in Spanish). When in doubt, write in English.

### 🧱 Repo Boundaries (MANDATORY)
Before creating any issue, confirm the feature belongs to THIS repo:
- **Xavier** (`iberi22/xavier`) = Rust memory server — MCP/HTTP interface, mesh sync, security
- **isar_agent_memory** (`iberi22/isar_agent_memory`) = Dart/Flutter memory engine — offline-first, mobile/edge
- They communicate via MCP/HTTP only. Never create Xavier features in isar_agent_memory or vice versa.

### Delivery Requirements

**Every issue delegated to an agent MUST result in committed+push to GitHub.** Local-only changes are not a valid delivery — the repo on GitHub is the single source of truth.

**Documentation and code MUST be in English.** Only user-facing conversation may be in the user's language. Issue bodies, code comments, variable names, PR descriptions, API docs — all English.

**Xavier integration is via MCP only.** Never couple code between Xavier (Rust) and isar_agent_memory (Dart). They are separate repos that communicate through MCP/HTTP.

### Post-Creation QA Audit

After creating ALL issues in a wave, run verification BEFORE applying any `jules` label:

```bash
# 1. Check body length (empty body = wasted session)
for n in $(gh issue list --repo <repo> --label wave-N --state open --json number --jq '.[].number'); do
  body=$(gh issue view $n --repo <repo> --json body --jq '.body | length')
  title=$(gh issue view $n --repo <repo> --json title --jq .title)
  if [ "$body" -lt 50 ]; then
    echo "❌ #$n EMPTY BODY ($body chars): $title"
  elif [ "$body" -lt 200 ]; then
    echo "⚠️ #$n SHORT BODY ($body chars): $title"
  else
    echo "✅ #$n ($body chars)"
  fi
done

# 2. Check Web Research Required section exists
for n in $(gh issue list --repo <repo> --label wave-N --state open --json number --jq '.[].number'); do
  body=$(gh issue view $n --repo <repo> --json body --jq .body)
  if echo "$body" | grep -q "Web Research"; then
    echo "✅ #$n has Web Research"
  else
    echo "❌ #$n MISSING Web Research Required — FIX BEFORE DELEGATING"
  fi
done

# 3. Check Acceptance Criteria and Failure Recovery
for n in $(gh issue list --repo <repo> --label wave-N --state open --json number --jq '.[].number'); do
  body=$(gh issue view $n --repo <repo> --json body --jq .body)
  has_ac=$(echo "$body" | grep -c "Acceptance Criteria")
  has_fr=$(echo "$body" | grep -c "Failure Recovery")
  echo "#$n: AC=$has_ac FR=$has_fr"
done

# 4. Verify file islands are disjoint
python3 -c "
issues = {}
for n in [LIST_OF_ISSUE_NUMBERS]:
    # Extract Files to Modify from each issue
    issues[f'#{n}'] = ['path1.rs', 'path2.rs']  # fill from issue bodies
for i1, f1 in issues.items():
    for i2, f2 in issues.items():
        if i1 < i2 and set(f1) & set(f2):
            print(f'❌ CONFLICT: {i1} and {i2} share files!')
print('✅ File islands verified')
"
```

### Template Validation Checklist

Antes de publicar CADA issue, ejecutar mentalmente:
- [ ] Current State con datos duros (líneas, %, archivos, fechas)
- [ ] **Web Research Required** presente con 3-4 queries específicas
- [ ] Acceptance Criteria verificables por comando (`grep`, `cargo test`, etc.)
- [ ] Files to Modify: tabla con Change + Risk
- [ ] DO NOT touch explícito con paths
- [ ] Anti-Hallucination Guard (mínimo 4 puntos)
- [ ] Verification commands correctos y ejecutables en el repo
- [ ] Dependencies & Merge Order completos
- [ ] **Failure Recovery** table (mínimo 3 filas)
- [ ] Label `jules` NO aplicado (se aplicará manualmente cuando toque)
- [ ] Body length > 200 chars

## Common Failure Modes (from Gestalt Fase 1 session, 2026-07-25)

| Failure | Cause | Prevention |
|---------|-------|-----------|
| **Web Research Required missing** | Issue creado sin sección de investigación | QA audit post-creación: script que verifica "Web Research" en body |
| **Wave < 14 issues** | Subestimación del alcance | Siempre target 14-15 issues. Dividir issues más grandes en sub-tareas. |
| **Template secciones compactadas** | Prisa por crear rápido | Template Validation Checklist ANTES de publicar |

### Pre-flight Checklist (Before Creating)

- [ ] `features.json` read — current progress documented
- [ ] **Repo identity verified** — confirm the feature belongs to THIS repo, not a sibling project. Xavier (Rust) and isar_agent_memory (Dart) are separate repos — do NOT create Xavier issues in isar_agent_memory or vice versa.
- [ ] Latest commits reviewed (understand what changed)
- [ ] **GitCore alignment** verified: SRC.md, docs/SRS/REQUIREMENTS.md, docs/SRS/ARCHITECTURE.md, .gitignore must exist and be up to date. If missing, fix GitCore alignment first.
- [ ] Codebase paths verified against real repo
- [ ] File ownership map built (shared files = conflict)
- [ ] **Per-stack commands verified** — use the correct lint/test command for the project stack (Rust: `cargo`, Dart: `dart`/`flutter`, Node: `pnpm`/`npm`)
- [ ] **Body validation**: `gh issue view <N> --json body --jq '.body | length'` > 0
- [ ] **Domain Scope Validation** ⚠️: does the proposed feature belong to THIS repo or ANOTHER?
  - Does it contain business logic from a specific domain (medical, legal, financial, gaming)?
  - If YES → the feature likely belongs to another repo (app/service), not the generic lib/package
  - If NO (infrastructure, abstract interface, generic API, pluggable adapter) → it belongs here
  - Validate: read pubspec.yaml / Cargo.toml / package.json — does the name/desc describe a generic package or a domain-specific one?
  - Validate: if you see domain-prefixed classes (`MedicalXxx`, `LegalXxx`, `FinanceXxx`) in a generic repo, it's a RED FLAG

- [ ] `features.json` read — current progress documented
- [ ] **Repo identity verified** — confirm the feature belongs to THIS repo, not a sibling project. Xavier (Rust) and isar_agent_memory (Dart) are separate repos — do NOT create Xavier issues in isar_agent_memory or vice versa.
- [ ] Latest commits reviewed (understand what changed)
- [ ] **GitCore alignment** verified: SRC.md, docs/SRS/REQUIREMENTS.md, docs/SRS/ARCHITECTURE.md, .gitignore must exist and be up to date. If missing, fix GitCore alignment first.
- [ ] Codebase paths verified against real repo
- [ ] File ownership map built (shared files = conflict)
- [ ] **Per-stack commands verified** — use the correct lint/test command for the project stack (Rust: `cargo`, Dart: `dart`/`flutter`, Node: `pnpm`/`npm`)
- [ ] **Body validation**: `gh issue view <N> --json body --jq '.body | length'` > 0
- [ ] **Domain Scope Validation** ⚠️: does the proposed feature belong to THIS repo or ANOTHER?
  - Does it contain business logic from a specific domain (medical, legal, financial, gaming)?
  - If YES → the feature likely belongs to another repo (app/service), not the generic lib/package
  - If NO (infrastructure, abstract interface, generic API, pluggable adapter) → it belongs here
  - Validate: read pubspec.yaml / Cargo.toml / package.json — does the name/desc describe a generic package or a domain-specific one?
  - Validate: if you see domain-prefixed classes (`MedicalXxx`, `LegalXxx`, `FinanceXxx`) in a generic repo, it's a RED FLAG

## Template Obligatorio — Canonical Xavier #980 Format

**Esta es la ÚNICA plantilla aceptada para delegar issues a agentes.** Sigue exactamente el formato del issue Xavier #980 (ver `references/xavier-980-template.md` para el ejemplo completo con explicaciones).

```
# [Wave N.XX] feat-xxx — Human-readable title

> Wave N — [Foundation/Infra/Core/Polish]. Label: `enhancement`, `ola{N}`, `wave-{N}`

---

## Current State (MEDIBLE)
[HARD data — file paths, line counts, last modified, % in features.json]
- File: `path/to/file.ext` (N lines, last modified YYYY-MM-DD)
- Class/function at line ~XX: [current behavior — include exact code snippets]
- Feature: `feat-xxx` at N% in `.gitcore/features.json`
- Tests: N existing, N passing
- Reference impl: [existing similar feature if applicable]

## Desired State (DELTA)
[EXACT changes — section by section, with line numbers]
- **Section A** (lines XX-YY): Add [specific functionality with method signatures]
- **Section B** (new method `foo()`): Implement [behavior]
- **New file**: `path/to/new.ext` with [purpose]

## 🌐 Web Research Required (MANDATORY — RESEARCH BEFORE CODING)
1. `search: "[primary technology] best practices 2026"`
2. `search: "[alternative/pattern] comparison implementation"`
3. `search: "[crate/package] documentation latest"`
4. `search: "[algorithm/approach] modern implementation"`

Cite sources and learnings in the PR description.

## Exact Technical Context
[File paths with line numbers, function signatures, struct/class definitions, CRITICAL gotchas]
- File: `path/to/file.ext` (N lines)
  - `fn_a()` at line XX — what it does, returns
  - `fn_b()` at line YY — how it's used
- Struct/class: `TypeName` at line ZZ — fields: [a, b, c]
- Related: `path/to/related.ext` (M lines) — relevant section
- ⚠️ CRITICAL: [stack-specific gotchas, path conventions, excluded modules]

## Problem
[2-3 sentences: what problem this solves, why it matters, what breaks without it]

## Acceptance Criteria (VERIFIABLE)
[Each checkbox MUST be validateable by command, not opinion]
- [ ] `grep -c "required_pattern" path/to/file.ext` returns N
- [ ] Stack lint: `cargo clippy -p xavier --all-targets -- -D warnings` (Rust) OR `dart analyze lib/` (Dart) OR `pnpm lint` (Node)
- [ ] Stack tests: `cargo test -p xavier --lib module::test` (Rust) OR `flutter test path/to/test.dart` (Dart)
- [ ] Stack check: `cargo check --workspace` (Rust) OR `dart analyze lib/` (Dart)
- [ ] `.gitcore/ola8-progress/<feature-id>.json` created with feature at 100%

## Files to Modify
| File | Current State | Change | Risk |
|------|--------------|--------|------|
| `path/to/file.ext` | N lines | [specific change] | LOW/MED/HIGH |
| `.gitcore/ola8-progress/<feature-id>.json` | new | Create at 100% | LOW |

⚠️ Do NOT modify features.json during the wave. Per-feature progress goes to `.gitcore/ola8-progress/<feature-id>.json`; wave-end reconciliation unifies all.

## DO NOT touch (Anti-Regression)
- [explicit paths, not generic]
- [other issue code islands]
- Revert noise: `git checkout origin/main -- Cargo.toml` if agent modifies it
- NO create .patch, .py, .txt loose files in repo root

## Anti-Hallucination Guard ⚠️
1. **Verify before create**: `ls path/to/existing.file` before assuming it exists
2. **Path conventions**: SRC.md → `.gitcore/`; features → `.gitcore/features/`; NEVER in src/*/
3. **No invent APIs**: Only implement what existing types/interfaces define
4. **Double-check paths**: All relative from repo root
5. **Stack verification**: Read pubspec.yaml (Dart) / Cargo.toml (Rust) / package.json (Node) before using stack commands

## Verification
```bash
# Stack-appropriate commands — adjust per project
# Dart/Flutter:
cd /path && dart analyze lib/ 2>&1 | tail -5
# Rust:
cd /path && CARGO_TARGET_DIR=/tmp/rt cargo check --workspace 2>&1 | tail -5
# Tests:
cd /path && flutter test path/to/test.dart 2>&1 | tail -5
# Feature progress:
python3 -c "import json; d=json.load(open('.gitcore/features.json')); print([f['id']+'='+str(f['progress_pct'])+'%' for f in d['features'] if f['progress_pct']<100])"
```

## Dependencies & Merge Order
- **Depends on:** #N | **Blocked by:** #M | **Parallel:** #P
- **Merge order:** 1 (foundation) → 2 (features) → 3 (tests) → 4 (docs/release)
- **Effort:** Small (<1h) / Medium (1-4h) / Large (4h+)

## Failure Recovery
| If this happens | Action |
|----------------|--------|
| `cargo check` / `dart analyze` fails | Fix imports first, do NOT commit broken code |
| File doesn't exist | Run `find . -name "filename" -type f 2>/dev/null` |
| Test fails | Fix test or document wrong assumption |
| PR conflicts with parallel work | Rebase on main, re-run verification |
| Stack manifest modified | Revert: `git checkout origin/main -- Cargo.toml pubspec.yaml package.json` |
```

## 🔍 Post-Creation Review: Validar Issues del Agente

Cuando un agente (Jules, Codex, Claude) crea issues automáticamente, **revisa** antes de dejarlos abiertos:

### Señales de Domain Contamination
- **Clases con prefijo de dominio** (`Medical*`, `Legal*`, `Financial*`) en un repo que debería ser genérico
- **Referencias a paths de otra app** (`orionhealth/lib/features/...`, `xavier/src/...`)
- **Lógica de negocio específica** (síntomas médicos, cálculos financieros) donde debería haber interfaces abstractas
- **Ejemplos en el cuerpo del issue** con data de dominio (patientId, transactionId) en vez de data genérica (userId, content)

### Qué hacer
1. Identificar si el feature es **infraestructura genérica** (pertenece aquí) o **lógica de dominio** (pertenece a otra app)
2. Si es dominio → crear issue en el repo correcto, cerrar el original con redirect
3. Si es infraestructura pero mal nombrada → renombrar (eliminar prefijos de dominio)
4. Actualizar el prompt del agente para que respete boundaries entre repos

### Checklist de validación post-creación
- [ ] `gh issue list --json number,title,labels --state open` — ver todos los issues creados
- [ ] Por cada issue: ¿el título suena a dominio específico o a feature genérico?
- [ ] Por cada issue: ¿los code paths referenciados existen en ESTE repo?
- [ ] Por cada issue: ¿las clases propuestas tienen prefijo/sufijo de dominio que no corresponde?

---

## Common Failure Modes (de esta sesión)

| Failure | Cause | Prevention |
|---------|-------|-----------|
| **Body vacío** | `gh issue create` sin `--body` | Body validation pre-submit |
| **Paths incorrectos** | SRC.md creado en `src/*/` en vez de `.gitcore/` | Anti-Hallucination Guard punto 2 |
| **ACs no verificables** | "mejorar", "completar" sin métrica | Template con comandos específicos |
| **Falso positivo** (Completed sin cambios) | Agente no pudo pushear o task era solo research | Incluir "push branch + create PR" en prompt |
| **PR demasiado grande** | Issue pide demasiado | Dividir en PRs ≤200 lines |
| **Prompt genérico TypeScript** en proyecto Rust | Copiar template de otro proyecto | Usar prompts Xavier-específicos en `references/prompts-*.md` |
| **Multi-feature issue falla** | 2+ features en 1 issue = sesión entera pierde | 1 issue = 1 feature = 1 acción. Ver `references/session-failure-patterns.md` |
| **Shared file conflict** | 2 PRs paralelos modifican features.json | Usar per-feature files: `.gitcore/ola8-progress/<feature-id>.json`. Reconciliation al final. |
| **Cargo.toml noise en PRs** | Jules agrega lints.clippy o autobenches | Descartar siempre: `git checkout origin/main -- Cargo.toml` |
| **Domain contamination** | Agente crea feature con lógica de dominio (médico, legal) en repo de paquete genérico | Domain Scope Validation pre-flight: clases con prefijo `Medical*`, `Legal*`, `Finance*` en repo genérico = RED FLAG |
| **Stack-command mismatch** | Using `cargo` commands on a Dart project or `flutter` on a Rust project | Pre-flight: always verify stack first (read pubspec.yaml vs Cargo.toml). Include per-stack commands in the template. |
| **features.json conflict in parallel PRs** | Multiple PRs modify features.json simultaneously — always conflicts | Extract unique files per PR branch, commit directly to main, force push. See `references/batch-pr-integration.md`. |
| **PRs in DRAFT not merged** | Jules creates PRs as DRAFT — must mark ready first | Mark ready: `gh pr ready <N>`. Then merge with `--admin`. |
| **Stryker timeout** | Stryker mutation testing takes 6-7 min per file. Subagents timeout at 600s when Stryker runs. | Use `background` execution for Stryker. Run verification tests upfront. For multi-file Stryker, run each file individually with `--mutate` flag. |
| **Label refresh necesario** | Jules no detecta issues nuevas tras 1h | Toggle label: remove + re-add. Ver `references/label-refresh-and-pr-noise.md` |
| **Label `wave-N`/`jules` inexistente en el repo destino** | `gh issue create --label wave-3` falla con `could not add label: 'wave-3' not found`; `gh issue edit <N> --add-label jules` falla SILENCIOSO con `failed to update 1 issue` → el issue se crea pero nunca llega a Jules | Los labels NO se heredan entre repos. Verificar/crear ANTES: `gh label list --repo iberi22/<repo> --limit 50 \| grep -E "jules\|wave-3"`; crear con `gh label create jules --repo ... --color 5319E7 --description "Delegable to Jules agent"`. Post-dispatch confirmar: `gh issue view <N> --json labels --jq '[.labels[].name]'` debe contener `jules`. (Real: Wave-3 Ago 2026, 3/4 dispatchados OK + 1 fallido silencioso) |

> 📎 Referencias: `references/xavier-980-template.md` (template canónico), `references/wave10-validated-template.md` (template validado en Wave 10, aceptado por el usuario), `references/session-failure-patterns.md`, `references/label-refresh-and-pr-noise.md`

## 📋 Prompts Xavier-Especificos para Agentes Especializados

Para agentes recurrentes (Sentinel, Bolt, Palette), existen prompts codebase-specific en el skill `jules-async-orchestration`:

| Rol | Prompt | Contiene |
|-----|--------|----------|
| 🛡️ Sentinel | `jules-async-orchestration/references/prompts-sentinel.md` | Rust security patterns, SSRF, command injection, unwrap audit |
| ⚡ Bolt | `jules-async-orchestration/references/prompts-bolt.md` | spawn_blocking, serde perf, RwLock contention, benchmarks |
| 🎨 Palette | `jules-async-orchestration/references/prompts-palette.md` | Tailwind a11y patterns, loading states, empty states, focus |

**Siempre usar estos prompts en vez de templates genéricos.** Contienen comandos reales que funcionan, paths del codebase, y patrones de código Xavier. NO copiar prompts de proyectos TypeScript/React genéricos.

## Post-Completion Verification

Después de que el agente completa:
- [ ] `jules remote list --session` (o equivalente)
- [ ] Buscar branches nuevas en origin
- [ ] Buscar PRs creados
- [ ] Si "Completed" sin cambios → verificar manualmente, actualizar features.json
- [ ] Verificar que features.json refleja el progreso real
