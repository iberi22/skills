# Label Refresh Trick & PR Noise Patterns

> From Ola 8 Wave 1 (2026-07-21): 14 parallel issues dispatched to Jules.

## Label Refresh Trick

**Problem:** After closing old issues and creating new ones with the `jules` label, Jules doesn't detect the new issues for 1+ hour. They sit undetected while old "Paused" sessions from closed issues saturate Jules's session pool.

**Solution:** Toggle the label off and back on:

```bash
# Remove label from all issues
for n in ISSUE_NUMBERS; do
  gh issue edit $n --remove-label jules
done

sleep 3  # Brief pause for GitHub to propagate

# Re-apply label
for n in ISSUE_NUMBERS; do
  gh issue edit $n --add-label jules
done
```

After the label refresh, Jules detects ALL issues within ~30 seconds (not the previous 1+ hour delay).

**Why it works:** Jules's issue scanner caches which issues it has already seen with the `jules` label. Removing and re-adding the label resets this cache, forcing a fresh scan.

## PR Noise Patterns

When Jules completes a session, ALWAYS review the PR diff for these extra changes:

| Extra Change | File | What It Is | Action |
|-------------|------|-----------|--------|
| `[lints.clippy]` section added | `Cargo.toml` | Jules auto-generates clippy allows to pass CI | Discard: `git checkout origin/main -- Cargo.toml` |
| `autobenches = false` | `Cargo.toml` | Benchmark config noise | Discard |
| Bench section removed | `Cargo.toml` | Jules removes `[[bench]]` entries | Restore from origin/main |
| `#![allow(unused_imports)]` | bench files | Jules silences warnings instead of fixing | Evaluate: keep only if genuinely unused |
| `let _state` rename | Any `.rs` file | Jules renames unused variables | Evaluate: acceptable if intentional |
| Assert threshold change | Test files | Jules changes assertion values (e.g., `>= 16` → `>= 12`) | ⚠️ VERIFY: may indicate tools changed |
| `.gitcore/ola8-progress.json` (shared) | Root | Old shared progress file format | **Do NOT merge** — should be per-feature files under `ola8-progress/` |

**Safe changes (accept without review):**
- New file under `.gitcore/ola8-progress/<feature-id>.json` — this is the intended output
- File verification (`ls path/` style) — Jules confirms paths exist

## Batch Merge Workflow

```bash
# 1. List open PRs
gh pr list --state open --json number,title,headRefName

# 2. Mark all as ready (Jules creates them as drafts)
for pr in PR_NUMBERS; do gh pr ready $pr; done

# 3. Merge all (safe because each touches different files)
for pr in PR_NUMBERS; do
  gh pr merge $pr --squash --subject "feat(Wave): description"
done

# 4. Pull merged state
git fetch origin main && git pull origin main
```
