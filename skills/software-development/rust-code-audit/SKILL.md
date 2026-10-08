---
name: rust-code-audit
description: "Use when auditing Rust code. Finds security and perf bugs."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [audit, security, performance, code-review, rust]
    related_skills: [requesting-code-review, codebase-inspection, systematic-debugging, github-issues, rust-code-quality-audit]
    references:
      - url: https://rustsec.org/
        title: "RustSec — Security Advisory Database"
        year: 2026
      - url: https://github.com/rustsec/rustsec
        title: "cargo-audit — Security audit for dependencies"
        year: 2026
      - url: https://docs.rs/subtle/latest/subtle/
        title: "subtle crate — Constant-time comparisons"
        year: 2026
      - url: https://tokio.rs/tokio/tutorial/shared-state
        title: "Tokio Shared State Patterns"
        year: 2026
      - url: https://cheats.rs/#unsafe
        title: "Rust Cheatsheet — Unsafe Code Patterns"
        year: 2026
---

# Rust Code Security & Performance Audit

Full-scale audit methodology for Rust codebases. Combines web research grounding with systematic pattern-based code search to find security vulnerabilities, performance anti-patterns, and supply-chain risks.

## When to Use

- User requests "security audit", "performance audit", or "code review" of a Rust project
- Before a release or merge of a large feature branch (50+ files, 5000+ LOC changed)
- After merging external contributions or autonomous-agent PRs
- When evaluating a new dependency or crate for adoption
- As part of a recurring audit cycle (e.g., AUDIT-5-*, AUDIT-6-* series)
- **When auditing a specific commit** — use Commit-Scoped Audit (Phase 0) instead of broad pattern search

**Skip for:** single-file changes, documentation-only PRs, pre-commit review (use `requesting-code-review` instead), or quick-fix sessions.

## Skill vs Related Skills

| Skill | Scope | Trigger |
|-------|-------|---------|
| **rust-code-audit** | Full codebase audit — security + performance + supply chain | "audit", "security review", "performance review" |
| `requesting-code-review` | Pre-commit diff scanning | "commit", "verify", "ship" |
| `codebase-inspection` | LOC/structure/CI/docs analysis | "how big", "what's in this repo" |
| `systematic-debugging` | Root cause debugging of specific bugs | bug reports, test failures |
| `github-code-review` | Reviewing other people's PRs with inline comments | "review PR #X" |
| `rust-code-quality-audit` | Architecture + code quality (separate from security) | "quality audit", "architecture review" |

## Phase 0 — Commit-Scoped Audit (when auditing a specific commit)

When the audit targets a specific commit (not the whole codebase), start with `git diff` analysis to understand the scope **before** running broad pattern searches:

```bash
# 1. Understand the scope
git log --oneline -5              # Recent history, context
git diff --stat HEAD~1..HEAD      # Files changed, lines added/deleted

# 2. Diff per file for key changes
git diff HEAD~1..HEAD -- <file>   # Detail per affected file

# 3. List all parent commits in the wave
git log --oneline HEAD~N..HEAD    # All commits in this wave/release
```

**Identify the change categories** from the diff stat before diving into patterns:

| Category | What to check | Security? | Performance? |
|----------|---------------|-----------|--------------|
| **Type widening** (u32→u64, f32→f64) | Verify no truncation, JSON compat, operation-order bugs | ✅ Safe in Rust (widening is always lossless) | Usually neutral |
| **Dead code removal** | Verify no needed code accidentally removed | ✅ Positive (reduced attack surface) | Marginal compile improvement |
| **Struct consolidation** | Verify DTOs moved to shared crate, no stale imports | ✅ Positive (single source of truth) | Net LOC reduction |
| **Dependency version bumps** | Verify semver compatibility, workspace consistency | ⚠️ Check for API breakage | Usually positive |
| **Docs updates** | Verify workspace structure accuracy, no stale claims | Usually PASS | No impact |
| **CLI command changes** | Verify enum match, help text accuracy | Low | Low |

Then run targeted `git diff` on the specific files identified, rather than broad `search_files` across the entire codebase.

## Phase 1 — Web Research Grounding (3 parallel queries)

Before examining code, establish current best practices. Run 3 web searches in parallel:

