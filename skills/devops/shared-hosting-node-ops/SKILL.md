---
name: shared-hosting-node-ops
description: 'Use when debugging Node on shared hosting: keep one copy.'
---

# Shared-Hosting Node Ops — cPanel/CloudLinux backends

Class-level workflow for Node backends living on shared cPanel hosting: no root, CloudLinux LVE limits, Node.js Selector (Passenger) available, deploys over SSH, Apache `.htaccess` proxy to a localhost port. Goal: one healthy copy, verified from the public internet, without ever pinning the account's process limit.

## Operating policy (standing)

- **Self-solve first, hosting support is last resort.** Diagnose everything reachable from our side (SSH, panel UI, public curl) before opening a ticket. Open one only when the cause is invisible from the account (e.g. processes nobody owns, panel backend itself crashing).
- **Support comms are non-technical.** Ticket drafts state symptoms + the one action requested ("kill the stuck processes on my account and tell me what spawns them"), never runtime internals, library names, or stack traces.
- **Act, don't narrate stalls.** If a step blocks, say what is blocked in one line and what runs next — never end a turn with only a promise. Background deploys report back on completion.

## Deploy flow (nohup worker + .htaccess proxy)

1. **Gate first:** lint clean, `tsc --noEmit` 0 errors, build produces `dist/index.js`, unit tests green, E2E green, no secrets tracked, no dev URLs in `dist`, deploy credentials present (never in repo — `.env.deploy`-style gitignored file only).
2. **Ship minimal tarball:** `dist + package.json + prisma` only. Never `node_modules`, `uploads`, or backups. Never print or overwrite the server `.env`.
3. **On the server:** `npm install --production` → `prisma generate` (pin the CLI version — a bare `npx prisma` can pull a wrong major) → `prisma db push`.
4. **Restart with verified death:** SIGTERM the old worker matched by CWD, wait up to ~20s verifying zero remain, SIGKILL stragglers, then start the new one with `setsid nohup`. Starting the new copy before the old one releases the port kills the new copy with `EADDRINUSE` while the health check still passes against the OLD copy — always confirm the PID changed.
5. **Post-checks from the public internet:** `/health` (or proxy path) → 200, one auth endpoint with a dummy payload returns the generic (non-enumerating) response, the public page → 200, exactly ONE worker process for the app, thread count sane (see below).

## The single-copy rule (hard)

- Exactly ONE running copy per backend, matched by process CWD (`readlink /proc/<pid>/cwd`). A second copy (stale nohup + a Passenger Play, a crashed restart that didn't die) doubles thread usage and causes `EADDRINUSE` crashes.
- **Passenger entry vs nohup: pick ONE mechanism.** If the app runs as a nohup worker behind an `.htaccess` proxy, a `stopped` Passenger entry for the same app root must stay stopped — pressing Play spawns a duplicate that fights for the same port and DB. Never delete a Passenger entry blindly (deletion may remove files); leaving it stopped is safe.
- A Passenger entry whose docroot subdirectory (e.g. `public_html/<uri>/.htaccess`) does not exist fails to start with `FileNotFoundError` from `clselector` — that is expected when the app is served by port+proxy instead of Passenger URI mapping. Do not "fix" it by creating the directory unless migrating to Passenger serving.

## CloudLinux LVE triage (NPROC counts threads)

- **NPROC counts threads, not processes.** A Node backend with a multithreaded engine layer (e.g. Prisma/tokio workers scale with core count) can sit at ~40+ slots while idle with CPU near zero — two copies pin a 100-slot account with nothing visibly wrong. Thread count per copy is checked with `ls /proc/<pid>/task | wc -l`.
- **Saturation signature:** `fork: Resource temporarily unavailable` everywhere, SSH authenticates but exec/SFTP channels never answer, the resource panel itself errors. Auth succeeding while channels stall rules out credential/rate-limit blocks.
- **When fork is dead, only shell builtins work** (`echo`, `kill`, `for`, `[[ ]]`, redirection reads of `/proc`). `ps`, `grep`, `tr`, `pgrep`, `curl` all need fork+exec and fail.
- **Never hammer a saturated account.** Each SSH attempt, panel click, and Play press spawns account processes. One probe at a time, generous waits between them; stop pressing panel buttons once NPROC is near the cap.
- Account owner vs operator: the cPanel account may belong to the client (tickets go out under their name), while deploy credentials live in the operator's local gitignored env file. Rotate any credential that ever landed in chat or repo history.

## Dictating shell to the user over chat

- **Chat corrupts paired asterisks in glob patterns** (`*sshd*` arrives as `sshd`, silently breaking `case` matches so "nothing found" looks like a clean result). When the user must paste shell from chat, match with `[[ $var =~ substr1|substr2 ]]` regex instead of `case` globs, and design every loop to print an explicit sentinel (`DONE`) plus per-item action lines (`KILLING <pid>`) so a zero-result run is distinguishable from a broken-pattern run.
- Prefer panel UI paths (Resource Usage snapshot tab, Node.js Selector states) over pasted shell when the user is non-technical — screenshots transcribed via vision beat terminal output they can't copy.

