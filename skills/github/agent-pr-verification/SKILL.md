---
name: agent-pr-verification
version: 1.0.0
description: 'Use when merging agent PRs: verify in isolation first.'
---

# Agent PR Verification — merge autonomous-agent PRs without regressions

For PRs opened by autonomous coding agents into a repo with an active
main: verify in isolation, repair agent-side defects in the PR branch,
merge in dependency order with green gates. Never trust the PR body;
trust commands run against the PR content.

## Procedure

1. **Isolate**: `git worktree add /tmp/wx-<n> origin/main`, checkout the
   PR branch there, symlink (never copy) the monorepo `node_modules`.
   Keep main clean; all repair commits go to the PR branch.
2. **Deletion sweep**: `git diff <base>...<branch> --name-status | grep ^D`.
   Agent branches fork from a stale base and silently delete files merged
   by sibling PRs. Restore every unexpected deletion from the base before
   any other work — a merge applies deletions exactly like additions.
3. **Revert check**: review every `M` hunk for stale-base reverts of
   already-merged work (adapter pins, wiring, config flags). Restore the
   merged version, then re-apply only the PR's legitimate additions.
4. **Targeted verification**: run the checks the issue promised (unit
   tests for the island, validator/CLI on real fixtures, `astro build`
   for page changes, Playwright spec for UI). Prefer the repo's canonical
gates over the PR's claims.
5. **Fix forward in the PR branch**: repair blockers with minimal
   commits on the PR branch (restore deletions, revert reverts, keep
   additions). Never fix by editing main around the PR.
6. **Push-before-merge**: read the push output. If it fails (wrong branch
   name, non-fast-forward), diagnose and re-push — merging without the
   fix commit ships the broken version, because merge operates on the
   remote branch, not your worktree.
7. **Merge in wave order**, then delete the worktree. Close the loop:
   reconcile feature tracking, run the full gate on main.

## Pitfalls

- Commit or stash before `gh pr checkout -B`: it force-moves the branch
  pointer and silently discards uncommitted fixes in the worktree.
- A green build in one worktree proves nothing about another: symlinked
  `node_modules` are shared, but per-worktree state (dist/, dev servers,
  ports) is not — rebuild and re-run gates after every branch switch.
- `pkill -f <pattern>` matches your own command line when the pattern
  appears in it; use a regex variant that cannot match literally.
- Evidence screenshots committed by agents live wherever the spec wrote
  them; unexpected binary churn in `git status` after a green run means a
  spec writes captures into the source tree instead of `test-results/`.
- Mixed-manager repos (npm + pnpm lockfiles, only one tracked) hide
  version pins: a clean reinstall can expose a latent adapter/framework
  incompatibility the old tree masked. When a previously-green build
  breaks after reinstall with a missing-export error, diff resolved
  versions first, then pin the compatible minor in the tracked manifest.
