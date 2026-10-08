---
name: monorepo-build-diagnostics
description: "Diagnose build failures in pnpm/Svelte/Vite monorepos — stash-comparison to isolate pre-existing breakage from your changes, workspace dependency resolution pitfalls, untracked-file missing deps."
version: 1.0.0
author: Hermes Agent
tags: [monorepo, pnpm, svelte, vite, build, diagnostics, workspace]
category: software-development
---

# Monorepo Build Diagnostics

## When to Use

- A `pnpm build` fails after you added or modified files in a Svelte/Vite monorepo
- You need to determine if the breakage is **yours** or **pre-existing** in the working tree
- A shared workspace package (`@scope/pkg`) was modified and consuming apps break
- Untracked `.svelte` files import npm packages that pass dev but fail build

## Stash-Comparison Workflow

**Core technique:** stash your changes, build from clean committed state, compare.

```bash
# 1. Stash your changes
cd <repo-root> && git stash

# 2. Build from clean committed state
cd apps/<app> && pnpm build

# 3. Restore your changes
cd <repo-root> && git stash pop

# 4. Build again — now the failure is attributable
pnpm build
```

**Interpretation:**
- Step 2 **passes** → breakage is yours → debug your code
- Step 2 **fails** → breakage is pre-existing → fix pre-existing issue first

## Common Pre-Existing Breakage Patterns

### 1. Shared package export mismatch

**Signal:** error says `"X is not exported by ../../packages/<pkg>/src/components/index.js"`

In pnpm monorepos, `@scope/pkg` resolves via the workspace `package.json` `"exports"` or `"svelte"` field. If someone modifies a shared package's `package.json` (e.g. changes `"exports": { ".": "./src/index.ts" }` to `"svelte": "./src/components/index.js"`), **every consuming app breaks** even though neither changed their imports. The `vite-plugin-svelte` resolver follows the `"svelte"` field first.

**Fix:**
```bash
git checkout HEAD -- packages/<broken-package>/package.json
pnpm install   # re-resolve workspace links
```

### 2. Missing npm dependencies for untracked files

**Signal:** `Rollup failed to resolve import "<pkg>" from "<path>/UntrackedFile.svelte"`

Untracked `.svelte` files that import npm packages pass `pnpm dev` (Vite resolves on-the-fly) but **fail `pnpm build`** (Rollup requires all imports resolvable at build time).

**Fix:**
```bash
pnpm add <pkg>              # runtime dependency
pnpm add -D @types/<pkg>    # types (if TypeScript)
```

### 3. Stale lockfile after workspace change

**Signal:** random build failures, modules not found, version mismatches

**Fix:**
```bash
pnpm install                # re-resolve workspace links
# Nuclear option:
rm -rf node_modules && pnpm install
```

## Decision Tree

```
Build fails after you changed files
├─ git stash → build passes without your changes?
│  ├─ YES → breakage is yours → debug your code
│  └─ NO  → breakage is pre-existing
│     ├─ Shared package export mismatch? → restore package.json
│     ├─ Missing dep for untracked file? → pnpm add
│     └─ Other? → systematic-debugging Phase 1
└─ git stash → build fails without your changes too?
   └─ Confirm: is the committed build broken? (CI vs local)
```

### 4. A write "succeeds" (2xx) but nothing lands in the store

This and the two sections below share one failure shape: **every local gate is
green and the artifact is still wrong.** When you hit one of them, stop
re-running the build — the build is not the thing that is lying; the artifact
or the gate's scope is.

**Symptom:** the write endpoint returns success and echoes the record back, the
parent entity appears updated, but a fresh read returns empty and the backing
store has zero rows for that entity.

This is a distinct failure class from the build errors above, because every
local gate stays green: typecheck, unit tests, and build all pass.

**Two mechanisms cause it, and they compose:**

