---
name: rust-workspace-patterns
description: "Use when structuring Rust workspaces. Layouts and splits."
version: 1.0.0
author: Hermes Agent for belal
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [rust, workspace, patterns, organization, architecture, dependency, feature-flags]
    related_skills: [rust-compile-optimization, cargo-wizard, rust-code-quality-audit]
    references:
      - url: https://doc.rust-lang.org/cargo/reference/workspaces.html
        title: "Cargo Workspaces — Official Documentation"
        year: 2026
      - url: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
        title: "Keep Your Architecture Documentation Clean — matklad"
        year: 2021
      - url: https://rust-lang.github.io/api-guidelines/
        title: "Rust API Guidelines — C-CARGO"
        year: 2026
      - url: https://github.com/rust-derive-eq/example-project
        title: "Example Rust Workspace Project Structure"
        year: 2024
---

# Rust Workspace Patterns — Organización de Código y Dependencias

## Cuándo usar

- Organizar un proyecto Rust con múltiples crates
- Decidir cómo dividir un monolito en workspaces
- Gestionar dependencias compartidas entre crates
- Configurar feature flags para compilación condicional
- Crear un workspace desde cero con estructura correcta
- Auditar la organización de un workspace existente

## Estructura canónica de un workspace

```
my-project/
├── Cargo.toml              # Workspace root
├── crates/
│   ├── core/               # Domain logic (sin dependencias externas pesadas)
│   │   ├── Cargo.toml
│   │   └── src/
│   ├── api/                # HTTP/REST layer (depends on core)
│   │   ├── Cargo.toml
│   │   └── src/
│   ├── cli/                # CLI binary (depends on core + api)
│   │   ├── Cargo.toml
│   │   └── src/
│   └── proto/              # Shared types (seria/JSON schema)
│       ├── Cargo.toml
│       └── src/
├── scripts/                # Build/test scripts
├── .cargo/
│   └── config.toml         # Workspace-wide cargo config
└── README.md
```

## Regla de dependencias: Capas

```toml
# core/Cargo.toml — SIN dependencias de la organización
[dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["rt", "macros"] }

# api/Cargo.toml — DEPENDE de core
[dependencies]
my-project-core = { path = "../core" }
axum = "0.7"
tower = "0.4"

# cli/Cargo.toml — DEPENDE de core + api
[dependencies]
my-project-core = { path = "../core" }
my-project-api = { path = "../api" }
clap = { version = "4", features = ["derive"] }
```

**Regla:** Nunca crear dependencias circulares. `core` no depende de `api` ni `cli`.

## Feature flags para compilación condicional

### En un crate

```toml
# core/Cargo.toml
[features]
default = ["json"]
json = ["serde_json"]
sqlite = ["rusqlite"]
enterprise = []  # Feature vacía para código condicional

[dependencies]
serde_json = { version = "1", optional = true }
rusqlite = { version = "0.31", optional = true }
```

```rust
// core/src/lib.rs
#[cfg(feature = "json")]
pub mod json_support;

#[cfg(feature = "sqlite")]
pub mod sqlite_store;

#[cfg(feature = "enterprise")]
pub mod enterprise_features;
```

### En el workspace

```toml
# Cargo.toml (workspace root)
[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["rt", "macros"] }

# crates heredan la versión exacta del workspace
# core/Cargo.toml
[dependencies]
serde.workspace = true
tokio.workspace = true
```

### Activar features desde CLI

```bash
# Solo con feature "enterprise"
cargo build --features enterprise

# Con múltiples features
cargo build --features "json,sqlite"

# Sin features por defecto
cargo build --no-default-features

# En workspace
cargo build --workspace --features my-crate/enterprise
```

## Patrones de organización

### 1. Proto/Shared types crate

Para tipos compartidos entre frontend (TS/Flutter) y backend (Rust):

```
proto/
├── Cargo.toml
├── src/
│   ├── lib.rs
│   ├── agent.rs      # AgentMessage, AgentState
│   ├── memory.rs     # MemoryEntry, QueryResult
│   └── event.rs      # EventType, EventPayload
├── schemas/          # JSON Schema (generado)
└── scripts/
    └── build.sh      # Genera schemas + types TS
```

```toml
# proto/Cargo.toml
[dependencies]
serde = { version = "1", features = ["derive"] }
schemars = "0.8"  # Para JSON Schema
```

### 2. Adapter pattern (Hexagonal architecture)

```rust
// core/src/ports/mod.rs — Interfaces (trait objects)
pub mod storage {
    pub trait Storage: Send + Sync {
        fn save(&self, key: &str, value: &[u8]) -> Result<()>;
        fn load(&self, key: &str) -> Result<Option<Vec<u8>>>;
    }
}

// adapters/src/sqlite.rs — Implementación concreta
pub struct SqliteStorage {
    conn: rusqlite::Connection,
}

impl core::ports::storage::Storage for SqliteStorage {
    fn save(&self, key: &str, value: &[u8]) -> Result<()> {
        // Implementación SQLite
    }
    // ...
}
```

### 3. Error handling por capa

