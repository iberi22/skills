# Session Failure Patterns — Ola 8 Wave 1 (2026-07-21)

## Core Discovery: Jules Handles 14 Parallel Issues

Jules detects and runs ~14 issues simultaneously. The old "1 label at a time" rule was a workaround for shared-file merge conflicts, not a Jules limitation.

**If each issue writes to a different file, 14 PRs can merge in any order with zero conflicts.**

## The Shared File Trap

Every feature writes to `.gitcore/features.json`. This single shared file:
- Forces sequential execution (1 issue → merge → next issue)
- Creates merge conflicts on every parallel PR
- Wastes Jules capacity

### Solution: Per-Feature Progress Files

Each issue writes to its OWN file under `.gitcore/ola8-progress/<feature-id>.json`:

```
.gitcore/ola8-progress/
├── feat-unified-storage.json     ← Issue A only (no conflict)
├── feat-belief-graph.json        ← Issue B only
├── feat-mcp-server.json          ← Issue C only
└── ...                           ← 11 more, all independent
```

**Do NOT use `.gitcore/ola8-progress.json` (shared file).** Two parallel PRs both creating/modifying this file WILL conflict.

At wave end, a reconciliation issue reads all `ola8-progress/*.json` files and merges into `features.json`.

## Failure Mode Analysis

### Issues That Failed

| Issue | Pattern | Root Cause |
|-------|---------|------------|
| feat-encryption+security (combined) | Multi-feature in one issue | Jules handles ONE feature per session. Split always. |
| feat-documentation-site (full template) | Complex: verify + modify + update | Too many action items. Single action only. |
| feat-encryption-at-rest (simple retry) | Verify + update single file | Path mismatch on remote VM. Add exact `ls` command. |

### Issues That Succeeded

| Issue | Pattern | Why |
|-------|---------|-----|
| feat-hybrid-search | Medium complexity, clear delta | Had exact paths + test names |
| feat-unified-storage | Simple: verify path + create file | Single action, single file |
| feat-documentation-site (retry) | Simple: verify path + create file | Same pattern, worked on retry |
| feat-security-hygiene (retry) | Simple: verify path + create file | Same pattern, worked on retry |

### Key Insight: 90%+ Success Formula

```
ISSUE = 1 feature + 1 file to CREATE + 0 existing files to MODIFY
```

No code changes, no features.json, no Cargo.toml. Just verify path exists + create progress file.

## PR Noise Pattern

When Jules succeeds, REVIEW every PR for extra changes:

| Extra Change | What It Is | Action |
|-------------|-----------|--------|
| Cargo.toml adds [lints.clippy] | cargo auto-generated | Discard: git checkout origin/main -- Cargo.toml |
| Cargo.toml adds autobenches=false | Benchmark config | Discard |
| .gitcore/ola8-progress.json (shared) | Old shared format | Close PR, create per-feature file manually |
| .gitcore/features/FEATURE-*.md edit | Feature doc improvement | Accept if clean |

## Label Refresh Trick

When Jules doesn't detect new issues (old sessions in "Paused" saturate the pool):

```bash
# Issues sit undetected for 1+ hour despite having the jules label
# Solution: toggle the label
for n in ISSUE_NUMBERS; do gh issue edit $n --remove-label jules; done
sleep 3
for n in ISSUE_NUMBERS; do gh issue edit $n --add-label jules; done
```

Jules re-scans within 30 seconds and detects all issues. Without this trick, new issues can sit idle for hours.

## The 14-Issue Batch Template

For verify-only tasks, use this minimal template instead of the full one:

```
# [WR-NN] <feature-id> -- verify paths + create progress file

Epic: #EPIC · Wave: N · File island: <path>
Label: ola{N} wave-{N}

## Current State
- Feature Reality Scan: N% real
- Path to verify: <path>

## Solo Action
1. Verify that <path> exists
2. Create .gitcore/ola8-progress/<feature-id>.json with single JSON line

## Acceptance Criteria
- ls <path> exists
- .gitcore/ola8-progress/<feature-id>.json exists
- cargo check -p xavier 0 errors
- cargo clippy -p xavier --all-targets -- -D warnings 0 errors

## DO NOT touch
- .gitcore/features.json (reconciled at end)
- Any .rs file
- Cargo.toml

## Effort: <5 min
```

## Dispatch Procedure

```bash
# 1. Create 14 issues with template above
# 2. Verify file islands are disjoint
# 3. Apply jules label to ALL 14 simultaneously
for n in ISSUE_NUMBERS; do gh issue edit $n --add-label jules; done
# 4. Monitor: jules remote list --session | grep "WR-"
# 5. As PRs arrive: review → accept only progress file → merge
# 6. All 14 merged → reconciliation reads all ola8-progress/*.json
```

## Recovery

Close failed issue → split into singles → add exact paths + inline JSON → verify file islands → re-apply label.
