# jules CLI

Checked 2026-10-08 on the working host: `jules remote list --session` and `jules remote list --repo` both exited 0 and printed results. `jules --help` lists the commands below. No cancel, close, or delete command exists.

## Commands

```bash
jules                                   # TUI
jules new "<task>"                      # session on the current directory's repo
jules new --repo <owner>/<repo> "<task>"
jules new --repo <owner>/<repo> --parallel 3 "<task>"
jules remote list --session             # sessions across all connected repos
jules remote list --repo                # connected repos (also a login check)
jules remote pull --session <ID>        # fetch the result
jules remote pull --session <ID> --apply
jules teleport <ID>                     # clone, checkout, apply patch; fails on uncommitted local changes
jules login                             # Google OAuth in a browser
jules logout
```

- "No valid client" from `remote list --repo` means not logged in.
- `remote pull` can return HTTP 400 when the remote session has expired. Recover what you can from the API activities instead (`api.md`).
- The CLI lists sessions for every repo. The TUI shows only the current repo.
- `jules new` with `--parallel N` creates N sessions for the same task. Use it only for independent tasks with distinct titles.

## Quoting and scripting

- Put timeouts around CLI calls in cron or pipelines: `timeout 10 jules remote list --session`. A hung call otherwise stalls the whole pipeline.
- Test the exit code, not only the output. Empty output with exit 0 is ambiguous (see NixOS below).

## NixOS: when the binary does not start

Symptoms and responses:

| Signal | Meaning | Response |
|---|---|---|
| "Could not start dynamically linked executable" or "NixOS cannot run dynamically linked executables" | Generic-Linux binary on NixOS, or its self-extraction to a temp dir fails | Run `steam-run "$(command -v jules)" remote list --session`. steam-run provides an FHS environment. |
| Exit 0, empty output | Inner Go binary failed silently | Retry with steam-run. Do not conclude "no sessions". |
| Exit 124, empty output | Service or network unreachable | Do not retry with steam-run. Use the GitHub-state fallback in `monitoring.md`. |
| Exit 127 | Not runnable or not on PATH | Check PATH. Cron and NixOS shells often lack `~/.local/bin`; check the file exists before concluding it is missing. |

Diagnostic: `jules remote list --session 2>&1 | grep -i "could not start\|stub-ld"`.

`patchelf` on the downloaded binary did not fix the self-extraction in the tested setup. Do not spend time on it before trying steam-run.