```bash
# 1. Security audit best practices
# e.g. "Rust security audit checklist 2026 unsafe code production"

# 2. Async performance patterns
# e.g. "Rust async performance optimization 2026 tokio spawn_blocking"

# 3. Supply chain / dependency security
# e.g. "Rust supply chain security cargo audit 2026 dependency management"
```

Capture key findings as a markdown reference. Include:
- Current recommended tools (cargo-deny, cargo-vet, cargo-audit, Cargo Scan)
- Known anti-patterns
- Reference URLs

## Phase 2 — Pattern-Based Code Search

Search for all security and performance patterns across the codebase. Run these searches in parallel using `search_files`:

### Security Patterns

| Pattern | What It Finds | Risk |
|---------|---------------|------|
| `unsafe` | Unsafe blocks — need audit for correctness | Memory safety violations |
| `.unwrap()` | Panic-on-error patterns in production code | Crashes under failure |
| `.expect(` | Assertive unwraps — less risky if descriptive | Lower risk |
| `thread::sleep` | Blocking sleep | Worker thread starvation |
| `std::sync::Mutex` | Sync mutex in async runtime | Contention, deadlock if held across .await |
| `block_on` | Blocking the current thread on async code | Nested runtime, deadlock |
| `api.?key\|API_KEY\|secret\|password` | Hardcoded secrets | Credential leak |
| `include_bytes!` | Embedded binary blobs | Supply chain risk |
| `let _ =` | Swallowed `Result`/`Error` values | Silent data loss, unlogged failures |
| `format!.*SELECT\|.*INSERT\|.*DELETE\|.*UPDATE` | SQL with format!() for identifiers | SQL injection if table names become dynamic |
| `env::var.*path\|env::var.*dir\|env::var.*PATH` | Env var used to construct file paths | Path traversal if env is controllable |
| `private_key.*String` | Private key as plain `String` in structs | Secret exposure via Debug/logs/serialization |
| **Type narrowing/widening** | `as u32`, `as u16`, `as i32` casts — truncation risk | Data loss |
| **`From<u32> for u64` / `Into<u64>`** | Widening: SAFE by default (From impl guaranteed in std) | ✅ Zero risk |
| **`as u64` cast** | Widening via `as`: SAFE (no truncation) but check for op-order bugs | ✅ Safe if arithmetic happens AFTER widening |
| **`as u32` cast from u64** | **Narrowing**: TRUNCATES silently — CRITICAL | Data loss / overflow |
| **`#[serde(untagged)]` enum changes** | Adding/removing variants without compat checks | Deserialization failure |

### Performance Patterns

| Pattern | What It Finds | Risk |
|---------|---------------|------|
| `spawn_blocking` | Proper async offloading | ✅ Positive — count usage |
| `thread::sleep` | Blocking in async | Worker thread starvation |
| `std::sync::Mutex` (in async) | Non-yielding locks | Throughput degradation |
| `.clone()` inside hot paths | Unnecessary allocations | Memory churn |
| `DashMap` | Concurrent map | Usually fine, check for iter() across await |
| `for m in &db.metrics` | Linear scans | O(n) on every operation |

### Search Template (Rust projects)

```bash
# Run all in parallel (concurrent tool calls in Hermes)
search_files(pattern="unsafe", file_glob="*.rs", path="/path/to/repo")  # Security
search_files(pattern="\\.unwrap\\(\\)", file_glob="*.rs", path="/path/to/repo")  # Security
search_files(pattern="\\.expect\\(", file_glob="*.rs", path="/path/to/repo")  # Security
search_files(pattern="thread::sleep", file_glob="*.rs", path="/path/to/repo")  # Perf/Sec
search_files(pattern="std::sync::Mutex", file_glob="*.rs", path="/path/to/repo")  # Perf/Sec
search_files(pattern="spawn_blocking", file_glob="*.rs", path="/path/to/repo")  # Perf (positive)
search_files(pattern="block_on", file_glob="*.rs", path="/path/to/repo")  # Security
search_files(pattern="api.?key|API_KEY|secret|password", file_glob="*.rs", path="/path/to/repo")  # Security
search_files(pattern="let _ =", file_glob="*.rs", path="/path/to/repo")  # Swallowed errors
search_files(pattern="format!.*SELECT|format!.*INSERT|format!.*DELETE|format!.*UPDATE", file_glob="*.rs", path="/path/to/repo")  # SQL injection
search_files(pattern="env::var.*path|env::var.*dir|env::var.*PATH", file_glob="*.rs", path="/path/to/repo")  # Env path injection
search_files(pattern="private_key.*String|secret.*String|api_key.*String", file_glob="*.rs", path="/path/to/repo")  # Secret as String
```

