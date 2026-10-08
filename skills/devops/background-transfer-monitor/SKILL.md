---
name: background-transfer-monitor
description: 'Use when running long background uploads: track progress.'
---

# Background Transfer Monitor

Run long transfers so they stay observable, report progress as % + ETA, and
verify completion independently. Applies to any transfer with countable units
(files, repos, chunks).

## 1. Launch (observable)

1. Redirect to a log file, never pipe through `tail`/`head`:
   `cmd > ~/.cache/<job>.log 2>&1`. Pipes buffer and blind process polling.
2. Launch in background with completion notification.
3. Verify alive IMMEDIATELY after launch: list/poll the job AND `pgrep` for
   the real child process. A launch that reports "started" but shows no
   process died silently — relaunch, never assume it is running.
4. Record total units up front (file count, repo count) so % is computable
   on every later ping without new discovery.

## 2. Progress checks

- Progress = completed units / total units, measured INDEPENDENTLY of the
  job (destination listing vs local source) — never from the job's own
  claims alone.
- For rclone-to-Drive specifics see `references/rclone-drive.md`.
- Before reporting "stuck" on a slow unit, drill one level deeper (files
  inside the current repo/dir) and report the inner %.

## 3. Status reports

- Terse, in Spanish: phase %, total %, what is running now, what remains,
  ETA. One or two lines, no narration.
- An unchanged % between pings is a valid report — name the current unit
  and confirm it is still transferring.

## 4. Completion

- Done = exit code 0 AND independent verification (destination counts match
  source, spot-check key artifacts). A worker's self-report alone is not
  evidence.
- Final report: what landed where + counts. If the session changed a
  standing condition (e.g. network constraint lifted), update memory.

## Pitfalls

- Never pipe a background job through `tail` for its final output — the
  monitor then only sees buffered previews until the pipe closes.
- A missing remote directory is not proof of failure — confirm the source
  unit is non-empty first (some backends have no empty-dir concept).
- Verify new rclone filters from the SAME root the transfer runs from —
  `**/` patterns match relative to root, so a check from elsewhere misleads.
