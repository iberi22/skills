---
name: cargo-wizard
description: "Use when validating Rust code. Runs check test clippy fmt."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [rust, cargo, build, check, test, clippy, fmt, quality-gate, ci-cd, validation]
    related_skills: [rust-compile-optimization, rust-build-ramdisk, rust-workspace-patterns]
    references:
      - url: https://doc.rust-lang.org/cargo/commands/cargo-check.html
        title: "cargo check — Official Documentation"
        year: 2026
      - url: https://doc.rust-lang.org/cargo/commands/cargo-clippy.html
        title: "cargo clippy — Official Documentation"
        year: 2026
      - url: https://doc.rust-lang.org/cargo/commands/cargo-fmt.html
        title: "cargo fmt — Official Documentation"
        year: 2026
      - url: https://nexte.st/
        title: "cargo-nextest — Fast Test Runner"
        year: 2026
      - url: https://github.com/rust-clippy/rust-clippy
        title: "Rust Clippy Lints — GitHub"
        year: 2026
---

# Cargo Wizard — Rust Build Pipeline

> 🦀 Automated Rust quality gate for SWAL repos. One command to rule them all.

## Quick Start

```bash
# Full pipeline (check → test → clippy → fmt)
cargo wizard

# Quick check only
cargo wizard --quick

# CI-safe features
cargo wizard --features ci-safe

# JSON output (for automated parsing)
cargo wizard --json
```

## Pipeline Phases

| Phase | Command | Pass Criteria | Timeout |
|-------|---------|---------------|---------|
| 1. Check | `cargo check --lib` | Exit 0, 0 errors | 120s |
| 2. Test | `cargo test --lib` | Exit 0, 0 failed | 300s |
| 3. Clippy | `cargo clippy --all-targets -- -D warnings` | Exit 0, 0 warnings | 180s |
| 4. Format | `cargo fmt --all -- --check` | Exit 0, no diff | 30s |

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | All phases PASS | ✅ Ready to merge |
| 1 | Check failed | ❌ Fix compilation errors |
| 2 | Tests failed | ❌ Fix failing tests |
| 3 | Clippy warnings | ⚠️ Fix warnings (<5 auto-fix, >5 delegate) |
| 4 | Format issues | ⚠️ Run `cargo fmt --all` |

## Usage in Subagents

When a subagent is spawned for Rust work, inject this context:

```
## CARGO WIZARD CONTEXT

You are working on a Rust project. Use these commands to verify your changes:

1. cargo check --lib          # Compile check
2. cargo test --lib           # Run tests
3. cargo clippy --all-targets -- -D warnings  # Lint
4. cargo fmt --all -- --check  # Format check

RULES:
- ALWAYS run `cargo check` before declaring work done
- If clippy reports <5 warnings, fix them directly
- If clippy reports >5 warnings, report to orchestrator
- Never commit code that doesn't pass `cargo check`
```

## SWAL Repos Configuration

| Repo | Features | Special Flags |
|------|----------|---------------|
| `iberi22/xavier` | `--features ci-safe` | `--no-default-features` |
| `iberi22/gestalt-rust` | — | Target: `aarch64-linux-android` |
| `iberi22/cortex-1` | — | Uses SurrealDB |

## Integration with jules-integration

The `cargo-wizard` is used by `jules-integration` pipeline:
- **CLEAN PR**: All 4 phases pass → ready for review
- **DIRTY PR**: Any phase fails → re-assign to Jules

## Decision Rules for Subagents

| Situation | Action |
|-----------|--------|
| Check fails | Read error, fix code, re-run check |
| Test fails | Read failing test, analyze, fix |
| Clippy <5 warnings | Fix inline in code |
| Clippy >5 warnings | Report to orchestrator |
| Format fails | Run `cargo fmt --all`, re-check |
| Timeout (>5min) | Break work into smaller chunks |

## Clippy Common Fixes

```rust
// ❌ clippy::needless_return
fn foo() -> i32 {
    return 42;
}

// ✅
fn foo() -> i32 {
    42
}

// ❌ clippy::manual_map
match option {
    Some(x) => Some(x * 2),
    None => None,
}

// ✅
option.map(|x| x * 2)

// ❌ clippy::redundant_clone
let s = String::from("hello");
let t = s.clone();
println!("{}", s);

// ✅
let s = String::from("hello");
println!("{}", s);  // Use s directly if clone isn't needed
```

## Nextest Integration (optional, faster)

```bash
# Install
cargo install cargo-nextest

# Use instead of cargo test
cargo nextest run --lib
cargo nextest run -p my-crate
```

## Referencias

1. **cargo check**: https://doc.rust-lang.org/cargo/commands/cargo-check.html — Documentación oficial.
2. **cargo clippy**: https://doc.rust-lang.org/cargo/commands/cargo-clippy.html — Lints de Rust.
3. **cargo fmt**: https://doc.rust-lang.org/cargo/commands/cargo-fmt.html — Formateo de código.
4. **cargo-nextest**: https://nexte.st/ — Test runner paralelo, 2-5x más rápido.
5. **Clippy Lints**: https://github.com/rust-clippy/rust-clippy — Lista completa de lints.
6. **Rust Style Guide**: https://rust-lang.github.io/rustfmt/ — Guía de formateo.

## Pitfalls

| Problema | Causa | Solución |
|----------|-------|----------|
| Clippy warnings in test code | Tests use different patterns | `#[allow(clippy::...)]` or fix if egregious |
| Format fails on CI | Local fmt version differs | Use `rustfmt.toml` to pin version |
| Check passes but build fails | Missing build.rs or features | Use `cargo check --all-targets` instead |
| Tests timeout | Slow tests or deadlocks | `cargo test -- --test-threads=1` to debug |
| Clippy auto-fix breaks code | Complex lint | Fix manually instead of `--fix` |

---

*Cargo Wizard — v1.1.0 (with references)*
