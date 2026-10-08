# SynapseTrader Wave 6 — Linux Desktop Deployment (merge log)

Transcripción de la integración real (2026-08-03) para referencia de patrones
de merge con Jules. 5 issues (#358-#362), 4 PRs de Jules, 1 conflicto resuelto.

## Issues → PRs → orden de merge

| Issue | PR | Archivos | Orden merge |
|-------|-----|----------|-------------|
| #358 Tauri integration | #366 | lib.rs, src-tauri/Cargo.toml, capabilities, api.ts, +page.svelte | 1º (sin conflicto) |
| #361 CI Linux bundle | #363 | linux-desktop.yml (new), pr-validation.yml | 2º |
| #359 tauri.conf.json | #364 | tauri.conf.json + **linux-desktop.yml (new también)** | 3º (conflicto) |
| #362 docs+features | #365 | DEPLOY_LINUX.md, README, features.json x2 | 4º |
| #360 install script | — | (Jules aún trabajando) | — |

## Conflictos y fixes encontrados

### 1. Dos PRs creando el mismo workflow (add/add conflict)

#363 y #364 AMBOS creaban `.github/workflows/linux-desktop.yml` como archivo
nuevo con contenido distinto (names "Linux Desktop Bundle (CI)" vs "Linux
Desktop Build"). GitHub marcó #364 como CONFLICTING.

Resolución local:
```bash
git checkout -b w6-364-merge origin/feat/tauri-linux-bundle-config-...
git merge origin/main                    # → CONFLICT add/add en linux-desktop.yml
git checkout --theirs .github/workflows/linux-desktop.yml   # conservar versión #363 (2 jobs, más completa)
git add . && GIT_EDITOR=true git commit --no-edit
git push origin w6-364-merge:feat/tauri-linux-bundle-config-...
gh pr merge 364 --merge --delete-branch   # tras gh pr ready
```

### 2. workspace raíz roto por src-tauri

#366 añadía `"mobile/src-tauri"` a `[workspace] members` del Cargo.toml raíz.
Problema: src-tauri tiene Cargo.lock propio; `cargo build --release --all` del
CI backend fallaría (necesita webkit2gtk). Fix inmediato post-merge:
```bash
git commit -m "fix: keep mobile/src-tauri out of root workspace (own Cargo.lock...)"
```

### 3. Draft PRs bloquean merge

`gh pr merge` → "GraphQL: Pull Request is still a draft". Fix:
`gh pr ready <N>` antes del merge. Afectó a #366, #363, #364, #365.

### 4. "Already merged" engañoso

`gh pr merge` reportó "was already merged" ANTES de que el fetch local
estuviera al día — el merge #363 no aparecía en `git log` local. Hacer
`git fetch origin && git log --oneline origin/main` para confirmar antes de
asumir que el PR se perdió.

### 5. Issues auto-cerrados por "Fixes #N"

Los issues #358/359/361/362 se cerraron SOLOS al mergear los PRs (los bodies
de Jules incluían "Fixes #N"). No hace falta `gh issue close` manual.

## Lección de proceso

- Jules entrega rápido (4 PRs en ~1h tras dispatch). El monitor
  `synapse-wave-monitor` (cada 5m) detecta los PRs.
- Validar CI localmente antes de mergear cuando el budget de Actions está
  agotado: `cargo check/test --lib` + `pnpm build` (dashboard+mobile) + estado
  del daemon. Ver skill `swal-ci-container` (modo host-native).
- Un commit de fix post-merge (workspace) es normal y barato — no esperar a que
  Jules lo haga.