## Phase 3 — Deep Reading of Candidate Files

For files matching critical patterns, read the full context around matches:

1. **unsafe blocks** — verify safety invariants, check for soundness holes
2. **unwrap/expect in production** — distinguish test code from production code paths
3. **thread::sleep** — identify whether it's inside an `async fn` or tokio task
4. **std::sync::Mutex** — check if locks are held across `.await` points
5. **Hardcoded secrets** — confirm whether they're test placeholders or real credentials

### Classification Rules

- **Test code** (`#[cfg(test)]`, `tests/` directory) — lower severity, note it
- **Production code** — full severity
- **Non-async functions** — `thread::sleep` is acceptable (not an async violation)
- **Async functions / tokio::spawn** — `thread::sleep` is critical

## Phase 4 — Finding Documentation

For each confirmed finding, document:

```
### ID [S/P]-[NN] [SEVERITY] [Brief Title]
- **File:** path/to/file.rs:line_number
- **Code:** relevant code snippet (5-10 lines)
- **Risk:** what could go wrong in production
- **Fix:** specific change needed
```

### Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| 🔴 **CRITICAL** | Blocks worker thread, crashes on failure path, or exposes secrets | Fix immediately before merge |
| 🟡 **HIGH** | Risk of deadlock/panic under specific conditions, or design flaw | Fix before next release |
| 🟢 **MEDIUM** | Suboptimal pattern, no immediate danger but tech debt grows | Schedule for next sprint |
| ⚪ **LOW** | Minor concern, acceptable at current scale | Note for future refactoring |

### Strong Points

Also document what the codebase does **right** — reinforces good practices:

```
Security:
- ✅ API keys from environment variables
- ✅ No SQL injection (parameterized queries)
- ✅ spawn_blocking properly used on all SQLite operations

Performance:
- ✅ virtual_fs.rs: correct spawn_blocking on all 7 operations
- ✅ health.rs: clean async patterns, no thread::sleep
```

## Phase 5 — Issue/Report Creation

Create the deliverable as a structured GitHub issue or report:

```bash
# Title format
[AUDIT-{N}-{NN}] {Category} — {Ola/Wave Name}

# Labels: audit, {ola/wave name}
gh issue create \
  --title "[AUDIT-5-02] Security + Performance — Ola 5" \
  --label "audit,ola5" \
  --body '<structured report>'
```

### Report Structure

1. **Header** — target commit, stats, reviewer, date
2. **Web Research Summary** — 3 queries with key findings
3. **Security Findings** — grouped by severity (CRITICAL → LOW)
4. **Performance Findings** — grouped by severity
5. **Strong Points** — what the codebase does right
6. **Summary Table** — ID, Category, Severity, Files, Description
7. **Recommendations** — priority-ordered fix list
8. **References** — URLs from web research

## Pitfalls

