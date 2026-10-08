---
name: rclone-drive-backup
description: Use when uploading local trees to Google Drive.
tags:
- rclone
- google-drive
- backup
- devops
- swal
---

# Rclone Drive Backup

## When to use

Load this skill when the user asks to:
- Upload, sync, or snapshot local directories to Google Drive via rclone
- Refresh `md-plain` mirrors, `tree` copies, or `snapshots/` tarballs on Drive
- Check % complete of an in-flight rclone upload
- Debug why a Drive destination is stale or missing

## Procedure

### 1. Pre-flight: remote health + what is already there

```bash
rclone lsd gdrive: --max-depth 2          # remote reachable?
rclone about gdrive:                        # quota headroom?
rclone lsl gdrive:SWAL/snapshots/ | tail    # date of last snapshot upload
rclone lsd gdrive:SWAL/tree/apps/           # date of last tree sync
rclone lsd gdrive:SWAL/md-plain/            # 'directory not found' = mirror never ran
```

Compare remote dates against local scope before choosing full vs incremental:
a mirror dir that does not exist means that pipeline stage never completed,
not that it is up to date.

### 2. Verify the filter file BEFORE uploading

`rclone lsf` is NON-recursive by default — a bare `lsf` shows only top-level
entries and hides what the filter really passes. Always verify with:

```bash
cd <same-root-the-sync-runs-from>
rclone lsf -R --files-only <source-root> --filter-from <filter-file> | wc -l
rclone lsf -R --files-only <source-root> --filter-from <filter-file> | grep -v '<allowed-extension>$' | head
```

Run from the SAME root the sync uses, or `**/` patterns match differently
and the check is worthless. The second command must print nothing: any
non-allowed extension in output means the filter leaks.

### 3. Launch long uploads in background and confirm liveness immediately

Launch with `terminal(background=true, notify=true)`, then poll the session
at once: background launches can die silently, and a missing process only
shows up if you check. Capture the `session_id` — it is the only handle
for later polls.

### 4. Monitor via pgrep + remote listing, never via piped output

Do NOT pipe the long command through `tail`: tail buffers until the pipe
closes, so process polls show zero progress for hours. Monitor instead with:

```bash
pgrep -af "rclone copy" | grep -v hermes-snap   # in-flight transfer = current repo
rclone lsd gdrive:SWAL/md-plain/ | wc -l         # completed units
```

### 5. Report % as completed-units / total-units + current unit + ETA

```bash
ls -d <local-source>/*/ | wc -l    # total units
```

Heavy repos stall the % for a long time while the process is healthy —
report the in-flight repo name and ETA alongside the %, not the % alone.
Answer repeated "que % falta?" checks with fresh remote listings, never
from memory of the last check.

### 6. Completion evidence (all required before claiming done)

- Background process exited (poll shows completed, or `pgrep` empty).
- Fresh (today) timestamps in EVERY destination stage
  (`rclone lsl` on snapshots, `rclone lsd` on mirrors).
- Report: files/bytes transferred per stage + remote paths.

## Standing gates

- Gate multi-GB rclone syncs on unmetered network. On mobile/metered data,
  run snapshot (tarball) uploads only, or ask first — bulk small-file syncs
  are throttled to KiB/s and burn the data budget. When the user announces
  wifi is back, update the network-regime memory entry the same turn the
  upload is re-enabled.
- Never commit secrets: `rclone.conf` contains OAuth tokens — redact
  `token`/`client_secret` in any output you show.
