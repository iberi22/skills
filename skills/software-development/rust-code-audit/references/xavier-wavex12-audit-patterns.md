# Xavier Codebase Audit Patterns (WAVEX-12, 2026-07-31)

## Key Findings Summary

Audit of 631 Rust files (~125K LOC) focusing on mesh/governance/pricing/acl/dashboard/discovery modules.

### Patterns Discovered

#### 1. Swallowed `save_state()` in Governance DAO
- **File**: `src/governance/mod.rs` (12 instances)
- **Pattern**: `let _ = self.save_state();` after every state mutation
- **Impact**: Silent divergence between in-memory and on-disk state
- **Fix**: Log the error at minimum: `if let Err(e) = self.save_state() { tracing::warn!(...) }`

#### 2. Mutex `.unwrap()` in Global Governance State
- **File**: `src/governance/mod.rs:62,75,86,106,115`
- **Pattern**: `get_quadratic_state().lock().unwrap()` in public functions
- **Risk**: Production deadlock if any thread panics while holding lock
- **Fix**: `.lock().unwrap_or_else(|e| e.into_inner())` or return `Result`

#### 3. Hardcoded EVM Private Key in Tests
- **File**: `src/mesh/governance/mod.rs:268,284,302,318`
- **Pattern**: `private_key: "0xac0974..."` in `#[cfg(feature = "dao-evm")]` tests
- **Risk**: Key in binary if feature enabled in release builds
- **Fix**: Use env var or dedicated test fixture

#### 4. Private Key as Plain String
- **File**: `src/mesh/governance/onchain.rs:29`
- **Pattern**: `pub private_key: String` with `#[derive(Debug, Clone)]`
- **Risk**: Key exposure via Debug output, error messages, serialization
- **Fix**: Use `secrecy::SecretString` or suppress Debug

#### 5. Dead Test Assertion
- **File**: `src/mesh/discovery.rs:221-222`
- **Pattern**: `assert!(discovered || ... || true)` — always passes
- **Fix**: Remove `|| true`

#### 6. Env Var Path Without Validation
- **File**: `src/mesh/acl.rs:35-42`
- **Pattern**: `PathBuf::from(env::var("XAVIER_CONFIG_DIR")?)` → `save()` writes to it
- **Risk**: Path traversal if env controllable

#### 7. SQL format!() for Table Names
- **Files**: `src/notifications/mod.rs:80,425,437,447`, `src/memory/sqlite_store.rs:399`
- **Pattern**: `format!("INSERT INTO {}", TABLE_NAME)` — safe now (constants) but anti-pattern

#### 8. GovernanceDao Has No Persistence
- **File**: `src/governance/dao.rs` (entire file)
- **Pattern**: Pure in-memory HashMap, no save/load
- **Risk**: Data loss on restart

#### 9. No Rate Limiting on Governance Voting
- **Files**: `src/governance/dao.rs:129-164`, `src/governance/mod.rs:80-101`
- **Pattern**: Credits user-provided, not deducted from balance
- **Risk**: Infinite voting with fabricated credits

### Positive Patterns Found

- **PII scrubbing**: `src/mesh/telemetry.rs` — regex-based PII redaction with LazyLock
- **Parametrized SQL**: `enterprise/persistence.rs` — all queries use `params![]` macro
- **ACL hierarchy with cycle detection**: `security/acl/hierarchy.rs` — DAG validation
- **Token authentication with Ed25519**: `mesh/auth.rs` — proper signature verification
- **RwLock with graceful fallback**: `mesh/auth.rs:157-172` — defaults to deny on poisoned lock

### Severity Distribution

| Severity | Count | Theme |
|----------|-------|-------|
| CRITICAL | 2 | Secret management |
| HIGH | 4 | Panic/deadlock risks + silent data loss |
| MEDIUM | 6 | Dead test, no persistence, env injection, no rate limiting |
| LOW | 5 | Swallowed errors, hardcoded arrays, inaccurate metrics |

### Audit Methodology Notes

1. **File discovery**: `find` + `grep` to locate WAVEX-12 new code
2. **Parallel reads**: Read 8 files simultaneously for initial context
3. **Pattern search**: 6 parallel `search_files` calls for unwrap, SQL, secrets, `let _ =`
4. **Deep dive**: Read continuation of critical files (auth.rs:150-299, governance.rs:500-900)
5. **Report**: Structured severity table with file:line references
