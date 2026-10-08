# Wave 10 Validated Issue Template

> This template was used for issues #70-#74 and was explicitly confirmed by the user as correct.
> ALL sections are mandatory. Issue MUST be in English.

## Template Structure

```markdown
# [WAVE-N.PX] Short Title — Descriptive title

> Wave N — [Category]. Parent epic: #EPIC.
> Label: `jules`, `wave-N`

---

## Current State (MEDIBLE)

[HARD data — file paths, line counts, mutation %, test counts]
- File: `path/to/file.ts` (N lines, key functions)
- Feature/metric: status at N%
- Test file: `test/file.test.ts` (N tests, status)

## Desired State (DELTA)

[What needs to happen — bullet points with specific targets]
- Run [tool] targeting [file]
- If score < N%: add tests to reach > N%
- Report final score

## Web Research Required

**MANDATORY**: Search BEFORE implementing. 3 queries minimum.
1. search: "[specific query 2026]"
2. search: "[alternative/library comparison]"
3. search: "[documentation/exact approach]"

## Exact Technical Context

- File: `path/to/file.ts` — class/method description
- Key methods: [list with brief description]
- ⚠️ CRITICAL: [time estimates, known blockers]
- [Tool name] takes ~N minutes per file. Use background execution.

## Problem

[2-3 sentences: what problem this solves]

## Acceptance Criteria (VERIFIABLE BY COMMAND)

- [ ] Verification command example | expected output
- [ ] `npx vitest run test/file.test.ts` | passes
- [ ] `npx tsc --noEmit` | 0 errors
- [ ] Score reported in issue comment

## Files to Modify

| File | Current State | Change | Risk |
|------|--------------|--------|------|
| `test/file.test.ts` | N tests | ADD tests if needed | LOW |
| `src/file.ts` | N lines | DO NOT MODIFY | — |

## DO NOT touch (Anti-Regression)

- [source files — tests only]
- `features.json` (handled at wave reconciliation)

## Anti-Hallucination Guard ⚠️

1. Run verification FIRST before making any changes
2. Only add code if threshold is not met
3. Do NOT modify source files — testing only
4. If tool times out, report partial results

## Verification

```bash
# 1. Verify existing tests pass
npx vitest run test/file.test.ts | tail -3

# 2. Run verification tool (takes ~N min)
npx verified-tool --mutate src/file.ts | grep "expected"

# 3. Verify TypeScript
npx tsc --noEmit
```

## Dependencies & Merge Order

- **Depends on:** None | **Parallel with:** #N (different file islands)
- **Merge order:** N | **Expected effort:** Small/Medium/Large

## Failure Recovery

| If this happens | Action |
|----------------|--------|
| Tool times out | Kill process, report partial results |
| Threshold already met | Report success, no changes needed |
| Tests break | Revert additions, keep only passing ones |
```

## Real Example: Issue #70 Body

The following was the actual body for issue #70 (edge-mesh-client Stryker mutation) and was accepted by the user:

```
# [W10-P1] Stryker Mutation: edge-mesh-client.ts — Verify score > 80%

> Wave 10 — Cleanup. Parent epic: #69.
> Label: `jules`, `wave-10`

---

## Current State (MEDIBLE)

- File: `src/services/mesh/edge-mesh-client.ts` (~300 lines, core P2P mesh client)
- Test file: `src/services/mesh/__tests__/edge-mesh-client.test.ts` (924 lines, 48 tests)
- Mutation score: 26.60% last verified (79 killed, 128 survived, 90 no-coverage)

## Desired State (DELTA)

- Run Stryker mutation test targeting ONLY edge-mesh-client.ts
- If score < 80% on covered code: add tests to reach > 80%
- Report final score in issue comment

## Web Research Required

1. search: "vitest stub edge-mesh-client WebRTC mock peerjs 2026"
2. search: "stryker-mutator mutation score improve typescript patterns 2026"
3. search: "equivalent mutant stryker ignore comment pattern"

## Exact Technical Context

- EdgeMeshClient class with methods: constructor, joinRoom, leaveRoom, subscribe, getCrdtEventBus, getCrdtMemoryStore, getPeers, destroy, getStatus
- Test file already exists with 48 tests
- Uses WebRTC/PeerJS internally
- ⚠️ Stryker takes ~6-7 minutes per file. Use background execution.

## Problem

The edge-mesh-client.ts file has very low mutation coverage. Despite 48 tests existing, the mutation score is only 26.60% — meaning most mutants survive.

## Acceptance Criteria (VERIFIABLE BY COMMAND)

- [ ] `npx stryker run --mutate src/services/mesh/edge-mesh-client.ts | grep "All files"` shows > 80%
- [ ] All existing tests still pass: `npx vitest run src/services/mesh/__tests__/edge-mesh-client.test.ts`
- [ ] `npx tsc --noEmit` passes

## DO NOT touch (Anti-Regression)

- `src/services/mesh/edge-mesh-client.ts` (source file — tests only)
- `features.json` (handled at wave reconciliation)

## Verification

```bash
npx vitest run src/services/mesh/__tests__/edge-mesh-client.test.ts | tail -3
npx stryker run --mutate src/services/mesh/edge-mesh-client.ts | grep "All files"
npx tsc --noEmit
```
```

## Key Validation Rules

1. **ALL sections required** — no compaction. If you skip a section, the user will correct you.
2. **English only** — issues, docs, code comments must be English.
3. **Web Research Required** is non-negotiable. The user explicitly said "debe de sugerir siempre buscar en la web el enfoque mas actualizado."
4. **Acceptance Criteria must be verifiable by command** — `grep`, test runner, linter. Not opinions.
5. **Anti-Hallucination Guard** prevents agents from modifying source files or creating files in wrong locations.
6. **Failure Recovery** table gives the agent a plan when things go wrong.
