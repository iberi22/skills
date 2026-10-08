# Merge conflicts, stale bases, post-merge breakage

## Parallel PRs touching shared files

Parallel Jules PRs often conflict on files they all regenerate or update. Two cases:

- **Generated files** (lockfiles, generated plugin lists): every PR regenerates them, so they conflict on each merge. Resolve by taking one side, then regenerating with the project's tool (`pub get`, `npm install`, and so on), and commit. Which side you take does not matter for generated content.
- **Progress or index files** (for example, a features or progress JSON that each PR updates): take main's version during a rebase (`--ours` is the base branch during rebase), then apply your own update again. Do not keep both sides by hand.
- **Source code**: never resolve by taking one side wholesale. Resolve by hand or send the PR back to Jules with the conflict described.

Merge with a merge commit, not a force-push rebase. A merge keeps the push fast-forward and avoids history rewrites that some setups block.

```bash
gh pr checkout <num> --force
git merge origin/main --no-commit
git checkout --ours -- <generated-files>     # during merge, --ours is the PR branch; then regenerate
git add <generated-files>
git commit --no-edit
git push origin <branch>
sleep 3 && gh pr merge <num> --merge
```

## Stale-base recovery

A PR created from an old base can reintroduce a regression that main already fixed. Symptom: the diff reverts a merged change (for example, a type fix or a process-handling change).

```bash
git fetch origin pull/<num>/head:pr-<num>
BASE=$(git merge-base main pr-<num>)
git rebase --onto main "$BASE" pr-<num>     # drops commits already in main; keeps only the PR's own changes
git diff main..pr-<num> --stat              # confirm the expected files only
git diff main..pr-<num> -- <sensitive-file> | grep -c "<regressed-pattern>"   # must be 0
```

Do not apply when the PR touches areas main changed incompatibly (large refactors, renamed APIs). Close it and relaunch on the current base.

Close without merging, with a note, when the diff reverts several merged PRs at once. Relaunch with the current base SHA in the brief.

## Post-merge breakage (generic)

After a batch merges, a branch can compile and still fail tests. Recurring causes:

1. **Codegen not run.** A PR added schema or table definitions without regenerating derived code. Run the generator (for example, `build_runner` in Dart/Drift) and commit the result as your own commit.
2. **Toolchain constraint inflated.** An upgrade PR raised the SDK or language constraint above the local toolchain. Compare the constraint with the installed toolchain version; revert the constraint if the local toolchain is older.
3. **Dependency injection missing in old tests.** A PR made a widget or service read a provider or DI container that old tests do not set up. Wrap those tests in the container.

After any post-merge fix: run the full test suite before committing. Merged Jules PRs are merge commits; put post-merge fixes in a separate commit on main.

## Scope mismatch (dangerous PRs)

Red flags in a PR whose title and diff disagree:
- Title says one small thing (for example, "add labels to close buttons"), diff is thousands of lines.
- Diff removes dependencies or rewrites unrelated components.
- Formatting or tooling changes mixed with functional changes.

Check: `gh pr diff <num> --stat | tail -1` and `gh pr diff <num> --name-only`. Decision: skip, leave a comment explaining why, and do not merge. If the scoped part is valid, rescue only that part (§8 of `SKILL.md`) into a new PR.

## Log and changelog conflicts

When several PRs append entries to the same log file, keep all entries from both sides. Never drop another PR's entry. Resolve by hand: remove the conflict markers and keep both blocks.

For a source file where a newer PR already contains the same change: take main's version of that file (`git checkout main -- <file>`), commit, and move on.

For a dependency-manifest conflict: keep the union of intended changes. Prefer the side with fewer unrelated changes, then add the other side's intended change by hand.

## Do not skip conflicting PRs

Leaving one PR unresolved causes cascading conflicts for the rest of the batch. Resolve it, or close it and relaunch. Resolve in dependency order (fewest dependencies first).

## Branch cleanup after a wave

| Branch | Has a PR? | PR merged? | Action |
|---|---|---|---|
| Yes | Yes | Yes | Delete the remote branch |
| Yes | Yes | No, clean | Review and merge first |
| Yes | Yes | No, stale base | Close the PR without merge |
| No | — | — | If it deletes merged work, delete it without merging. If clean, open a PR or delete |

Audit: `git fetch origin --prune`, then list remote branches by recent commit date.

Duplicate issues: when a feature was tracked in an earlier wave and again in this one, close the older issue with a pointer to the newer one. Finish with zero open issues carrying the trigger label without a PR or a decision.

## Duplicate fixes

Agents re-discover fixes already on main. Before approving or merging a fix that touches one file, check the file's recent commits and closed PRs for the same change. A closed-as-duplicate PR is a signal to check the brief sent to the agent.
