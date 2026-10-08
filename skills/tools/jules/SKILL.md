---
name: jules
description: Use when delegating a coding task to Google Jules (async cloud coding agent, via REST API v1alpha or the jules CLI), or when monitoring, rescuing, or merging the pull requests it opens.
version: "6.0.0"
updated: "2026-10-08"
---

# Jules

Jules is an asynchronous coding agent. It clones a repo into a VM, works on one task, and opens a draft PR. A human or a local agent reviews and merges. Jules receives no secrets and does not deploy.

This file holds the decisions and the order of operations. Long material is in `references/`.

## 1. Route: is Jules the right executor?

Use Jules for bounded tasks with a checkable deliverable: a fix, a feature slice of 2–7 files and about 50–1000 changed lines, unit tests, content, dependency bumps. TS/JS and small, file-scoped Rust changes fit best. Choosing among inline work, subagents, local runs, and Jules across all tools belongs to the `llm-routing` skill.

Do not send Jules:

| Task | Why |
|---|---|
| Refactor or decoupling across a large multi-crate workspace | High FAILED rate; the VM cannot build it in time |
| "Make the whole suite green" or any open-ended goal | Sessions stop to ask questions and stall |
| Standing persona or agent prompts with no concrete deliverable | Low merge rate |
| Work needing credentials, deploys, or real data | Jules has no secret store (§10) |
| Native or cross-compile work (BLE, NFC, FFI, Gradle/Xcode) | The sandbox cannot run it |
| Merging or rebasing other branches | Keep that local (§7) |
| DevOps or infrastructure changes (NixOS, CI pipelines, deploy config) | Often stuck in PLANNING; do locally |
| Complex multi-widget UI changes in one task | Incomplete PRs or wrong scope; split or do locally |
| Repos your local runner marks as blocked for Jules | Route local |

## 2. Interfaces

- **REST API v1alpha** (`https://jules.googleapis.com/v1alpha`): dispatch, bulk status, replies. Header `x-goog-api-key`, one key per account. Details: `references/api.md`.
- **`jules` CLI**: `new`, `remote list --session|--repo`, `remote pull [--apply]`, `teleport`, `login`, `logout`. There is no cancel, close, or delete command. Details: `references/cli.md`.
- Dispatch through the wave tooling your environment provides. If you call the API by hand, always send `automationMode: "AUTO_CREATE_PR"` with `sourceContext.githubRepoContext.startingBranch` set. Without it, sessions can finish COMPLETED with code and no PR.
- The GitHub label trigger (`jules` label on an issue) is a legacy path. Do not mix it with API dispatch for the same task: it creates duplicate sessions. If you must use labels: create every issue without the trigger label, add it only to the first issue in merge order, and add the next one after each merge.
- Jules only sees repos connected to the account. Confirm with `jules remote list --repo` or `GET /sources` before dispatch.

## 3. Capacity before dispatch

- Each account has a concurrent-session limit and a daily session limit. Values depend on the plan. The vendor usage page, as reported in 2026-07, listed Free 3 concurrent / 15 per day, Pro 15 / 100, Ultra 60 / 300; re-verify before relying on it.
- A session occupies a slot in every non-terminal state: `QUEUED`, `PLANNING`, `AWAITING_PLAN_APPROVAL`, `AWAITING_USER_FEEDBACK`, `IN_PROGRESS`, `PAUSED`. Counting only `IN_PROGRESS` undercounts badly.
- Going over the concurrent limit is accepted: extra sessions wait in `QUEUED`. Report how many were queued.
- Count with paginated `GET /sessions` (script in `references/api.md`). Use at most 4 parallel reads; 8 parallel reads returned 429.
- Capacity is rarely the bottleneck; brief quality is. Dispatch fewer, better-scoped tasks.

## 4. Wave workflow

1. **Plan islands.** Each task owns a disjoint file set. Include every file a task touches, not only its primary file: two tasks with different primary files still conflict if both edit a shared shell or wiring file. Give each shared wiring file to exactly one task; the others list it under "do not touch" and note the integration point. Fix the merge order before dispatch.
   - Sequence new modules as: scaffolding first, then types, then implementations, then tests, then integration. A shared index or progress file is touched only by the last task.
2. **Write complete briefs** (one file per task) before any dispatch. Check that each brief has: deliverable, file table, a pattern to copy, decisions made in advance, a verification command, prohibitions, and a closing instruction (§5). Fix incomplete briefs before dispatch, not after.
3. **Probe.** Dispatch one session first in any new, heavy, or recently changed repo. If it fails during VM setup, fix the environment (§9) before spending the wave.
4. **Dispatch** 5–8 sessions per repo per wave. The title (first line of the brief) is the idempotency key: never re-dispatch the same title by hand.
5. **Monitor** (§6). Review PRs before issues.
6. **Gate and merge** in merge order (§7). Rescue failures (§8).
7. **Close the wave** (§11).

