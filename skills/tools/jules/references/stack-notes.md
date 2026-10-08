# Stack notes

Qualitative notes from observed sessions.

## TS/JS (Astro, Svelte, Vite/React, Cloudflare Workers)

- Default destination for Jules tasks.
- Good fits: unit tests, UI changes driven by design tokens, content, dependency bumps, small components.
- Playwright E2E tasks open PRs often but merge less often. Keep each E2E brief narrow: one flow, one file set.
- Brief must name the verification command for the touched module (`vitest run <path>`, the package's test script). Do not ask for the full build.

## Rust

- Good fits: fixes in a single crate, small features with clear file scope, unit tests in the touched module.
- Poor fits: refactors across a large workspace, decoupling many modules, anything that needs a full `cargo build`/`cargo test` inside the VM. The VM times out during long commands and the session ends FAILED.
- Brief wording that works: "Do not compile. Run `cargo fmt -- <files>` only; CI runs clippy and tests."
- Per-commit clippy or other heavy hooks inside the repo kill Jules's own commits. Keep hooks light and make the heavy mode opt-in.
- Probe the repo with one session before a wave when its setup or hooks changed.

## Flutter / Dart

- Expect conflicts on generated files in every parallel PR (see `merge-and-rescue.md`).
- Sessions can take hours to produce a PR. Use only when the work is not urgent; otherwise do it locally.
- After merging a batch: regenerate code, check the SDK constraint against the installed toolchain, run the full test suite.

## Solidity

- Small, well-specified contract changes with existing test suites fit well.
- Brief must name the test command and forbid deploys and any key or RPC use.
- Any task that needs a funded wallet, a live RPC, or a deployment is out of scope (§1 of `SKILL.md`).

## Dependency bumps

- Good fit when the brief names the exact version, the changelog to check, and the verification command.
- Lockfile-only PRs fail the empty-PR gate. Require a code or config change to go with the bump, or do the bump locally.