1. **A NOT NULL column is missing from the built record.** Adapters that write
   a metadata row (e.g. `sealed_meta(id, appId, instance_id, entity,
   content_hash, r2_key, created_at)`) require a `created_at`. A factory that
   emits only a domain-specific timestamp (`recorded_at`, `paid_at`) omits it,
   the INSERT fails, and the write silently degrades to an in-process cache
   map. Because the same request reads back from that cache, the handler can
   honestly report the record it just wrote — and lose it on the next request
   when the isolate is cold.

2. **`.catch(() => {})` on the insert.** Swallowed errors make a failed write
   indistinguishable from a successful one. Every `.catch(() => {})` on a
   persistence path should log the entity and id.

**Diagnostic sequence:**
```bash
# 1. Is the row actually there? (count by entity)
wrangler d1 execute <database_id> --remote --json \
  --command "SELECT entity, COUNT(*) n FROM <meta_table> GROUP BY entity"

# 2. Compare against a sibling entity that works
wrangler d1 execute <database_id> --remote --json \
  --command "SELECT entity,id,r2_key,created_at FROM <meta_table> WHERE entity='<working>' LIMIT 2"
```
If your new entity has **no rows at all** while a sibling written by the same
adapter has rows, the write path is at fault — not the read path. Diff the two
records field by field against the table's NOT NULL columns.

**Fix:** emit every required column from the record factory, and make the catch
log. Add a regression test asserting the factory output carries the NOT NULL
fields (assert presence and parseability, not just truthiness of one field).

**Rule:** a 2xx from a write is a claim, not proof. Confirm in this order:
response body → fresh GET on a new request → direct store count. The store
count is the only one that cannot lie.

### 5. The build exits 0 and leaves a deploy bundle that would break production

**Symptom:** `pnpm run build` exits 0 and the whole suite passes, but the
artifact the deploy command reads back is wrong. Same epistemic shape as the
write case above: every local gate is green, and the defect only appears
against the real system.

**Mechanism.** When the build script wraps a framework build (`astro build`,
etc.), that framework **regenerates its own config artifact** from scratch at
the end of the run. Any normalization step placed *before* it is silently
overwritten, and the incomplete file is exactly what ships.

**Two independent failure modes, both silently green:**

1. **Ordering.** The normalization runs before the framework build, so the
   framework build overwrites it. The build directory keeps only the
   framework's bare output — missing bindings, wrong name, missing env vars.
   Fix: run normalization as the **last** step of the build script, and make
   the build **exit non-zero** when it fails, so a half-normalized artifact
   can never be deployed.
2. **Calendar-derived config.** A config field stamped with `new Date()`
   drifts by itself. It works until the installed runtime stops supporting
   that date, at which point the runtime refuses to boot while the build still
   exits 0 — the failure is at startup, so no compile-time gate can see it.
   Fix: inherit the field from the declarative config source (the real
   config file), never from the current date; add a test asserting the value
   equals the declared one and is not today.

**Diagnostic sequence:**
```bash
# 1. Inspect the artifact the deploy command actually reads, after a fresh build
python3 -c "import json;j=json.load(open('dist/server/wrangler.json'));print(j['name'],j.get('vars'),len(j.get('d1_databases',[])))"

# 2. Prove the ordering from the build script itself
grep -n "<framework-build>\|<normalize-script>" <build-script>

# 3. For the startup-only class, read the runtime's own error, not the exit code
<runtime> dev --config dist/server/wrangler.json
```

**Rule:** a build artifact is not correct because the build was green. Assert
the artifact's fields directly — name, bindings with real identifiers, env,
route config, and the inherited-not-dated config fields — as a test that reads
the file the build emitted.

### 6. A gate you reported green was never actually run over your files

**Symptom:** a delivery report says "lint clean" while the linter, run
properly, reports violations in a file you edited.

Mechanism, one of two: lint was never invoked separately (a green build and a
green suite are different gates, and reporting one while implying the other is
a false claim), or the linter ran from a directory / over a path list that did
not include the edited file, so its scope silently excluded the code in
question. A passing gate only certifies what it actually covered.