- **Don't skip web research** — best practices evolve fast (async patterns, tooling). Always ground the audit in current standards.
- **Distinguish test vs production code** — `unwrap()` in tests is acceptable; in production paths it's a bug.
- **Don't flag `std::sync::Mutex` blindly** — it's safe if never held across `.await`. Check the actual usage pattern.
- **`spawn_blocking` has overhead** — don't recommend it for trivial sync operations (micro-second range). Use judgment on the tradeoff.
- **Don't report every `.clone()`** — focus on clones in hot async paths or tight loops.
- **Don't report every `unsafe`** — some FFI/OS calls are inherently unsafe and well-understood (libc::kill, libc::getuid). Focus on Rust level-2 unsafety (pointer deref, layout assumptions).
- **Supply chain audit** requires `cargo audit` + `cargo deny` — recommend adding these to CI, not just running once.
- **Swallowed errors (`let _ =`) are easy to miss** — they don't produce warnings. Always run `search_files(pattern="let _ =", ...)` as part of the security scan. Categorize by intent: fire-and-forget (acceptable) vs persistence/IO (flag).
- **Test assertions with `|| true` are dead tests** — search for `|| true` in test code. If an assertion includes `|| true`, it can never fail. This is a silent CI gap.
- **Hardcoded test secrets behind feature gates** — if a `#[cfg(feature = "X")]` module contains hardcoded keys, and that feature can be enabled in release builds, the key is in the production binary. Verify feature gating matches build profiles.
- **Env var file paths without validation** — `PathBuf::from(env::var("SOME_DIR")?)` is a path traversal vector if the env is controllable. Always validate or sanitize env-derived paths.
- **One fixed instance of a copy-pasted pattern is not a fix** — after finding an expensive or unsafe pattern, grep its siblings before declaring it resolved: `grep -rc 'store\.get(' src/<component>/ | grep -v ':0'`. Count > 1 in files you did not touch means you found an instance of an N-instance bug. The suite will stay green either way, because it tests each module in isolation and each is correct about itself.
- **A green suite plus an unchanged symptom means the live process is the only oracle left** — read its own output (`journalctl -u <svc> --since '10 min ago' | grep <stage>`) to see which stage actually costs. A loop that logs stages A, B, C and never reaches D localises the cost precisely, and reveals that the stage you just fixed was never the expensive one.
- **Deploying a release build with a reduced feature set silently drops subsystems** — a CI-safe feature set can exclude the TUI, webhook or notification code the running node depends on, and the binary still builds and passes every gate. Diff meaningful symbols (counts of a feature's types) between the newly built binary and the installed one before overwriting it; file size is a hint, not proof.

## Issue/Report Creation — Summary Table Format

When creating the audit issue/report, include a summary table at the bottom of each section and a consolidated table at the end. Use the PASS/PASS/CRITICAL/HIGH scoring:

```markdown
| ID | Category | Severity | Files | Description |
|----|----------|----------|-------|-------------|
| S-01 | Security | PASS | ingest.rs, models.rs | Type widening u32→u64: SAFE. JSON compat preserved |
| S-02 | Security | PASS | models.rs | f64 consistency: already correct |
| S-03 | Security | PASS | run.rs | Dead code removal: 76 LOC removed |
| S-04 | Security | PASS | docs/ | Docs updated: references corrected |
| P-01 | Performance | PASS | models.rs | Compile impact: negligible (+71 LOC) |
| D-01 | Dependencies | PASS | Cargo.toml | tokio 1.37→1.49: semver-compatible |
```

### Critical: authorization that is opt-in per layer

A guard that each layer must remember to install is not a guard. Audit for the shape, not the individual check:

| Anti-pattern | Why it fails | Correct form |
|---|---|---|
| `match path { … _ => true }` in a scope/permission check | Every route nobody classified inherits *allowed* | Derive the requirement from method+path into an enum (`Read`/`Write`/`RootOnly`); unknown route falls to the strictest sane default |
| `fn authorize(..) -> Result<..> { Ok(()) }` with a "scaffolding" comment | Reads like a policy, approves everything, and its only caller may pass `Uuid::nil()` so it could never deny | Fail closed (`Err`), and delete the call site |
| Per-route `.layer(middleware::from_fn(gate))` | Forgetting the layer ships the route open | `route_layer` on the whole sub-router: gated by construction |
| Permission trait where a new capability reuses a broad existing method | Any holder of the broad method silently gains the capability | Add an explicit method per capability, narrowest role first |
| A wildcard bind (`0.0.0.0`) on a service that serves authenticated routes | Publishes the auth surface to every interface; a loopback default is the one a reviewer can verify | Loopback default; widening must be an explicit, documented opt-in |
| Capability token (lease/short-lived) usable as a general session | Handed to a subprocess for one call, becomes node-wide access | Constrain it to the one path prefix it exists for |
| `.unwrap_or(true)` / `.unwrap_or(default_allow)` on a rate-limit or policy check | Fails open on error | Fail closed (`unwrap_or(false)`) |

**Also verify the gate is real at the router level**, not just at the handler: grep the registration site and confirm every route in the sensitive family is covered by the gate function, and that the tests build their router from that same function.

## Verdict Line

End with a clear overall verdict:

```markdown
## VERDICT

**Overall: ✅ PASS** — No security vulnerabilities found. All changes are safe and correct.
```

Or for findings:

```markdown
## VERDICT

**Overall: ⚠️ ISSUES FOUND** — 2 CRITICAL, 3 HIGH, 1 MEDIUM. See Recommendations section.
```

---

## Common Rust Audit Patterns

### Critical: `thread::sleep` in async context

```rust
// ❌ BAD — blocks the tokio worker thread
async fn integrate_branches() {
    std::thread::sleep(policy.backoff);  // BLOCKS!
}

// ✅ GOOD — yields to the runtime
async fn integrate_branches() {
    tokio::time::sleep(policy.backoff).await;  // Yields
}
```

### High: `std::sync::Mutex` in async with .await

```rust
// ❌ DANGEROUS — lock held across .await
async fn bad() {
    let guard = my_mutex.lock().unwrap();
    do_something_async().await;  // Lock held! Deadlock risk!
}

// ✅ SAFE — brief synchronous scope
async fn good() {
    let value = {
        let guard = my_mutex.lock().unwrap();
        guard.clone()  // Clone before releasing
    };
    do_something_async().await;  // Lock already released
}
```

### High: `.unwrap()` on poisoned mutex

```rust
// ❌ BAD — panics if another thread panicked
let conn = self.conn.lock().unwrap();

// ✅ GOOD — propagates error
let conn = self.conn.lock().map_err(|e| ...)?;
```

### High: Swallowed errors with `let _ =`

```rust
// ❌ BAD — silent data loss on persistence failure
let _ = self.save_state();

// ✅ GOOD — log and propagate or at minimum warn
if let Err(e) = self.save_state() {
    tracing::warn!("Failed to persist DAO state: {:?}", e);
}
```

**When auditing:** Count `let _ =` instances. Categorize:
- Event publishing / fire-and-forget → acceptable (note as INFO)
- DB/file persistence → flag as MEDIUM-HIGH (silent data loss)
- Error propagation from fallible ops → flag as HIGH

### Medium: Hardcoded secrets in test code

```rust
// ❌ DANGEROUS — real key in test, could leak if feature gate is enabled in prod
#[cfg(feature = "dao-evm")]
private_key: "0x<64-hex-key>" // e.g. a hardcoded Hardhat default account key

// ✅ BETTER — use env var or fixture
private_key: std::env::var("TEST_EVM_PRIVATE_KEY").expect("set TEST_EVM_PRIVATE_KEY")
```

**Key question:** Is the `#[cfg(feature = "...")]` gate compiled into production builds? If the feature can be enabled in release, the test key is in the binary.

### Medium: Private key as plain String in structs

```rust
// ❌ Secret exposed via Debug, Serialize, Clone
#[derive(Debug, Clone, Serialize)]
pub struct EvmDaoConfig {
    pub private_key: String,  // leaks in logs, error messages
}

// ✅ Use secrecy crate or suppress Debug
pub struct EvmDaoConfig {
    #[serde(skip)]
    private_key: secrecy::SecretString,
}
```

### Medium: Governance / DAO state persistence gaps

```rust
// ❌ In-memory only — data lost on restart
pub struct GovernanceDao {
    proposals: HashMap<String, Proposal>,
    // no save/load mechanism
}

// ✅ Persistence layer required for production governance
```

**When auditing governance modules, check:**
1. Is state persisted to disk/DB? (HashMap-only = data loss on restart)
2. Are save operations error-handled? (silent `let _ =` = divergence)
3. Are Mutex unwraps in global state functions? (deadlock if poisoned)
4. Is there a credit/balance system? (verify credits are deducted, not just checked)

### Medium: Blocking I/O in async context

```rust
// ❌ BAD — blocks worker thread
pub async fn record_metrics(&self, metrics: ExecutionMetrics) -> Result<()> {
    let mut db = self.read_db();  // std::fs inside async fn!
    db.metrics.push(metrics);
    self.write_db(&db)?;
    Ok(())
}

// ✅ GOOD — offloads to blocking pool
pub async fn record_metrics(&self, metrics: ExecutionMetrics) -> Result<()> {
    let db_path = self.db_path.clone();
    tokio::task::spawn_blocking(move || {
        let mut db = read_db(&db_path)?;
        db.metrics.push(metrics);
        write_db(&db_path, &db)
    })
    .await??;
    Ok(())
}
```

### PASS: Dependency Version Bump Verification

When a dependency version is bumped (e.g., tokio 1.37→1.49), verify:

```bash
# 1. Check if semver-compatible (same major version)
#    1.37 → 1.49: minor bump within same major → SHOULD be compatible

# 2. Check if other workspace crates already use the newer version
grep -rn 'tokio.*version' */Cargo.toml | grep -v 'Cargo.lock'

# 3. Check Cargo.lock impact
git diff HEAD~1..HEAD -- Cargo.lock | head -20

# 4. Check if features changed
#    e.g., tokio = { version = "1.49", features = ["full"] }
#    vs tokio = { version = "1.37", features = ["full"] }
```

**Assessment criteria:**
- ✅ Same major version: SAFE (semver guarantees backward compatibility)
- ✅ Same feature set: SAFE (no feature flag changes)
- ✅ Aligns with workspace: POSITIVE (reduces version drift)
- ⚠️ Feature set changed: needs review (new features might pull in new transitive deps)
- 🔴 New major version (2.x): BREAKING — requires full API audit
- 🔴 Feature removed: BREAKING — check if the code uses the removed feature

### PASS: Docs Update Verification

When docs files change alongside code, verify accuracy:

```bash
# 1. List all docs files changed
git diff HEAD~1..HEAD --name-only | grep '\.md$'

# 2. Check workspace member consistency
grep -A 20 '\[workspace\]' Cargo.toml

# 3. Check ARCHITECTURE.md crate map matches workspace
grep -E '^| `.*` \|' ARCHITECTURE.md 2>/dev/null

# 4. Check AGENTS.md claims against Cargo.toml
#    e.g., "gestalt_swarm is excluded" → verify it's NOT in workspace members
```

**Assessment criteria:**
- ✅ Workspace members match doc claims: PASS
- ⚠️ Discrepancy found: file issue (DOCS severity) to fix docs
- 🔴 Major disconnect (docs say excluded, Cargo.toml includes): CRITICAL for CI

### PASS: Type Widening Analysis (u32→u64)

In Rust, widening conversions are ALWAYS safe — the standard library provides `From<u32> for u64`. When auditing code that changes field types from u32 to u64:

**Key verification points:**
1. **Is the cast safe?** u32→u64 via `From`/`Into` or `as` — YES, always safe (no truncation possible)
2. **Is JSON serialization backward-compatible?** YES — JSON numbers are arbitrary precision; u32 and u64 both serialize as integers
3. **Are there operation-order bugs?** Check if arithmetic happens on the narrower type BEFORE widening:
   ```rust
   // ❌ Operates on u32 before widening — overflow risk
   let result = (x + y) as u64;   // x+y overflows as u32 first
   
   // ✅ Widens before arithmetic — no overflow
   let result = (x as u64) + (y as u64);
   ```
4. **Are the values realistic?** For priorities (50, 100, 150), both u32 and u64 are fine

**When to flag:**
- 🔴 Narrowing (u64→u32) without checked conversion — silent truncation
- 🔴 Operation-order bug — u32 arithmetic before widening
- ✅ Widening (u32→u64) — always PASS, document as safe

## Referencias

1. **RustSec**: https://rustsec.org/ — Security advisory database for Rust.
2. **cargo-audit**: https://github.com/rustsec/rustsec — Audit dependencies for known vulnerabilities.
3. **subtle crate**: https://docs.rs/subtle/latest/subtle/ — Constant-time comparisons (timing attack prevention).
4. **Tokio Shared State**: https://tokio.rs/tokio/tutorial/shared-state — Patterns for thread-safe state in async.
5. **Rust Cheatsheet (Unsafe)**: https://cheats.rs/#unsafe — Unsafe code patterns reference.
6. **cargo-deny**: https://github.com/EmbarkStudios/cargo-deny — Deny criteria for dependencies.
7. **cargo-vet**: https://github.com/nickel-org/cargo-vet — Supply chain verification.
8. **Rust Secure Code**: https://rust-secure-code.github.io/ — Security guidelines for Rust.

---

*Rust Code Security & Performance Audit — v1.1.0 (with references)*