## 5. Brief template

Measured levers: name the target branch for the PR, tell Jules to finish with defaults instead of asking, give only light verification, and list prohibitions. Length alone was not the cause of failures in the measured data. If a brief keeps failing, check the environment (§9) first, then trim it to exact paths, signatures, and snippets.

```markdown
# [<wave>.<NN>] <type>: <observable result in one line>

## Deliverable
<1–3 sentences: what exists or changes; measurable.>

## Files (this task's island)
| File | Change |
|---|---|
| `path/a.ts` | modify: … |
| `path/a.test.ts` | create: … |
Do not touch files outside this table, except new tests. Do not touch lockfiles unless the task is about dependencies.

## Context you cannot guess
- Pattern to copy: `path/existing.ts` (why).
- Facts: real paths, names, versions, API contract.

## Decisions already made (do not ask)
- If <predictable ambiguity> → use <default>. Note it in the PR.
- If something in the spec is missing from the repo → implement the minimum coherent version and explain it in the PR.
- If a command fails because of the environment (network, toolchain, browser) → document it in the PR and continue.

## Verification (light: runnable in the sandbox)
`<test command for the touched module>`
Do NOT run the full build, the full E2E suite, or release builds. CI verifies, on the PR.

## Prohibited
- Disabling rules or tests to pass (`eslint-disable`, `#[allow]`, `.skip`, lowering thresholds).
- Asking for or using credentials. Deploying.

## Closing
Do not ask for confirmation at any point. When done: commit and open the PR against `<branch>`. PR body: files changed, commands run and their results, open items as `item | cause`.
```

## 6. Monitoring and state actions

| State | Action |
|---|---|
| `QUEUED`, `PLANNING` | Wait. No change for more than 10 min: check connectivity and repo size. |
| `IN_PROGRESS` | Wait. Do not close the issue as "stuck"; there is no cancel. |
| `AWAITING_PLAN_APPROVAL` | Approve (`:approvePlan`). Keep `requirePlanApproval` false unless plan review saves real work: this state holds a slot. |
| `AWAITING_USER_FEEDBACK` | §6.1 |
| `PAUSED` | Archive at wave close. |
| `COMPLETED` | Check the PR outcome (`references/monitoring.md`). No PR and no patch = false positive. |
| `FAILED` | Rescue (§8). Do not retry blindly. |

When the CLI list and the API disagree, trust the API state and the paginated activities.

Sessions that look stuck often finish late. Close an issue as failed only when the session is `COMPLETED` or `FAILED` and there is no PR.

### 6.1 AWAITING_USER_FEEDBACK

Triage in this order:
1. Read the session state from the API.
2. Paginate its activities to the end. They are oldest-first; the newest page is last.
3. The last `agentMessaged` is the pending question. If the last activity is `planApproved`, `artifacts`, or `progressUpdated` with no question, there is nothing to answer.

If there is a real question, answer once, with a decision and a closing instruction:
`Use <default>. Do not wait for more confirmation: commit and open the PR against <branch> now; put open items in the PR body.`

If the session already produced artifacts but sits in AWAITING with no question:
`The change is approved. Finish, run the lint and tests, and open the PR. If you already did, confirm the status.`

Rules:
- Before approving any proposed fix, check main and closed PRs for an existing fix. Agents re-discover merged fixes.
- A "?" inside a progress report is not always a question. Read the whole last message; if it is a technical doubt, verify the claim before answering.
- Two or more agents stuck in AWAITING at the same time with no PRs usually means a shared gate, not individual abandonment. Escalate to a person in one batch (`monitoring.md`).
- Technical questions about the environment (missing module, error that does not reproduce on main): verify on the real repo first. If the error is sandbox-only, say so and tell the agent to validate only its own file. Do not let it stub dependencies that resolve on main.
- At most one reply per session. If there is still no PR after it, `patch` the session, integrate by hand, and archive it.
- Replies use `:sendMessage` with exactly `{"prompt": "<text>"}`. Other field names return 400. The state changes to `IN_PROGRESS` within about 10–20 s; do not resend.

## 7. Gate PRs before merge

```bash
gh pr view <url> --json state,files,additions,deletions
gh pr checks <url>
```

1. **Empty-PR gate.** At least one non-lockfile file, all inside the task's island. Lockfile-only or empty: rescue the code (§8) and close the PR with a note.
2. **Scope gate.** Compare the diff size and file list with the stated scope. Skip or close PRs whose diff has unrelated changes: dependency removals, rewrites of unrelated files, or a diff many times the stated size. Do not merge a scoped fix bundled with risky unrelated changes.
3. **Parts gate.** If the brief lists Parts A/B/C, confirm every part's files are in the PR. A `Fixes #N` line closes the issue even when only Part A landed.
4. **Stale-base gate.** Signal: deletions far exceed additions, or files outside the island are deleted. Rebase so only the PR's own commits remain: `git rebase --onto main $(git merge-base main <pr-branch>) <pr-branch>`. Confirm the reverted patterns are gone. If the rebase conflicts with real code, do not force-push: close the PR and relaunch on a current base.
5. **Shared generated files** (lockfiles, plugin lists, progress files): take one side, regenerate, commit. Never take one side blindly for source code.
6. **Conflicts and red CI**: prefer sending them back to Jules on its own branch (a follow-up message or a fix session with the exact error pasted and the files named). Jules cannot see CI output unless you paste it. Fix locally only generated files, or when Jules cannot.
7. **Draft PRs**: mark them ready before merging; the merge fails silently on drafts.
8. **Merge** with a merge commit, not a rebase with force-push. After a push, wait a few seconds for GitHub to recompute mergeability.
9. **Trust objective guards** (tests, ratchets, CI) over the PR body's claims.
10. **Post-merge**: run the project's full build and tests on main once, in your own commit. Known breakages: `references/merge-and-rescue.md`.

