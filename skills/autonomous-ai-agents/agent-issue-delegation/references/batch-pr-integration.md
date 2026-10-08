# Batch PR Integration — Wave Merge Protocol

> Added: 2026-07-22 (Wave 1, isar_agent_memory)
> Context: Jules now pushes directly to GitHub and creates PRs as DRAFT. No teleport needed.

## PR Lifecycle

```
Jules completes → PRs on GitHub (DRAFT)
    ↓
Mark ready: `gh pr ready <N>`
    ↓
Merge safe (docs/CI/release, <100 lines)
    ↓
Resolve features.json conflicts (extract files, commit direct)
    ↓
Rebase complex PRs (shared models)
    ↓
Final verification
```

## Commands

### List PRs
```bash
gh pr list --repo owner/repo --state open --json number,title,additions,deletions,mergeable
```

### Draft → Ready
```bash
gh pr ready <N> --repo owner/repo
```

### Merge safe PRs (docs/CI/release — never conflict)
```bash
gh pr merge <N> --repo owner/repo --merge --delete-branch --admin
```

### Resolve features.json conflict
Parallel PRs all modify `.gitcore/features.json` → guaranteed conflict.

**Fix:** extract unique files from each PR branch, commit directly to main:

```bash
git fetch origin <pr-branch>
git show FETCH_HEAD:test/new_test.dart > /tmp/new_test.dart
git checkout main
cp /tmp/new_test.dart test/new_test.dart
git add test/new_test.dart && git commit -m "tests: feature description"
git push origin main --force
```

Close orphaned PRs afterwards. Force push safe when sole committer.

### Rebase complex PRs (shared models, interfaces)
```bash
gh pr checkout <N>
git merge main
git checkout --theirs path/to/conflicted/file
git add -A && git commit -m "Merge main: resolve conflicts"
git push origin HEAD
gh pr merge <N> --repo owner/repo --merge --admin
```

### Final verification
```bash
git checkout main && git pull origin main --ff-only
dart analyze lib/   # Dart
cargo check          # Rust
gh pr list --repo owner/repo --state open  # must be empty
```
