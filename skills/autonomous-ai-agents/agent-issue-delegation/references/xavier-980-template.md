# Xavier #980 — Canonical Issue Template

**Repo:** iberi22/xavier (Rust)
**URL:** https://github.com/iberi22/xavier/issues/980

This is the canonical template format for all SWAL project issues. Every section is mandatory.

## Template

```
# [Wave N.XX] feat-feature-id — Human-readable Title

> Wave N — [Foundation/Infra/Core/Polish].
> Label: `ola{N}`, `wave-{N}`

---

## Current State (MEDIBLE)
- File: `path/to/file.rs` (N lines, last modified YYYY-MM-DD)
- Current behavior at line XX: `exact code snippet`
- Feature: `feat-xxx` at N% in `.gitcore/features.json`
- Reference impl: [link to existing similar feature]
- Benchmark data if applicable: `metric improved from X to Y (+Z%)`

## Desired State (DELTA)
- **Section A** (lines XX-YY): Change [exact behavior]
- **New method** `fn_name()`: Implement [signature and behavior]
- **New file**: `path/to/new.rs` with [purpose]

## Web Research Required
1. `search: "topic best practices 2026"`
2. `search: "alternative approach comparison"`
3. `search: "library documentation latest"`
4. `search: "related implementation patterns"`

## Exact Technical Context
- File: `path/to/file.rs`
  - `fn_a()` at line XX — entry point, accepts [params], returns [type]
  - Method at line YY — current implementation detail
- Struct: `TypeName` at line ZZ — fields: [a, b, c]
- Related struct: `OtherType` — how it connects
- ⚠️ CRITICAL: [stack-specific gotchas, path conventions, column ordering, etc.]

## Problem
[2-3 sentences. What breaks without this? Why does it matter now?]

## Acceptance Criteria (VERIFIABLE)
- [ ] `grep -c "pattern" path/to/file.ext` returns N
- [ ] Stack lint passes: `cargo clippy ...` / `dart analyze lib/`
- [ ] Stack tests pass: `cargo test ...` / `flutter test ...`
- [ ] `cargo check --workspace` 0 errors / `dart analyze lib/` 0 errors
- [ ] E2E: [curl command or manual test step with expected output]
- [ ] `.gitcore/features.json` → `feat-xxx: 100%`

## Files to Modify
| File | Current State | Change | Risk |
|------|--------------|--------|------|
| `path/to/file.ext` | N lines, N funcs | [specific change] | LOW/MED/HIGH |
| `.gitcore/features.json` | feat-xxx at N% | Update to 100% | LOW |

## DO NOT touch (Anti-Regression)
- [explicit paths, other modules, sibling features]
- NO create .patch, .py, .txt loose files
- Revert Cargo.toml noise if agent adds lints: `git checkout origin/main -- Cargo.toml`

## Anti-Hallucination Guard ⚠️
1. Verify file exists before assuming path: `ls path/to/existing.file`
2. Path conventions: SRC.md → `.gitcore/`; features → `.gitcore/features/`
3. No invent APIs — only implement existing types/interfaces
4. Double-check column order for SQL/table operations
5. Stack verification: read manifest file before using commands

## Verification
```bash
# Stack-appropriate commands
CARGO_TARGET_DIR=/tmp/rt cargo check --workspace 2>&1 | tail -5
cargo test -p xavier --lib module 2>&1 | tail -10
python3 -c "import json; d=json.load(open('.gitcore/features.json')); print([f['id']+'='+str(f['progress_pct'])+'%' for f in d['features'] if f['progress_pct']<100])"
```

## Dependencies & Merge Order
- **Depends on:** #N | **Blocked by:** #M | **Parallel:** #P
- **Merge order:** 1 (foundation) → 2 (features) → 3 (tests) → 4 (docs)
- **Effort:** Small (<1h) / Medium (1-4h) / Large (4h+)

## Failure Recovery
| If this happens | Action |
|----------------|--------|
| `cargo check` fails | Fix imports, do NOT commit broken code |
| File not found | Run `find . -name "filename" 2>/dev/null` |
| Test fails | Fix or document wrong assumption |
| PR conflicts | Rebase on main, re-run verification |
| Manifest modified | `git checkout origin/main -- Cargo.toml` |
```

## Key Differences from Generic Templates

| Element | Generic Template | Xavier #980 Format |
|---------|-----------------|-------------------|
| Title | `Feature X to 100%` | `[Wave N.XX] feat-xxx — Title` |
| Current State | Qualitative | **MEDIBLE** with line numbers, file sizes, exact code snippets |
| Problem section | Missing | **2-3 sentences** explaining the problem |
| Web Research | 1 generic link | **4+ specific search queries** |
| Exact Technical Context | File+lines | **Struct/class definitions**, function signatures, **CRITICAL gotchas** |
| Acceptance Criteria | Generic | **grep commands** with expected counts, **E2E curl commands** |
| Failure Recovery | Missing | **Table** of failure scenarios + actions |
| DO NOT touch | 1-2 items | **Explicit exclusion list** + manifest revert instructions |
