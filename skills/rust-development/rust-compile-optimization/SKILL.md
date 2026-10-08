---
name: rust-compile-optimization
description: "Use when Rust builds are slow. Applies fast compile fixes."
version: 1.0.0
author: Hermes Agent for belal
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [rust, compile, optimization, speed, cargo, build, performance]
    related_skills: [rust-build-ramdisk, cargo-wizard, rust-workspace-patterns]
    references:
      - url: https://matklad.github.io/2021/09/04/fast-rust-builds.html
        title: "Fast Rust Builds — matklad (author of rust-analyzer)"
        year: 2021
      - url: https://corrode.dev/blog/tips-for-faster-rust-compile-times
        title: "Tips For Faster Rust Compile Times — Matthias Endler"
        year: 2026
      - url: https://xxchan.me/blog/2023-02-17-optimize-rust-comptime-en
        title: "Stupidly effective ways to optimize Rust compile time — xxchan (RisingWave)"
        year: 2023
      - url: https://doc.rust-lang.org/cargo/guide/build-performance.html
        title: "Optimizing Build Performance — The Cargo Book (official)"
        year: 2026
      - url: https://davidlattimore.github.io/posts/2024/02/04/speeding-up-the-rust-edit-build-run-cycle.html
        title: "Speeding up the Rust edit-build-run cycle — David Lattimore"
        year: 2024
---

# Rust Compile Optimization — Técnicas para Maximizar Velocidad de Compilación

## Cuándo usar

- El proyecto Rust compila lento (>30s para check, >2min para build)
- El agente necesita optimizar tiempos de compilación para productividad
- Configurar CI/CD más rápido para repos Rust
- Diagnosticar por qué un workspace específico es lento
- Antes de crear un skill de build o CI para un proyecto Rust

## Regla de oro

> "Compilation time is a multiplier for basically everything. One minute of work for the compiler wastes more than one minute of work for the human." — matklad

## Técnicas por impacto (mayor a menor)

### 1. `cargo check` > `cargo build` (2-3x más rápido)

Para detectar errores, NO necesitas compilar el binario completo:

```bash
# ❌ Lento — compila todo el binario
cargo build

# ✅ Rápido — solo type-checking
cargo check

# ✅ Para tests
cargo check --tests
```

**Cuándo usar:** Durante desarrollo iterativo, antes de commit, en CI para fast-fail.

### 2. `cargo nextest` > `cargo test` (2-5x más rápido)

Test runner paralelo, mucho más rápido:

```bash
# Instalar
cargo install cargo-nextest

# Usar
cargo nextest run
cargo nextest run --workspace
cargo nextest run -p my-crate
```

**Por qué es más rápido:** Ejecuta tests en procesos paralelos separados (cada test en su propio proceso).

### 3. Linker rápido (30-50% menos tiempo de linking)

El linker es el cuello de botella #1 en proyectos grandes:

```toml
# .cargo/config.toml
[target.'cfg(target_os = "linux")']
# mold (el más rápido, requiere GCC 12+)
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]

# Alternativa: lld (más maduro, production-ready)
# linker = "clang"
# rustflags = ["-C", "link-arg=-fuse-ld=lld"]
```

```bash
# Instalar mold (NixOS)
nix-shell -p mold

# Verificar
mold --version
```

### 4. `sccache` — Cache de compilación (20-40% en rebuilds)

Cachea compilaciones individuales de crate entre builds:

```bash
# Instalar
cargo install sccache

# Configurar
export RUSTC_WRAPPER=sccache

# Verificar
sccache --show-stats
```

### 5. `cargo-machete` — Eliminar dependencias no usadas

Cada dependencia no usada compila código innecesariamente:

```bash
# Instalar
cargo install cargo-machete

# Ejecutar
cargo machete

# Auto-fix (remueve dependencias no usadas de Cargo.toml)
cargo machete --fix
```

### 6. Feature flags — Deshabilitar features pesadas

Muchas dependencias traen features pesadas por defecto:

```toml
# ❌ Trae TODO: serde, tokio full, hyper, etc.
tokio = { version = "1", features = ["full"] }

# ✅ Solo lo que necesitas
tokio = { version = "1", features = ["rt", "macros", "net"] }
```

```bash
# Verificar features activas
cargo tree -e features
```

### 7. `cargo hakari` — Workspace-hack technique

Reduce rebuilds en workspaces al unificar features:

```bash
# Instalar
cargo install cargo-hakari

# Generar workspace-hack crate
cargo hakari generate

# Integrar en CI
cargo hakari check
```

### 8. Split crates — Workspaces para paralelización

Si un crate es muy grande, dividirlo en workspaces:

```toml
# Cargo.toml
[workspace]
members = ["core", "api", "cli"]
```

**Beneficio:** Cargo compila crates hermanos en paralelo.

### 9. `cargo llvm-lines` — Detectar monomorphization bloat

Los generics monomorphizados inflan el tiempo de compilación:

```bash
# Instalar
cargo install cargo-llvm-lines

# Analizar
cargo llvm-lines --lib --release -p my-crate | head -20
```

**Qué buscar:** Funciones con alto número de "copies" (monomorphization).

