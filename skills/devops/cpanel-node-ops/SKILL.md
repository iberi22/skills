---
name: cpanel-node-ops
description: Use when deploying Node backends on cPanel hosting.
---

# cPanel Node Ops

Deploy and debug Node.js backends on cPanel shared hosting (CloudLinux LVE, nodevenv, Passenger) via SSH plus panel clicks.

## One-time panel setup (per app, manual)

1. MySQL Database Wizard: database + user + ALL privileges. Record exact names for DATABASE_URL.
2. Setup Node.js App: Application root `~/<app>`, Startup file `dist/index.js`, Node major matching local engines, Mode Production.
3. Create `~/<app>/.env` on the server (DATABASE_URL, JWT_SECRET from `openssl rand -hex 32`, FRONTEND_URL, SMTP_*). Deploy scripts must NEVER touch this file.

## Automated deploy (SSH, scripted)

Tar `dist + package.json + prisma` (never node_modules/uploads/backups) → SFTP upload → swap dirs → `npm install --production` → `prisma generate` + `prisma db push` with a PINNED prisma CLI (npx latest can pull a breaking major) → restart per manager below → `curl` the local health port. Abort with a clear message if app dir, nodevenv, or server .env is missing.

## Process manager rule (never mix)

- Passenger-managed app: restart ONLY via `touch ~/app/tmp/restart.txt`. Never pkill/nohup alongside it or copies accumulate.
- Self-managed (nohup): restart by killing ONLY the worker whose CWD is the app dir (`readlink /proc/$p/cwd`), then `setsid nohup`. Never kill by bare process name.
- Accept hosting support's offer to register the app in the Node manager when given: it ends copy accumulation. Adapt the deploy script's restart step the same day.

## .htaccess proxy

Per-directory rules match the path WITHOUT leading slash: `RewriteRule ^api-prefix/(.*)$ http://<backend-host>:<port>/api/$1 [P,L]`. Keep a health passthrough (`^api-prefix/health$` → `/health`). Verify publicly with curl after every deploy; a 404 with a healthy backend means the proxy is not engaging (mod_proxy/AllowOverride), not an app bug.

## Secrets in deploy scripts

No credential fallbacks in tracked scripts: `password: process.env.DEPLOY_PASSWORD` plus a fail-fast guard (`Missing DEPLOY_PASSWORD in .env.deploy`, exit 1). Connection targets (host/user/port) may keep defaults; secrets never. `.env.deploy` stays gitignored. A burned credential means ROTATE on the server, not just delete from code: history keeps it.

## SSH failure ladder (in order, one probe each)

1. TCP connect to host:port. Closed/refused = network or firewall.
2. Auth-only connect + immediate clean disconnect. If auth fails everywhere, credentials are stale.
3. Auth OK but exec/SFTP channels never answer = SERVER-SIDE stall (stuck sessions, LVE limits), never a client bug. Repeated successful logins rule OUT rate limiting: cPHulk/fail2ban block pre-auth on FAILED logins, and a fresh auth+close succeeding proves no ban.
4. Never hammer: each killed local attempt can leave a lingering server-side session. Wait minutes between retries, one connection at a time.

## LVE essentials

- NPROC counts THREADS, not apps. A library spawning one worker thread per core (32-core host) pins NPROC at 100 with CPU near zero. Fix in app config: cap worker threads (e.g. 2), not by raising the limit.
- Resource Usage Snapshot tab only records limit-FAULT events; empty with zero faults is normal, not broken.
- On a fork-exhausted account only bash builtins work (for, read, echo, kill, `$(<file)`); every external binary (ps, grep, tr, pkill) fails. Triage via /proc with builtins only.

## Paste-safe shell for chat

Chat copy-paste strips paired `*text*` asterisks, silently turning `case *sshd*` into `case sshd` — a killer loop that matches nothing and reports success. In ANY one-liner the user will paste from chat, match with `[[ $var =~ regex ]]` instead of `case *glob*`. Bracket globs like `/proc/[0-9]*` survive; paired word-asterisks do not. After a kill loop with zero matches, distrust the pattern before distrusting the diagnosis.
