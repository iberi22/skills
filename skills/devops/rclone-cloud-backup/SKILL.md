---
name: rclone-cloud-backup
description: Use when auditing a running rclone cloud sync job.
version: 1.0.0
tags:
- rclone
- backup
- google-drive
- sync
- filters
- quota
---

# Rclone Cloud Backup

Audit and maintain long-running `rclone sync` jobs to cloud remotes
(backup mirrors, not interactive transfers). Procedure first, then the
pitfalls that cost quota and time.

## Audit procedure (in this order)

1. Process alive? `ps aux | grep rclone`, then read the FULL command line
   via `/proc/<pid>/cmdline` (tr `\\0` to space) — ps output truncates
   flags. Record: source, dest remote:path, `--filter-from` file,
   `--tpslimit`, `--transfers`, `--log-file`.
2. Progress from the tool's own log: `tail` the `--log-file` and grep the
   `Transferred:` lines (count + bytes + ETA). Never poll the cloud API
   for progress — the log is instant and free.
3. Error census: count `ERROR` lines and look specifically for
   `rateLimitExceeded` / quota 403s. Occasional 403s with retries set is
   normal; a sustained 403 wall means `--tpslimit` is too high or the
   file mix is too small-file-heavy.
4. Filter-leak check: grep the live log for `Copied (new)` lines under
excluded territory (`site-packages`, `node_modules`, `.venv*`). Any hit
   is quota burned on junk — fix filters (see pitfall).
5. Continuity check: is the sync a bare one-shot command or a loop/timer?
   A bare `rclone sync` is ONE pass, not continuous backup. For
   change-as-it-happens coverage it must re-run (loop wrapper or
   systemd timer); re-passes are incremental and cheap.
6. Progress notifier (optional): a no-agent cron script that prints the
   last `Transferred:` line while the rclone PID lives and prints nothing
   when it exits (empty stdout = no notification). Keeps the user
   informed without an LLM per tick.

## DBs: `sync` is the wrong tool — snapshot them separately

`rclone sync` is a MIRROR: re-uploading a `.db` overwrites the remote copy and
Drive drops the previous revision. That is not a backup. DBs also fail as plain
transfers: live WAL/SHM files always error with `md5 hashes differ` or
`source file is being updated`, and large DBs that are genuinely worth keeping
are often already hidden by `- **/data/**` / `- .xavier/**` excludes.

Correct pattern (implemented in `proyectosSWAL/scripts/db-backup-snapshot.py`,
daily cron wrapper `~/.hermes/scripts/db-backup-db.sh`):
1. `sqlite3 VACUUM INTO` per DB via Python's `sqlite3` — a consistent, defragmented
   snapshot that does NOT require stopping the writer. Check `PRAGMA quick_check`
   first and skip a corrupt DB instead of overwriting a good remote copy.
2. gzip and `rclone copyto` (NOT sync) to `db-backup/<project>/<date>/` so prior
   versions are PRESERVED; prune by date folder for retention.
3. Skip dev-regenerable DBs (`.wrangler` miniflare trace stores, `.pnpm-store`) —
   they are hundreds of MB of tool cache, not data. `data/` must NOT be skipped.

Rule: exclude `*.db-wal` / `*.db-shm` / `*.db-journal` from the code sync (they
are ephemeral and always fail), but back up the `.db` itself via the snapshot path.

## Reporting progress: never print rclone's raw `Transferred:` line

A looping `rclone sync` RESETS its counters every pass, so the raw line reports
the % of THAT pass's plan, not of the project — the same work reads 61% → 77% →
92% and looks stuck. rclone's ETA is also meaningless when the remaining files
are 2-20 KB (it prints hours at 0 B/s). A notifier must:
- read the last pass boundary (counters back to `0 B / 0 B`) and say
  "N/total DE LA PASADA, cola X", not "X% del proyecto";
- list top-level dirs modified since the pass began but with no copies in it —
  rclone builds its file list when the pass STARTS, so new worktrees created
  mid-pass are silently skipped until the next restart (this is the usual real
  cause of a "stuck" sync);
- estimate real throughput from `Copied` lines per minute, not from the ETA;
- cost zero Drive API calls (there is a per-minute "Queries" quota that walls
  with 403s); use local logs + `stat`, and cache any full-log scan.

## Pitfalls

- Exact-name excludes do not match suffixed variants: `- **/.venv/**`
  still uploads `.venv-kokoro/` and `.venv-ui/`. Always add wildcard
  variants (`- **/.venv*/**`) plus a content catch-all for the ecosystem
  (`- **/site-packages/**` matches nothing but Python environments),
  because every leaked env is thousands of tiny files that burn API
  quota and stretch a sync from hours to days.
- Tightening excludes on a `sync` job DELETES the already-uploaded junk
  from the remote on the next pass (sync mirrors, including deletions).
  That deletion is the desired outcome but it happens on someone else's
  cloud copy — confirm with the user before applying, stating exactly
  what will be removed.
- `sync` refuses to delete when the pass had I/O errors (built-in guard).
  A remote that never converges plus `not deleting files as there were
  IO errors` in the log means the listing itself is failing (usually
  quota), not that the filters are wrong — fix quota first.
- Do not promise retention from memory: Google Drive keeps ~100 revisions
  or ~30 days (whichever is shorter) for non-Google files plus ~30 days
  in trash. Re-verify provider policy before committing to it in a
  report; it is the remote's versioning, not rclone's, that saves
  overwritten files — rclone itself keeps no versions unless
  `--backup-dir`/`--suffix` is configured.
- New top-level directories under a synced root need no registration:
  the next pass picks them up automatically unless a filter excludes
  them. Say so instead of building per-app plumbing.
