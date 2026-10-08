---
name: antigravity_guide
description: "Reference for using agy CLI (Antigravity) as a headless subagent: correct invocation, effort-tier selection, timeouts, status visibility, NixOS gotchas, and opencode CLI as an alternate backend."
version: 3.0.0
author: Claude (validated live 2026-09-26 against `agy --help`/`agy changelog`; supersedes prior Spanish versions)
tags: [antigravity, guide, agy, opencode, subagents, reference]
related_skills: [agy, agy-customizations, orca-cli, opencode-dev-workflow, model-routing-estrategia]
---

# agy CLI — subagent reference

All facts below verified against `agy --help`, `agy models`, `agy changelog` (v1.2.9-1.2.11) or live runs. If this drifts from `--help`, trust `--help`.

## Paths

- Binary: `~/.local/bin/agy` (`agy.bin`).
- Skills: `~/.agents/skills/` + mirrors (`~/.gemini/config/skills/`, `~/.openclaw/skills/`, `~/.hermes/skills/`, ...) — no known auto-sync; propagate manually.
- Full conversation logs: `~/.gemini/antigravity-cli/conversations/<id>.db`.
- **Fast status/progress**: `~/.gemini/antigravity-cli/conversation_summaries.db`, table `conversation_summaries` (`step_count`, `status`, `not_fully_idle`, `killed`, `last_modified_time`, `workspace_uris`). `step_count` rising = still working. No literal "%", `step_count` is the closest proxy.
- `sqlite3` CLI is **not installed** here — use Python's stdlib `sqlite3` module.

## Model / effort-tier selection

`agy models` lists effort baked into the name: `gemini-3.8-flash-{low,medium,high}` (also 3.7, 3.6; `gemini-3.1-pro-{low,high}`; `claude-sonnet-4-6`; `claude-opus-4-6-thinking`; `gpt-oss-120b-medium`). **Never pass `--effort` alongside a model whose name already has a tier suffix** — errors with "conflicts with --effort". Only use `--effort` with a model that has no tier suffix.

**Owner rule (Bel, 2026-10-03): Gemini ONLY at `-low` effort.** `high` and `medium` burn the weekly quota (the
first Google account was left at 30 % of its weekly allowance in one afternoon). The launcher `~/.local/bin/agy`
rewrites any `gemini-*-high` / `gemini-*-medium` to `-low` and any `--effort` value to `low`, with a warning on
stderr — so always ask for `gemini-3.8-flash-low` directly. Low is good **if the prompt guides it well**:
- One SHORT task per run (one finding, one file island, `--print-timeout` ≤ 20 min), staggered ≥ 45 s.
- The prompt names the exact files, the exact rule, the regression test to write FIRST (and see fail), and the
  package-scoped verification command. No open-ended "fix everything" runs.
- Judgment-heavy audits and design go to Claude (Opus) reviewers; parallel short fixes can also go to the free
  Hermes/opencode subagents (`free-model`). The orchestrator verifies (tests + mutation) before committing.
- A long run that dies mid-way leaves a half-done tree (measured 2026-10-03: inventory r2/r3 runs of 60-90 min).

Default to the cheapest tier that fits; escalate only when the task genuinely needs judgment.

**`low` tier risk**: given an open-ended "write code, then verify" task, a low-tier run may start with unscoped whole-project checks (`astro check`, full `vitest run`) before writing anything and burn the whole `--print-timeout`. Scope `--add-dir` to the smallest real working directory (a subpackage, not the monorepo root), tell it to write the code files before running any shell/test/check command, and never ask it for unscoped full-suite commands; the orchestrator verifies.

**Quota is shared across ALL Gemini models, not per model** (confirmed live 2026-09-26): after 4 parallel `gemini-3.8-flash-*` runs (~0.8M input tokens each), every Gemini model (`3.8-flash`, `3.7-flash`, `3.1-pro`) returned `RESOURCE_EXHAUSTED (code 429): Individual quota reached ... Resets in 59m` (exit code 3). `claude-sonnet-4-6` via agy uses a separate bucket and kept working — relaunch dead runs on it rather than waiting. Their edits stay on disk, so tell the relaunch to "continue from the current worktree state". Quick probe: `agy --model <m> --print-timeout 60s --output-format json --prompt "Reply OK"`.

## Headless invocation

