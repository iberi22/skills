---
name: public-repo-maintainer
description: Maintain a busy public repo (t3code-style). Triggers: public repo maintenance, contributor PR triage, branch/worktree policy, release nightly/stable, dependabot batching, CI gates, security disclosure, weekly repo checklist, labels and issue triage.
---

# Public Repo Maintainer (t3code model)

Study source: `github.com/pingdotgg/t3code` (clone read-only, never execute).

## 1. Branch / worktree policy

- Single source of truth is `main`. No long-lived `develop`/`staging` branches.
- Short-lived branches only: `fix/<scope>-<slug>`, `feat/<scope>-<slug>`, `agent/<task>`. t3code has dozens of ephemeral `agent/*` heads; `git log --oneline --merges` shows squash-merge onto main.
- One problem per PR (see `CONTRIBUTING.md#one-problem`). Split unrelated fixes.
- Worktree setup script runs on create (`t3.json` → `scripts/setup-worktree.ts`).
- Auto-cleanup: delete branch after merge; `git fetch -p` in weekly checklist.

## 2. PR flow (t3code `CONTRIBUTING.md` + `.github/pull_request_template.md`)

- Template sections required: Problem / Change / Scope-and-approval / Verification.
- Prior approval: features need a linked Ideas discussion with explicit maintainer approval; obvious tiny bugfixes exempt (explain why).
- Verification = focused tests + observed results, never just "tests pass". UI changes need before/after screenshots; motion needs a recording. Never commit PR-only assets (CI rejects `.github/pr-assets/` — see `.github/workflows/ci.yml`).
- Conventional titles: `fix(web): ...`, `feat(server): ...`, `chore(deps): ...`.
- Drafts get triaged the same as ready PRs.

## 3. Labels / triage

- Auto-labels, synced as code: `size:XS–XXL` (`.github/workflows/pr-size.yml`), `vouch:trusted|unvouched|denounced` from `.github/VOUCHED.td` (`.github/workflows/pr-vouch.yml`), `bug`+`needs-triage` on bug reports (`.github/ISSUE_TEMPLATE/bug_report.yml`), managed `bug/enhancement/needs-triage` sync (`.github/workflows/issue-labels.yml`).
- Only `TRIAGE_EXEMPTIONS.td` logins bypass triage; org membership or prior merges do not.
- Triage verdict: problem established? approval linked? scope coherent? evidence adequate? Passing triage ≠ correctness approval.
- Issues: `blank_issues_enabled: false` (`.github/ISSUE_TEMPLATE/config.yml`); bugs in issues, features in Discussions; agent-filed reports use `via-triage` template (`.github/triage/PLAYBOOK.md`).

## 4. Release / versioning

- Channels: `nightly` (scheduled cron `8,38 * * * *`, min 6h gap, only if changes — `.github/scripts/check-nightly-release.cjs`), `preview`, `stable` (tag `v*.*.*`; stable builds the commit the latest nightly already shipped — `.github/workflows/release.yml`).
- Concurrency: nightlies serialized (`queue: max`), stable never blocked by nightly.
- No changesets, no CODEOWNERS/labeler/dependabot config in repo; deps land as `chore(deps)` PRs.

## 5. Dependabot batching

- Batch minor/patch per ecosystem weekly; major upgrades get own PR with migration notes. Keep PRs small so `size:*` stays S/M.

## 6. CI gates / speed tricks

- Parallel jobs (lint / typecheck / build / test) on fast runners, `cancel-in-progress` on PRs, sparse checkout excluding heavy dirs, dependency cache, background apt-install while setup runs (`.github/workflows/ci.yml`).
- Path-filtered jobs (don't build Rust for docs-only PRs); final `Check` gate aggregates.
- Preview labels (`preview:web`, `preview:mac`) gate expensive builds; platform checks (`windows-tests.yml`, `mobile-fingerprint-check.yml`) scoped to touched code.

## 7. Security disclosure

- Report to `security@ping.gg`; never describe a vulnerability publicly before the fix ships (`.github/SECURITY.md`).
- Fix with generic commit messages (`fix(server): harden token check`); publish CVE/advisory only after release. Scrub secrets and home paths from issues (triage playbook rule 9).

## 8. Contributor experience

- `CONTRIBUTING.md` states plainly: limited review capacity, no merge guarantee, what gets accepted (focused fixes > unsolicited features).
- `AGENTS.md` documents glossary, surfaces to cover (entry points, clients, providers, contracts, reverse states, connection modes), and "three ways to hurt yourself".

## 9. Weekly checklist

```bash
git fetch -p; git branch --merged main | grep -v 'main$' | xargs -r git branch -d
gh pr list --state open --json number,title,labels | head -40
gh issue list --state open --label needs-triage --json number,title
gh release list -L 5; gh label list --limit 50
# close stale needs-triage with no repro; re-run /recheck-vouch where needed
```