**Diagnostic sequence:**
```bash
# 1. Run the linter explicitly on the edited files, from the project root
npx biome check <edited-files>; echo "EXIT=$?"

# 2. Attribute each violation before reporting
git show <commit> -- <file> | grep -E '^[-+]'   # what your diff changed
git log -L <a>,<b>:<file>                        # who introduced the line
```

**Rule:** report your violations and the pre-existing ones as two distinct
facts, and never fold the second into the first to make a report look
cleaner. Leave unrelated pre-existing violations out of a focused fix.

### 5. A seed/fixture script runs twice and duplicates the world

**Symptom:** a public listing renders every record twice. Each duplicate has the
same business fields but a **different id**, so deduplicating by id does
nothing. The adapter's `list()` faithfully returns both rows; nothing is broken
downstream — the data itself is wrong.

**Why:** seed scripts that POST blindly create a second set on re-run. Because
they are idempotent-ish at the user level (409 → login) the second run looks
successful in the log while multiplying everything below that point.

**Fix, two layers:**

1. Make the seed idempotent on the business key, not just on auth:
   ```js
   const existing = (await api('/api/<items>?instance_id=' + INSTANCE)).data;
   const names = new Set((Array.isArray(existing) ? existing : []).map((r) => String(r?.name ?? '')));
   for (const item of items) {
     if (names.has(item.name)) { created.push(`${item.name} -> ya existia (skip)`); continue; }
     await api('/api/<items>', { method: 'POST', body: item });
   }
   ```
2. Dedupe defensively in the **reader**, keyed on business identity
   (restaurant + normalized name + price) rather than id. Keep entries whose
   same name carries a **different price** — that is real menu variation, and a
   dedupe that deletes it destroys actual data.

Clean up the existing duplicates afterwards through the app's own DELETE
endpoint, then confirm the store count matches the API response and the DOM.

**Verification rule for UI lists:** assert on the **rendered DOM**, not on the
serialized HTML. SSR frameworks often serialize the same data twice (props as
`[0, value]` tuples, preloaded JSON plus the markup), so counting occurrences in
raw HTML reports numbers the user never sees. Count the actual rendered
controls instead:
```js
[...document.querySelectorAll('button')].filter(b => b.innerText.trim() === 'Añadir').length
```

### 6. A router rejects two files that resolve to the same path — and tests stay green

**Symptom:** the build warns
`The route "/api/x/[id]" is defined in both "[id]/index.ts" and "[id].ts"`
followed by "a collision will result in a hard error in following versions".
**Unit tests, typecheck and vitest all pass** — the warning only appears when
compiling, so a test-only gate reports green on a tree that will not deploy.

**Rule:** before adding an endpoint under a dynamic segment directory, check
whether the flat file already exists:
```bash
find src/pages -name "index.ts" -path "*\[[a-zA-Z]*\]*" | while read f; do
  [ -f "${f%index.ts}.ts" ] && echo "COLISION: ${f%index.ts}.ts <-> $f"
done
```

**Which one to keep:** the pre-existing flat file usually carries more
convention than the new one. Compare them — if the old one soft-deletes (marks
`deleted_at` and the listing filters it) while the new one hard-deletes
(`adapter.del`, wiping the store), keep the old: soft delete preserves history
and is the project's convention. Deleting the wrong one destroys the data model.

**Pitfall when cleaning up:** delete **only the offending file**. Removing the
whole directory takes sibling routes with it (e.g. `[id]/transactions.ts`
imported by a test), and the resulting `ts2307 Cannot find module` is a
self-inflicted wound. Restore siblings from git rather than recreating them.
Note that a directory `[id]/` holding `payment.ts`/`transition.ts` alongside a
flat `[id].ts` is **not** a collision — only a competing `index.ts` is.

## Reference

> 📎 `references/error-fix-reference.md` — condensed error → fix mapping, stash comparison script, and pnpm workspace resolution order.
