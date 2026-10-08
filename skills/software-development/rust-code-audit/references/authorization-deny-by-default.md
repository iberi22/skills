# Auditing and Fixing Authorization in an Axum/Rust Service

Topical reference for the "authorization is opt-in, so new routes ship open" class of finding.
Applies to any HTTP service that gates some routes and not others.

## Why the finding is structural, not a missing line

Most services have several plausible-looking authorization layers (a scope check in middleware, an
RBAC call, a per-route gate). Each one approves by default and trusts another to deny. The
resulting bug is not "someone forgot a check" — it is that **a new route inherits "allowed"
because nobody had to make a decision about it**. Any fix that only adds the missing check leaves
the trap armed for the next route.

So the audit question is not "is this route protected?" but "**what happens to a route that nobody
classified?**" Trace that and you find the whole class.

## Layer-by-layer audit

### 1. Scope/token layer

Look for a match on the request path whose fallthrough arm allows:

```rust
// ❌ the arm that makes the whole thing worthless
let has_scope = match path {
    "/memory/search" => scopes.contains("read"),
    "/memory/add"    => scopes.contains("write"),
    _ => true, // default allow
};
```

Any `_ => true` (or `unwrap_or(true)`, or `HashSet::contains(...).then(...).unwrap_or(true)`) is a
finding regardless of how correct the other arms are.

Fix — invert to a requirement, not an allowlist. An enum cannot be extended by accident:

```rust
pub enum RequiredScope { Read, Write, RootOnly } // RootOnly: no scope unlocks it, not even `all`

pub fn required_scope(method: &Method, path: &str) -> RequiredScope {
    if ROOT_ONLY_PREFIXES.iter().any(|p| path.starts_with(p)) { return RequiredScope::RootOnly; }
    if matches!(*method, Method::GET | Method::HEAD | Method::OPTIONS)
        || READ_ONLY_POST_PREFIXES.iter().any(|p| path.starts_with(p)) { RequiredScope::Read }
    else { RequiredScope::Write }
}

pub fn token_satisfies(scopes: &[String], required: &RequiredScope) -> bool {
    match required {
        RequiredScope::RootOnly => false,
        RequiredScope::Read  => scopes.iter().any(|s| s == "read" || s == "all"),
        RequiredScope::Write => scopes.iter().any(|s| s == "write" || s == "all"),
    }
}
```

Name the root-only prefixes explicitly. Note the prefix semantics: `"/secrets/"` with the trailing
slash is deliberate and worth a test, because `"/secretsomething"` must not match.

### 2. The "RBAC" stub

```rust
// ❌ reads like a policy, approves everything
pub fn authorize(_user_id: Uuid, action: Permission, _r: String) -> Result<(), RbacError> {
    // scaffolding: assume success
    Ok(())
}
```

Two things to check before judging it: **how many production call sites does it have**, and what
identity do those callers pass. A single call site passing `Uuid::nil()` means it could not have
denied anyone even in principle — the "enforcement" was decorative.

Fix: make it fail closed (`Err(RbacError::PermissionDenied(action))`) and delete the call sites
rather than leaving a landmine. A function that always errors is self-documenting; a function that
always succeeds under a name like `authorize` is the problem.

### 3. Route gate

Per-route `.layer(middleware::from_fn(gate))` means each new `.route()` needs a matching layer
remembered. Put the gate on the **whole sub-router** instead:

```rust
pub(crate) fn secrets_routes() -> Router<CliState> {
    Router::new()
        .route("/a", post(handler_a))
        .route("/b", post(handler_b))
        .route_layer(middleware::from_fn(require_permission(check)))  // covers a and b, and whatever comes next
}
```

Add `#[deny(dead_code)]` to the constructor: it makes "the server stopped registering these routes"
a **build error** rather than a silently-open surface.

### 4. Identity vs authority

Enumerated credentials that all collapse to one role make "authenticated" mean "can do everything
not explicitly closed". Check what each principal type maps to: a lease/capability token, an
ephemeral session, and a long-lived API token should not all become the same `UserRole::User`.

Constrain a capability token to the path prefix it exists for:

```rust
pub fn lease_may_access(path: &str) -> bool { path.starts_with("/v1/proxy/") }
```

A capability handed to a subprocess for one outbound call must not double as a node-wide session.

### 5. Bind address

A service serving authenticated routes on `0.0.0.0` is published to every interface, so every
authorization gap becomes network-reachable. Loopback is the default that a reviewer can verify;
widening must be explicit. Check the *runtime* source of the bind value, not only the code default —
a config file that overrides a safe code default removes the protection while the code still looks
correct. If a comment claims a secure default, verify the code actually does it; a reassuring
comment over a wildcard return is worse than no comment.

## Verifying the fix

Per-route matrix plus a router-level test built from the constructor the server registers:

```rust
for role in [None, Some(UserRole::Readonly), Some(UserRole::User)] {
    for (method, uri, body) in &routes {
        assert_eq!(gated_status(&fx, method, uri, body.clone(), role).await,
                   StatusCode::FORBIDDEN, "{role:?} reached {method} {uri}");
    }
}
```

Include a positive control (Admin succeeds) — a gate that denies everyone also passes a
deny-only test — and, where the handler has a side effect, a filesystem canary asserting the child
process was never spawned. "403" alone does not prove nothing happened.

**Then mutate.** Remove the `route_layer`; the test must go red. Quote the assertion. If it stays
green, the test is exercising a copy of the wiring and the fix is unproven.

Scope-policy functions are pure, so table-test them directly: no scope unlocks a root-only path
(including `all`); an unknown route falls to `Read`/`Write` by method and never to open; existing
memory routes keep their behaviour.