### 10. Evitar proc macros pesadas

Las proc macros son el cuello de botella #1:

```bash
# Encontrar proc macros lentas
cargo build --timings
```

**Alternativas:**
- `serde` → `nanoserde` (más rápido, menos features)
- `diesel` → `sqlx` (compile-time checked queries)
- `thiserror` → `derive_more` o manual impl

### 11. Parallel frontend (nightly)

```toml
# .cargo/config.toml
[build]
rustflags = "-Zthreads=8"
```

**⚠️ Requiere nightly.** Compila el frontend del compilador en paralelo.

### 12. `cargo-watch` — Rebuild automático

```bash
# Instalar
cargo install cargo-watch

# Watch mode
cargo watch -c -x check
cargo watch -c -x test
cargo watch -c -x "test -- --lib"
```

### 13. Cranelift — Compilador alternativo (debug builds)

```bash
# Instalar
rustup component add rustc-codegen-cranelift-preview

# Usar (debug builds más rápidos)
export CARGO_PROFILE_DEV_CODEGEN_BACKEND=cranelift
cargo build
```

**⚠️ Solo para debug builds.** Release builds usan LLVM.

### 14. `cargo-chef` — Docker builds optimizados

```dockerfile
FROM rust:1.75 as planner
WORKDIR /app
RUN cargo install cargo-chef
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

FROM rust:1.75 as cacher
WORKDIR /app
RUN cargo install cargo-chef
COPY --from=planner /app/recipe.json recipe.json
RUN cargo chef cook --release --recipe-path recipe.json

FROM rust:1.75 as builder
WORKDIR /app
COPY . .
COPY --from=cacher /app/target target
RUN cargo build --release
```

### 15. Incremental compilation

```toml
# .cargo/config.toml
[profile.dev]
incremental = true  # Default en debug, más rápido para edits pequeños

[profile.release]
incremental = false  # Release no necesita incremental
```

## Diagnóstico: Encontrar el cuello de botella

```bash
# 1. Ver tiempos por crate
cargo build --timings
# Abre target/cargo-timing.html en el navegador

# 2. Ver dependencias
cargo tree --depth 1

# 3. Ver features activas
cargo tree -e features

# 4. Contar líneas generadas (monomorphization)
cargo llvm-lines --lib -p my-crate | head -20
```

## Configuración óptima para NixOS (tu setup)

```toml
# .cargo/config.toml
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]

[build]
jobs = 8  # Paralelizar compilación de crates

[profile.dev]
incremental = true

[profile.release]
incremental = false
lto = "thin"
codegen-units = 1
```

```bash
# Shell.nix óptimo
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    cargo rustc rustfmt clippy
    cargo-nextest cargo-machete cargo-hakari cargo-llvm-lines
    cargo-watch cargo-chef
    mold lld  # Linkers rápidos
    sccache   # Cache de compilación
  ];

  shellHook = ''
    export RUSTC_WRAPPER=sccache
    echo "✅ Rust compile optimization ready"
  '';
}
```

## Referencias

1. **matklad (Fast Rust Builds)**: https://matklad.github.io/2021/09/04/fast-rust-builds.html — El guide definitivo. 200k LOC Rust = ~10min CI en GitHub Actions optimizado.
2. **Corrode (Tips for Faster Compile Times)**: https://corrode.dev/blog/tips-for-faster-rust-compile-times — Lista completa actualizada 2026.
3. **xxchan (RisingWave optimizations)**: https://xxchan.me/blog/2023-02-17-optimize-rust-comptime-en — Optimizaciones reales que redujeron CI de 40min a 16min.
4. **Cargo Book (Build Performance)**: https://doc.rust-lang.org/cargo/guide/build-performance.html — Documentación oficial.
5. **David Lattimore**: https://davidlattimore.github.io/posts/2024/02/04/speeding-up-the-rust-edit-build-run-cycle.html — Benchmark-driven approach.
6. **mold linker**: https://github.com/rui314/mold — Linker más rápido para Linux.
7. **sccache**: https://github.com/mozilla/sccache — Cache de compilación distribuido.
8. **cargo-nextest**: https://github.com/nextest-rs/nextest — Test runner paralelo.
9. **cargo-machete**: https://github.com/bnjbvr/cargo-machete — Detecta dependencias no usadas.
10. **cargo-hakari**: https://github.com/gankra/cargo-hakari — Workspace-hack technique.

## Pitfalls

| Problema | Causa | Solución |
|----------|-------|----------|
| mold no funciona | GCC <12 o no instalado | `nix-shell -p mold` o usar lld como fallback |
| sccache no acelera | No hay rebuilds significativos | sccache brilla en CI, menos en dev local incremental |
| nextest falla tests | Tests dependen de estado compartido | `cargo nextest run --failure-continue` o testificar |
| Cranelift panic | Feature no soportada | Fallback a LLVM automáticamente |
| Hakari genera diffs | Features cambiaron | `cargo hakari generate` de nuevo |
| TIMINGS no muestra timings | Solo con `cargo build` | Usar `cargo build --timings` explícitamente |

---

*Rust Compile Optimization — v1.0.0*
