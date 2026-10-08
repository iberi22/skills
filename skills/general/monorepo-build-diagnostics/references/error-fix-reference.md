# Monorepo Build Diagnostics — Error → Fix Reference

## Quick Diagnosis Table

| Error message pattern | Likely cause | Fix |
|---|---|---|
| `"X" is not exported by "../../packages/<pkg>/src/components/index.js"` | Shared package `package.json` exports field was modified (e.g. `"svelte"` field added) | `git checkout HEAD -- packages/<pkg>/package.json` + `pnpm install` |
| `Rollup failed to resolve import "<dep>" from "src/<file>.svelte"` | Untracked file imports npm package not in `package.json` | `pnpm add <dep>` + `pnpm add -D @types/<dep>` |
| `"SWAL_NAV_DEFAULT" is not exported by "@swal/ui"` | `@swal/ui` package was rewritten (new design system) without re-exporting old symbols | `git checkout HEAD -- packages/swal-ui/src/index.ts packages/swal-ui/package.json` |
| `Could not resolve "<workspace-pkg>"` | Workspace link broken or `pnpm-lock.yaml` stale | `pnpm install` (or delete `node_modules` + `pnpm install`) |
| Build passes with `pnpm dev` but fails with `pnpm build` | Rollup strictness vs Vite dev lazy resolution | Check which imports are only in untracked files → `pnpm add` |

## Stash Comparison Script

```bash
#!/bin/bash
# monorepo-build-check.sh — Is breakage pre-existing or yours?
REPO_ROOT="${1:-.}"
APP_DIR="${2:-apps/swal-backoffice}"

cd "$REPO_ROOT"
echo "=== Step 1: Stash changes ==="
git stash push -m "build-diag-$(date +%s)"

echo "=== Step 2: Build clean ==="
cd "$APP_DIR" && pnpm build 2>&1 | tail -5
CLEAN_EXIT=$?
cd "$REPO_ROOT"

echo "=== Step 3: Restore changes ==="
git stash pop

echo "=== Step 4: Build with changes ==="
cd "$APP_DIR" && pnpm build 2>&1 | tail -5
MODIFIED_EXIT=$?

echo ""
echo "=== Result ==="
if [ $CLEAN_EXIT -eq 0 ] && [ $MODIFIED_EXIT -ne 0 ]; then
  echo "Breakage IS from your changes (clean builds, modified fails)"
elif [ $CLEAN_EXIT -ne 0 ] && [ $MODIFIED_EXIT -ne 0 ]; then
  echo "Breakage is PRE-EXISTING (both fail)"
elif [ $CLEAN_EXIT -eq 0 ] && [ $MODIFIED_EXIT -eq 0 ]; then
  echo "Both build successfully — no issue"
fi
```

## pnpm Workspace Resolution Order

When you `import X from "@scope/pkg"` in a Svelte/Vite project:

1. pnpm resolves `@scope/pkg` via workspace `package.json` `"exports"` field
2. `vite-plugin-svelte` checks `"svelte"` field FIRST (overrides `"exports"`)
3. If `"svelte"` points to wrong file → export not found error

**This means:** if someone adds `"svelte": "./src/components/index.js"` to a workspace package, it silently overrides the `"exports"` field. Every consumer now resolves to `components/index.js` instead of the expected entry point.