## 8. Rescue FAILED sessions

- Most FAILED sessions still produced code. Read the last patch that contains code (ignore lockfile-only patches): `patch`.
- Retrying the same prompt rarely works (measured: about 16% produced a PR). Rescue instead:
  ```bash
  git switch -c rescue/<wave>-<NN> origin/<base>
  git apply --3way --exclude='*lock*' <patch-file>
  # run the repo's local gates, then open the PR and explain the rescue in its body
  ```
- Read the failure signal. "Jules was unable to complete the task" right after the last activity means scope or spec. "Error when working on the task" after a long silence means a command ran too long: take the build out of the brief.
- Retry only if the cause is fixed. Use a new title (`… v2`) and the corrected brief. Never reuse the title.

## 9. Environment (top cause of FAILED)

- An empty setup script makes Jules infer setup from `AGENTS.md`. If that file lists heavy builds, the VM fails during setup or during work.
- Fix: set a light setup script in the web UI (repo → Environment → Setup script → run and snapshot). Add a "Remote agents" section to `AGENTS.md`: do not run full builds, CI verifies. Keep pre-commit hooks light: a heavy hook inside a Jules session kills its commits.
- The API has no field for setup scripts or environment variables. Set them in the web UI.
- If the repo's CI is blocked (for example, private repos with Actions billing failures), "CI verifies" does not hold. Use local gates instead.

## 10. Secrets

- Never put tokens, keys, or credentials in prompts, messages, or issues. Jules has no secret store.
- Split credentialed tasks: Jules prepares everything (code, green build, exact commands, rollback in the PR). A person or a local process runs the 2–4 authenticated commands.
- Exception: owner approval, a minimum-scope token, revoked right after, and recorded in the issue.

## 11. Close the wave

1. Check the status of every session (API).
2. Gate, then merge or rescue each PR (§7–8).
3. Archive every non-terminal session left (`AWAITING_*`, `PAUSED`, stuck). Archiving frees slots; an open AWAITING session can open a duplicate PR later.
4. Record each outcome: merged, closed without merge (find out who closed it and why), no PR, rescued.
5. Clean up: delete merged Jules branches; delete branches with no PR that revert merged work; close duplicate issues from earlier waves; check that no open Jules issues remain without a PR or a decision. Details: `references/merge-and-rescue.md`.
6. Optional: an independent review of the merged batch by a different agent, with findings turned into new briefs.

## 12. Gotchas

- "Session #N" is not necessarily a GitHub issue number. Check the issue, then search PRs by topic, then branches. Report what matches; do not invent status.
- The TUI shows only the current repo. `remote list --session` shows all repos, including sessions from other automation.
- Activities are oldest-first. Paginate to the end.
- Responses can contain control characters: parse with `json.loads(raw, strict=False)`.
- A POST whose response was lost may still have created the session. Search by title before retrying.
- Jules branches start with `jules-`. Use `head:jules-` to isolate its PRs from other authors' PRs.

## 13. Reference map

| File | Load when |
|---|---|
| `references/api.md` | calling the REST API, counting capacity, replying, parsing activities |
| `references/cli.md` | using the `jules` CLI, or it fails to start (NixOS) |
| `references/monitoring.md` | mapping sessions to PRs, PR outcomes, fallback when the CLI and API are down |
| `references/merge-and-rescue.md` | merge conflicts, stale bases, post-merge breakage |
| `references/stack-notes.md` | per-stack behavior (TS/JS, Rust, Flutter/Dart, Solidity) |

Related skills: `llm-routing` (which executor), `gitcore-jules-issues` (issue template for label dispatch).
