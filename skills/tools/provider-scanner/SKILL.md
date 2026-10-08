---
name: provider-scanner
description: Use when you need to know which cloud/dev CLIs (aws, gh, docker, kubectl) are installed, authenticated, or reachable on this machine before running tasks that depend on them.
license: MIT
---

# provider-scanner

Node CLI that probes local provider CLIs and writes a JSON report. Read-only
probes; no provider state is changed.

## What it checks

| Provider  | Probes |
|-----------|--------|
| `aws`     | `aws --version`; `aws sts get-caller-identity` (credentials); `aws service-quotas list-service-quotas --service-code ec2 --max-items 5` |
| `gh`      | `gh --version`; `gh auth status`; `gh api rate_limit` (core limits) |
| `docker`  | `docker version --format {{.Client.Version}}`; `docker info` (daemon reachable) |
| `kubectl` | `kubectl version --client -o json`; `kubectl config current-context` |

Also collects `environment`: OS, arch, hostname, RAM, free disk on `/`, `hasDocker`, Node version.

## Invocation

```sh
node scripts/provider-scanner.js
node scripts/provider-scanner.js --output ./providers-report.json
```

Flags (only these exist):

- `--output <path>`: report destination. Default `/tmp/providers-report.json`.

Requires Node.js and whichever CLIs you want scanned. Missing CLIs are reported
as `available: false`, not as errors.

## Output

Writes JSON (overwrites the target file without asking):

- `schemaVersion` (`"1.0"`), `scannedAt`, `durationMs`
- `providers[]`: `name` (`aws`, `github`, `docker`, `kubectl`), `available`,
  `credentialsPresent`, `version`, `path`, `error`, plus provider detail
  (`identity` for aws, `rateLimit` for gh, `info` for docker, `currentContext` for kubectl).
- `environment`: see above.

Stdout: one line, `Wrote <path> (4 providers, <ms>ms)`.

## Limits

- Each command has an 8 s timeout; output capped at 2 MB per command.
- `aws` and `gh` make authenticated API calls with the user's own credentials
  (`sts get-caller-identity`, `service-quotas`, `api rate_limit`). Run it only where that is acceptable.
- `kubectl` `available` is `true` whenever the binary exists; use `credentialsPresent` for context status.
- Only the EC2 quota family is queried for aws, limited to 5 items.
- Does not print or store secrets, but the report includes AWS account ID, ARN and user ID, and the hostname.
  Do not publish the report unredacted.
- No `--help`: the only flag is `--output`, and unknown arguments are ignored.