```bash
agy --model <model> --project <unique-name> --add-dir "<workdir>" \
    --mode accept-edits --sandbox --dangerously-skip-permissions \
    --print-timeout 900s --output-format json --prompt "<full self-contained task>"
```

Run via the harness's `run_in_background: true` — **do not** also append a trailing `&`.

## Gotchas (each cost a real relaunch this session)

1. `--print`/`-p`/`--prompt` are aliases that consume the next token as their value. Never place them before other flags — `agy --print --model x ...` swallows `"--model"` as the prompt text. Put `--prompt "..."` last.
2. Headless mode auto-denies every `command`-type tool call without `--dangerously-skip-permissions` (no prompt UI exists to approve it) — looks like success (`status: SUCCESS`) but `denied_actions` is populated and nothing happened. Required for any Bash/cargo/grep work; contain the blast radius with `--sandbox` + a scoped `--add-dir` or a git worktree instead of skipping the flag.
3. Combining `run_in_background: true` with a trailing `&` makes the wrapper report "completed" instantly while `agy.bin` keeps running detached — check `ps aux | grep agy.bin` before relaunching, or you get duplicate processes editing the same tree concurrently.
4. Model name already has an effort suffix + `--effort` flag = hard error (see above).
5. **No `--print-timeout` = the run waits for its own self-launched background processes (e.g. an agent-started `cargo test`) until they finish, unconditionally** (per `agy changelog` 1.2.9+: default changed from 5min to unlimited; background tasks are *not* killed on timeout, they're left running and the CLI returns partial output only once `--print-timeout` itself expires). Always pass `--print-timeout <duration>` to bound worst case. Without it, a hung subprocess can burn the full session. **Confirmed live 2026-09-26**: a run launched without this flag (and with the redundant `--effort` mistake from gotcha #4 on top) had its own conversation reach `CASCADE_RUN_STATUS_IDLE` / `step_count` frozen ~14 minutes before the OS process (`agy.bin`) was still alive — it was blocked on a self-launched `npm exec vitest run <file>.test.ts` child that never returned. Diagnosis: don't stop at `ps aux | grep agy.bin` when wall-clock looks long — run `ps --ppid <agy.bin PID>` to see what child it's actually blocked on.
6. **`--print-timeout` takes a Go duration string, not a bare integer** — `--print-timeout 900` fails immediately with `time: missing unit in duration "900"` (exit code 2, nothing runs). Use `900s` or `15m`.
7. **A wrapper script's own trailing `echo "exit code: $?"` (or similar) defeats exit-code checking at the orchestrator level**: if you background a shell script via the harness's `run_in_background`, the task-notification's `(exit code N)` reflects the *script's last command*, not `agy`'s actual exit code — an `echo` after a failed `agy` call reports `(exit code 0)` even though `agy` itself exited 2. **Confirmed live 2026-09-26** alongside gotcha #6 above: the notification said "completed (exit code 0)" for a run that had actually failed flag-parsing instantly. Fix: end the wrapper with `exit $?` (propagate the real code) instead of an `echo`, and/or always read the captured stdout/stderr files yourself rather than trusting the notification summary.
8. Parallel agents must touch disjoint files (or separate worktrees) and must **not** `git add`/`git commit` — the orchestrator reviews and commits after reading each `REPORT.md`.
9. Since 1.2.10, a headless run that fails on a model/agent error exits with code `3` and an `AGY_ERROR: {...}` JSON line on stderr — check the exit code and that line, don't assume success just because the process returned.

10. **Shared `CARGO_TARGET_DIR` + 4 parallel agents that each run clippy + tests = starvation** (confirmed live 2026-09-26, Rust repo Xavier): cargo's lock serializes every build, so each agent spent most of its budget in "waiting on the build directory lock"; 3 of 4 runs hit `--print-timeout 3000s` with code written but no `REPORT.md`. Rule for parallel Rust waves: subagents write code and run at most `cargo check` (or nothing); the orchestrator runs fmt/clippy/tests once per worktree afterwards. Separate target dirs avoid the lock but cost a full dependency build (GBs of RAM/disk) each.

## NixOS-specific: running Rust test/binaries (solved 2026-09-26)

Compile works with `PKG_CONFIG_PATH=$HOME/.nix-profile/lib/pkgconfig` (`cargo check`, `cargo test --no-run`, `cargo build`). **Running** the output binary fails: nix-profile OpenSSL pins RUNPATH to a newer glibc (2.42) while the system loader is 2.40 → "GLIBC_ABI_DT_X86_64_PLT not found", or SIGSEGV if you only set `LD_LIBRARY_PATH` (loader/libc mismatch). **Fix: invoke the binary through the matching glibc's own loader**, never `LD_LIBRARY_PATH` alone:

```bash
cargo test --lib --no-run            # prints "Executable unittests ... (<path>)"
<path> 2>&1 | head -2                # error names the glibc it needs: "... (required by /nix/store/<HASH>-glibc-2.42-NN/lib/...)"
G=/nix/store/<HASH>-glibc-2.42-NN/lib    # multiple 2.42 builds exist in the store — use the one from the error
$G/ld-linux-x86-64.so.2 --library-path $G <path> [test_filter]
```

**`--lib` is NOT the full suite.** Integration tests (`backend/tests/*.rs`), bin unit tests and other workspace crates are separate executables — `cargo test --lib` missed 2 real regressions on 2026-09-26. Full run:

```bash
cargo test --workspace --no-run 2>&1 | grep -oE '\(/[^)]+\)' | tr -d '()' > bins.txt
while read b; do $G/ld-linux-x86-64.so.2 --library-path $G "$b" 2>&1 | grep '^test result'; done < bins.txt
```

Same loader pattern works for `target/debug/<bin>` (e.g. a backtest CLI). Give subagents this exact recipe instead of banning tests, and never accept a subagent's "all tests pass" without checking which targets it ran — one agent edited a test to match its own overclaim. Docker remains the zero-config alternative.

## Alternate backend: `opencode` CLI (free models)

Routing between backends lives in skill `llm-routing` (canonical). If the paid
`opencode-go/*` models return `Invalid API key`, use the free Zen models, discovered
and smoke-tested by `~/.hermes/scripts/free-models-refresh.sh` (cache
`~/.cache/swal/free-models.json`). Default for code: `opencode/space-bunny-free --variant max`.

```bash
opencode run --model opencode/space-bunny-free --variant max \
  --dir "<workdir>" --title "<name>" --auto --format json "<task>"
```

Flags MUST precede the message (a misordered flag prints `--help` and exits 0). Flag
equivalence with agy: `--auto` = `--dangerously-skip-permissions`, `--dir` = `--add-dir`,
`--variant` = effort, `--title` = `--project`. No sandbox flag: contain it with a worktree.
From Claude Code, the `free-model` subagent wraps this call.

## Alternate backend: `codex` CLI (ChatGPT Plus)

Model/effort policy and quota facts live in `llm-routing` §1e (canonical). Invocation:

```bash
codex exec -m gpt-6-sol -c model_reasoning_effort=medium \
  -C "<workdir>" -s workspace-write -o "<out.md>" "<self-contained task>" < /dev/null
```

- `< /dev/null` is mandatory — without it `codex exec` waits on stdin forever.
- Always pass `-m`; never rely on the config default. `gpt-6-astra` only at low/medium.
- Planning with structured output: `-s read-only --output-schema <schema.json> -o <out.json>`.
- Same rules as agy/opencode: own worktree, disjoint files, no `git add/commit`, no unscoped
  `cargo test`; the orchestrator verifies. Confirm progress within a minute (log size grows).

## Customization

See `agy-customizations` for skills/rules/hooks without breaking updates.

**Automatic quota fallback (2026-09-28):** `~/.local/bin/agy` (the launcher) now retries a non-interactive run once on `claude-sonnet-4-6` when a Gemini model answers RESOURCE_EXHAUSTED (agy may exit 0 with `"status":"ERROR"`, so it checks the output, not the exit code). Original launcher: `~/.local/bin/agy.launcher.bak`; an agy update can overwrite the launcher — re-check after updates. Second Google profile (`HOME=~/.agy-profiles/b`) is not set up yet (owner login pending).

**Concurrent launch OAuth race (confirmed live 2026-10-01, agy 1.2.14):** launching 3 headless runs within the same second
made the first one refresh `~/.gemini/antigravity-cli/antigravity-oauth-token` while the other two printed "Authentication
required ... Waiting for authentication (timeout 60s)" and exited 1 after ~90 s with `"error":"authentication failed or timed
out"` (no work done). Stagger parallel launches by ≥ 45 s (or run a `--prompt "Reply OK"` probe first), and treat a run that
dies in < 2 min with exit 1 as an auth race → relaunch.

