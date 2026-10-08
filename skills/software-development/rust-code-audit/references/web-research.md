# Web Research Output Template (Concrete Example)

Use this structure when documenting web research for `rust-code-audit`.

---

## Query 1: Rust Security Audit Checklist 2026

**Query:** `Rust security audit checklist 2026 unsafe code production`

- Key risk areas: unsafe contracts, FFI boundaries, async deadlocks, supply chain gaps
- Critical insight: "binary in production ≠ code reviewed" — feature flags/target deps change what runs
- Recommended tools: cargo-deny, cargo-vet, Cargo Scan (effect tracking across crate boundaries)
- Reference: https://sherlock.xyz/post/rust-security-auditing-guide-2026
- Academic: Cargo Scan — interactive program analysis for crate auditing (ESOP 2026)
  - Reduces audit burden to ~0.2% of LOC compared to auditing whole crates

## Query 2: Rust Async Performance Optimization (Tokio spawn_blocking)

**Query:** `Rust async performance optimization 2026 tokio spawn_blocking`

- spawn_blocking: offloads synchronous/blocking work to dedicated thread pool
  - Default blocking pool limit: 512 threads
  - Has overhead (thread switch, cache invalidation) — use judiciously
- Anti-pattern #1: Running blocking code (std::sync::Mutex, thread::sleep, file I/O) on worker threads
- Anti-pattern #2: Holding std::sync::Mutex across `.await` points
- Fix for CPU-bound: tokio::task::spawn_blocking
- Fix for I/O: prefer async-native APIs (tokio::fs, tokio::net, tokio_postgres)
- Reference: https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
- Reference: https://www.techbuddies.io/2026/03/21/top-5-tokio-runtime-mistakes-that-quietly-kill-your-async-rust

## Query 3: Rust Supply Chain Security (cargo-audit / cargo-deny)

**Query:** `Rust supply chain security cargo audit 2026 dependency management`

- cargo-audit: checks against RustSec advisory DB for known vulnerabilities
  - Github Action: rustsec/audit-check
- cargo-deny: licenses, sources, duplicate versions, advisory database
  - Github Action: embark-studios/cargo-deny-action
- Cargo Machete: detects unused dependencies
- Cargo Scan: helps audit *potentially dangerous code* in transitive deps
- Risk: dependency creep, unmaintained crates, transitive unsafe
- Recommendation: run cargo audit + cargo deny in CI
- Reference: https://rustsec.org
- Reference: https://blog.logrocket.com/comparing-rust-supply-chain-safety-tools

---

## Variant Queries for Commit-Scoped Audits

### Query: Type widening safety (u32→u64)

**Query:** `Rust type safety concerns type widening u32 to u64`

- Widening conversions are ALWAYS safe in Rust (std `From<u32> for u64` is guaranteed)
- `as u64` cast is safe for widening (no truncation)
- Pitfall: operation-order bug — arithmetic on narrower type before widening
  - `(x + y) as u64` — BUG: overflows as u32 first
  - `(x as u64) + (y as u64)` — FIX: widens before arithmetic
- JSON serialization: both u32 and u64 serialize as JSON numbers — backward compatible
- Ref: https://stackoverflow.com/questions/28273169/how-do-i-convert-between-numeric-types-safely-and-idiomatically

### Query: Rust workspace dependency version consistency

**Query:** `Rust dependency version consistency best practices`

- Use `[workspace.dependencies]` to pin shared deps across all crates
- Caret notation: `"1.37"` = `"^1.37"` = `">=1.37.0, <2.0.0"`
- Version drift across crates: Cargo resolves highest compatible, but explicit inconsistency is maintenance debt
- Tools: `cargo-outdated`, `cargo upgrade`, `cargo update -Z minimal-versions`
- Ref: https://users.rust-lang.org/t/best-practice-in-specifying-dependency-versions-in-cargo-toml/54007

### Query: Dead code removal in Rust workspaces

**Query:** `Rust workspace hygiene dead code removal tips`

- `cargo clippy -- -D warnings` catches dead code before merge
- `cargo-minify` auto-removes unused functions/structs/kinds
- `cargo-udeps` detects unused dependencies
- Dead code removal improves compile times (less LLVM IR) and reduces attack surface
- Ref: https://github.com/tweedegolf/cargo-minify
- Ref: https://matklad.github.io/2021/08/22/large-rust-workspaces.html
