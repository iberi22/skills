---
name: cron-fleet-maintenance
description: "Use when auditing or repairing a fleet of cron jobs."
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [cron, automation, fleet, audit, triage, no-agent, harness, cost]
---

# Cron Fleet Maintenance

A fleet of scheduled jobs is a system, not a list. This is the class-level
procedure for auditing it, deciding what to keep, and repairing what is broken.
Applies to any scheduler with the same primitives: a job registry file, per-job
schedule/prompt/script, and a `no_agent` (script-only) mode that costs no tokens.

Triggers: audit my cron jobs; which jobs cost tokens; which jobs are obsolete;
unify duplicate jobs; a job reports ok but fails; a scheduled job broke; job
fails with 402 / insufficient funds / command not found.

## Step 1 — Inventory before touching anything

Back up first, then classify. Nothing else matters until you can answer these
three per job:

1. **Does it cost tokens?** `no_agent: true` = script only, zero inference, no
   matter how often it fires. Otherwise it costs once per tick — unless it is
   monitor-gated (a script whose hash gates the wake-up), in which case it only
   costs when that hash changes. A monitor-gated job idle for days is spending
   nothing; say so rather than counting executions as cost.
2. **Is it broken, or starved?** HTTP 402 / "insufficient funds" means the
   *provider* is out of credit, not that the job is defective. Starved jobs are
   still worth keeping — pause, never delete. Genuinely obsolete means: script
   deleted, workdir gone, or never executed. Verify both on disk before deciding.
3. **Is it covered elsewhere?** Two jobs for one repo is duplication; two jobs
   for two repos is not. Before pausing a "redundant" job, confirm the
   replacement covers the *same* target. Redundancy you assumed is a coverage
   gap you just created.

Read the schedule field as a **structured dict**, not a cron string, and compute
frequency: `{"kind":"interval","minutes":20}` is 72/day, `"*/30 * * * *"` is
48/day. Parsing it as a string yields nonsense (a 20-minute job does not fire
once a day).

## Step 2 — Repair wrappers before trusting any status

A job reporting `ok` can be lying. These three defects each made a job report
success while failing, and all are invisible from the registry:

- **A pipe to a truncating command returns the wrong exit code.** `cmd | tail -n 8`
  exits with *tail's* status (0), so any real failure reads as success. Use
  `set -o pipefail` and exit with `${PIPESTATUS[0]}`. The identical shape:
  `git add a b c 2>/dev/null` aborts (rc 128) and stages **nothing** when one path
  is missing, leaving any guard reading `git diff --cached` silently scanning an
  empty set. Never suppress stderr on a command whose failure changes what you
  inspect.
- **A minimal env breaks absolute-looking assumptions.** Cron/systemd env is not
  your shell's. On NixOS `/usr/bin` does not exist and coreutils plus node live
  under the system store path, so an exported PATH without it yields
  "command not found" (exit 127) on the first utility the script uses.
- **A script that reads a label/marker that does not exist.** `gh issue create
  --label X` does *not* create label X: gh fails, the issue goes out unlabelled,
  and the script dies after having already written. Ensure the prerequisite is
  present, idempotently, before the tool that requires it.

Test every wrapper under an explicit minimal env, not your shell:

```bash
env -i HOME="$HOME" PATH="/run/current-system/sw/bin:$HOME/.local/bin:/usr/bin:/bin" \
  bash wrapper.sh; echo "EXIT=$?"
```

## Step 3 — Verify by the real channel

Shell output is not the job's environment; the dispatcher's own session is.
Trigger the job and let it run where it actually runs, then read back
`last_status`/`last_error`. A job that only ever passed in your shell is unproven.

## Always-on rules

- **Back up in two artifacts before any destructive step**: the full prior state
  (`registry.json.bak`) and a manifest of `id + reason` per removed entry.
  "Reversible" means another session can restore without reconstruction.
- **Prefer pause over delete** for anything that might be needed again (starved
  providers, seasonal work). Delete only after confirming on disk that the
  script and workdir are gone.
- **Clean residual state on conversion.** When a job goes `no_agent`, clear its
  `model`/`provider`/`skills`/`prompt`. They are inert today but are a trap: the
  day someone removes `no_agent`, the job silently reverts to a provider that may
  have no credit. State should reflect what the job does.
- **Report cost in executions/day, split by whether inference is involved** —
  that split is the whole reason the audit is worth running.
- **State what you did not verify.** Jobs that have never fired (future-dated),
  repos left without coverage, or jobs skipped for lack of credit belong in an
  explicit "pending" list, not quietly in a green table.

## Verifying when no test command exists

Most cron wrappers have no repo, no CI, no canonical gate. "No gate exists" means
you build one — and a harness you delete at the end of the turn guarantees the
same verification gets rebuilt next session. Full procedure, plus the
`git add` / `git rm --cached` staging traps that bite staging guards, in
`references/adhoc-harness-and-staging-traps.md`.

## Support files

- `references/adhoc-harness-and-staging-traps.md` — building an ad-hoc harness
  with checks that have teeth, and the git-index behaviours that make
  pre-commit/staging guards silently pass