```rust
// core/src/error.rs — Errores del dominio
#[derive(Debug, thiserror::Error)]
pub enum CoreError {
    #[error("Not found: {0}")]
    NotFound(String),
    
    #[error("Validation failed: {0}")]
    Validation(String),
    
    #[error("Internal error: {0}")]
    Internal(#[from] anyhow::Error),
}

// api/src/error.rs — Errores HTTP (usa core errors)
#[derive(Debug, thiserror::Error)]
pub enum ApiError {
    #[error(transparent)]
    Core(#[from] core::CoreError),
    
    #[error("Unauthorized")]
    Unauthorized,
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        match self {
            ApiError::Core(e) => (StatusCode::INTERNAL_SERVER_ERROR, e.to_string()).into_response(),
            ApiError::Unauthorized => (StatusCode::UNAUTHORIZED, "Unauthorized").into_response(),
        }
    }
}
```

### 4. Config centralizado

```rust
// config/src/lib.rs — Config compartida
use serde::Deserialize;

#[derive(Debug, Deserialize, Clone)]
pub struct AppConfig {
    pub database: DatabaseConfig,
    pub server: ServerConfig,
    pub features: FeatureFlags,
}

#[derive(Debug, Deserialize, Clone)]
pub struct FeatureFlags {
    pub enterprise: bool,
    pub analytics: bool,
}

// Uso en api
pub async fn start_server(config: AppConfig) {
    let app = Router::new()
        .route("/", get(health))
        .with_state(config.server);
}
```

### 5. Test helpers compartidos

```
crates/
├── core/
│   ├── src/
│   └── tests/
│       └── common/
│           └── mod.rs  # Test fixtures
├── api/
│   ├── src/
│   └── tests/
│       └── common/
│           └── mod.rs  # Re-exporta core::tests::common
```

## Gestión de dependencias

### Verificar dependencias no usadas

```bash
# Detectar dependencias no usadas
cargo machete

# Verificar features activas
cargo tree -e features

# Verificar dependencias duplicadas
cargo tree --duplicates
```

### Actualizar dependencias

```bash
# Verificar updates disponibles
cargo outdated

# Actualizar todas
cargo update

# Actualizar una específica
cargo update -p serde
```

### Dependencias del workspace

```toml
# Cargo.toml (workspace root)
[workspace.dependencies]
# Definir versiones una vez
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["rt", "macros"] }

# En crates individuales
# core/Cargo.toml
[dependencies]
serde.workspace = true
tokio.workspace = true
```

## Patrones anti-patrones

### ❌ Monolito gigante

```rust
// src/main.rs — 5000 líneas, TODO mezclado
fn main() {
    // HTTP handlers, DB logic, CLI parsing, business logic...
}
```

### ✅ Workspace separado

```
crates/
├── core/      # Business logic
├── api/       # HTTP layer
├── cli/       # CLI interface
└── proto/     # Shared types
```

### ❌ Dependencias circulares

```toml
# core/Cargo.toml
[dependencies]
my-project-api = { path = "../api" }  # ❌ core no debería depender de api
```

### ✅ Dependency inversion

```rust
// core define el trait
pub trait ApiClient: Send + Sync {
    fn send_request(&self, url: &str) -> Result<Response>;
}

// api implementa el trait
impl ApiClient for ReqwestClient {
    fn send_request(&self, url: &str) -> Result<Response> {
        // reqwest implementation
    }
}
```

## Comandos útiles para workspaces

```bash
# Build todo el workspace
cargo build --workspace

# Test todo el workspace
cargo test --workspace

# Test un crate específico
cargo test -p my-crate

# Clippy en todo
cargo clippy --workspace

# Formatear todo
cargo fmt --all

# Verificar compilación sin build
cargo check --workspace

# Ver miembros del workspace
cargo metadata --format-version 1 | jq '.workspace_members'
```

## Referencias

1. **Cargo Workspaces (Official)**: https://doc.rust-lang.org/cargo/reference/workspaces.html — Documentación oficial de Cargo.
2. **ARCHITECTURE.md (matklad)**: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html — Cómo documentar arquitectura de proyectos Rust.
3. **Rust API Guidelines**: https://rust-lang.github.io/api-guidelines/ — Guidelines para APIs de Rust.
4. **Cargo Book (Workspaces)**: https://doc.rust-lang.org/cargo/book/workspaces.html — Guía de workspaces.
5. **Rust Design Patterns**: https://rust-unofficial.github.io/patterns/ — Patrones de diseño en Rust.
6. **Thiserror**: https://github.com/dtolnay/thiserror — Derive macro para errores.
7. **Anyhow**: https://github.com/dtolnay/anyhow — Error handling para applications.
8. **Schemars**: https://github.com/GREsau/schemars — JSON Schema generation desde Rust.

## Pitfalls

| Problema | Causa | Solución |
|----------|-------|----------|
| "cycle detected" en cargo | Dependencias circulares | Revisar el grafo de dependencias con `cargo tree` |
| Feature unification problem | Features se unen en workspace | Usar `resolver = "2"` en workspace root |
| Test helpers duplicados | Cada crate tiene sus propios fixtures | Crear crate `test-utils` compartido |
| Path dependency hell | Muchos crates con `path = "../"` | Considerar crates.io o git deps para crates estables |
| Stale feature flags | Features que nadie usa | `cargo machete` + revisar `cfg(feature = "...")` en código |
| Build times explode | Workspace muy grande | Split en sub-workspaces o reducir dependencies |

---

*Rust Workspace Patterns — v1.0.0*
