# Session Failure Patterns & Parallel Execution Design

> Derived from Ola 8 Wave 1 (Julio 2026). 14 issues dispatched, 14 completed, 99.4% real.

## What Worked

### Single-Action Issues = 100% Success Rate
WR1-01 to WR1-14: "verify + update progress file" — 14/14 completadas.
Cada issue = UNA acción: verify path exists + create progress file.

### Per-Feature Progress Files = Zero Merge Conflicts
.gitcore/ola8-progress/feat-<feature-id>.json — each PR touches its own file.

### Label Refresh Technique
When Jules stops detecting new issues (old "Paused" sessions):
1. Remove label: gh issue edit $N --remove-label jules
2. Wait 3s
3. Re-apply: gh issue edit $N --add-label jules

## What Failed
- Multi-feature issues (2+ features in 1 issue) = 0% success
- Cargo.toml noise: Jules adds [lints.clippy], autobenches — discard always
- Shared ola8-progress.json: two PRs creating same file = conflict

## Wave Reconciliation Flow
1. Merge all PRs (gh pr ready + gh pr merge)
2. Read .gitcore/ola8-progress/*.json, unify into features.json
3. Run xavier verify features
4. Close issues and EPIC
5. Push
