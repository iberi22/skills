---
name: linux-desktop-app-packaging
description: >
  Empaquetar apps de escritorio Linux (Tauri 2) como .deb/.AppImage/.rpm:
  configurar tauri.conf.json (bundle targets, linux deps, metadata), CI en
  GitHub Actions (deps webkit2gtk, pnpm, backend binary artifact), resolver
  conflictos cuando dos PRs crean el mismo workflow, mantener src-tauri fuera
  del workspace raíz, y validar localmente cuando el budget de Actions falla.
version: 1.0.0
author: Hermes Agent
tags: [tauri, linux, packaging, desktop, deb, appimage, github-actions, rust, svelte]
metadata:
  hermes:
    related_skills: [swal-ci-container, ramdisk-multi-project-routing, github-pr-workflow]
---

# Linux Desktop App Packaging (Tauri 2)

Empaquetar una app Tauri 2 (frontend Svelte/React + shell Rust) como app nativa
Linux: backend daemon + frontend de escritorio. Probado en SynapseTrader Wave 6
(2026-08-03) — 4 PRs mergeados, 1 conflicto resuelto.

## Arquitectura típica

```
monorepo/
├── backend/            # Rust daemon (Axum), puerto API local
├── mobile/             # Tauri 2 + Svelte: la app de escritorio
│   ├── src/            # frontend Svelte (vite build)
│   └── src-tauri/      # shell Rust + tauri.conf.json (Cargo.lock PROPIO)
└── .github/workflows/  # linux-desktop.yml (bundle) + pr-validation.yml
```

## tauri.conf.json — config Linux esencial

```json
{
  "productName": "MiApp",
  "identifier": "com.org.app",
  "bundle": {
    "active": true,
    "targets": ["deb", "appimage", "rpm"],
    "category": "Finance",
    "shortDescription": "...",
    "longDescription": "...",
    "publisher": "...",
    "copyright": "AGPL-3.0",
    "homepage": "https://github.com/...",
    "linux": {
      "deb": { "depends": ["libwebkit2gtk-4.1-0", "libgtk-3-0", "libsoup-3.0-0"] },
      "appimage": { "bundleMediaFramework": false }
    }
  }
}
```
- `category` es key de `bundle` (no bajo `linux`).
- Validar siempre: `python3 -c "import json; json.load(open('mobile/src-tauri/tauri.conf.json'))"`.
- Icons: necesarios 32/128/@2x png + icns + ico (Tauri los genera con `tauri icon`).

## CI — GitHub Actions (linux-desktop.yml)

Dos jobs: **backend-binary** (cargo build --release → upload artifact) y
**desktop-bundle** (deps sistema + pnpm + tauri build → upload .deb/.AppImage/.rpm):

```yaml
desktop-bundle:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: sudo apt-get update && sudo apt-get install -y
        libwebkit2gtk-4.1-dev libgtk-3-dev libsoup-3.0-dev librsvg2-dev patchelf
    - uses: dtolnay/rust-toolchain@stable
    - uses: Swatinem/rust-cache@v2
      with: { workspaces: mobile/src-tauri }   # ← IMPORTANTE
    - uses: actions/setup-node@v4
      with: { node-version: 22 }
    - run: corepack enable && corepack prepare pnpm@10.15.1 --activate
    - working-directory: mobile
      run: pnpm install --frozen-lockfile && pnpm build
    - working-directory: mobile
      run: pnpm tauri build          # en PR: pnpm tauri build --no-bundle
    - uses: actions/upload-artifact@v4
      with:
        name: synapse-trader-desktop
        path: mobile/src-tauri/target/release/bundle/**/*.{deb,rpm,AppImage,tar.gz}
        if-no-files-found: error
```

## Pitfalls críticos (verificados en Wave 6)

1. **NO meter `mobile/src-tauri` en el workspace raíz** — tiene su PROPIO
   Cargo.lock (workspace independiente). Añadirlo al `[workspace] members` del
   monorepo rompe `cargo build --release --all` en CI (necesitaría webkit2gtk
   en el job backend). Fix: revertir el member del workspace.
2. **Dos PRs que crean el MISMO workflow nuevo** → conflicto add/add en merge.
   Resolver localmente: checkout de la rama, `git merge origin/main`, `git
   checkout --theirs <workflow>` (conservar la versión más completa), commit,
   push a la rama del PR, luego merge.
3. **Draft PRs**: `gh pr merge` falla con "still a draft" — hacer
   `gh pr ready <N>` primero.
4. **CI jobs fallan en 2-3s sin ejecutar steps** = budget de Actions agotado
   (annotation "Actions budget is preventing further use"), NO error de código.
   Validar localmente (ver swal-ci-container host-native) y mergear con
   aprobación; el CI se re-valida cuando vuelva el budget.
5. **pnpm, no npm**: el proyecto usa pnpm-lock.yaml; `npm ci` falla si no hay
   package-lock.json. En CI: corepack + `pnpm install --frozen-lockfile`.
6. **`|| true` en pasos de build CI esmascara fallos** — quitarlo.
7. **Frontend → API local**: el frontend de escritorio debe apuntar al daemon
   local (default 19234 en SynapseTrader), configurable en runtime via
   `window.__DASHBOARD_CONFIG__?.apiBase` con fallback al puerto del daemon.

## Verificación

```bash
# estructura workflow
grep -c "tauri build" .github/workflows/linux-desktop.yml
grep -c "webkit2gtk" .github/workflows/linux-desktop.yml
# tauri.conf válido
python3 -c "import json; json.load(open('mobile/src-tauri/tauri.conf.json'))"
# src-tauri fuera del workspace raíz
grep -c "src-tauri" Cargo.toml   # → 0
```

## Referencias
- `references/synapse-wave6-merge-log.md` — transcript del merge de la Wave 6
  (orden 366→363→364→365, conflicto add/add resuelto, fixes post-merge).
