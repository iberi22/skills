# Documentation Infrastructure Audit Pattern

**Context:** Deep-dive audit of a Rust project's documentation readiness for public release on GitHub Pages. Based on Xavier project analysis (2026-05-21).

## Probe Checklist

### 1. GitHub Pages Configuration

```bash
# Probe: is it branch-based or Actions-based?
ls .github/workflows/*.yml 2>/dev/null | xargs grep -l "pages\|gh-pages\|deploy" 2>/dev/null

# Probe: check .nojekyll
ls .nojekyll 2>/dev/null || echo "NO .nojekyll"
ls docs/site/dist/.nojekyll 2>/dev/null || echo "NO .nojekyll in dist"

# Probe: check remote and custom domain
git remote -v
git branch -r | grep "gh-pages" || echo "No gh-pages branch"
```

**Why .nojekyll matters:** Astro/Starlight generates `_astro/` directory. GitHub Pages runs Jekyll by default which ignores `_`-prefixed directories. Without `.nojekyll`, CSS/JS assets don't load.

**Fix:** Add `run: touch docs/site/dist/.nojekyll` before `upload-pages-artifact` in the workflow, or configure Astro's `build.format` to avoid `_` prefixes.

### 2. SSG (Static Site Generator) Analysis

```bash
# Probe: Astro/Starlight
ls astro.config.mjs 2>/dev/null && head -20 astro.config.mjs

# Probe: mdBook
ls book.toml 2>/dev/null && cat book.toml

# Probe: Docusaurus
ls docusaurus.config.* 2>/dev/null

# Probe: custom SSG in Rust (Chronicle-style)
grep -r "ssg\|chronicle.*build\|DevLogSSG" src --include="*.rs" 2>/dev/null | head -5
```

**Key questions:**
- Does the SSG produce standalone HTML/CSS/JS or is it part of a Node.js framework?
- Does the SSG output integrate with the main docs site or is it a separate site?
- Has the SSG build EVER been run? (`ls public/devlog/` or equivalent)
- What does the generated HTML look like? (theme, nav, search, responsive)

### 3. Code Symbol Indexer

```bash
# Probe: code-graph or similar
ls code-graph/Cargo.toml 2>/dev/null && cat code-graph/Cargo.toml | head -5

# Probe: tree-sitter parsers
find . -name "*.rs" -exec grep -l "tree_sitter\|TreeSitter" {} \; 2>/dev/null | head -5

# Probe: DB schema (SQLite)
grep -r "CREATE TABLE.*symbols\|CREATE TABLE.*edges\|stable_id" code-graph/ --include="*.rs" 2>/dev/null | head -10
```

**Critical data for auto-documentation:**
- `Symbol` types: name, kind (Function/Struct/Enum/Trait), file_path, start/end line, signature
- `Edges/graph`: Calls, Defines, Contains, Imports, References — with confidence scores
- `stable_id` (deterministic): enables cross-version tracking of symbols
- **Check if it extracts docstrings** (/// comments) — most parsers DON'T by default
- **Check if it tracks visibility** (pub/pub(crate)/private) — most DON'T by default
- **Check signature truncation** — common bug: signatures cut at 400 chars

### 4. CI/CD Documentation Pipeline

```bash
# Probe: docs workflow
cat .github/workflows/docs.yml 2>/dev/null  # or equivalent

# Probe: devlog/post generation workflow
grep -l "devlog\|chronicle\|auto.doc\|post.*generat" .github/workflows/*.yml 2>/dev/null
```

**Red flags:**
- `echo "Jules is picking up..."` — placeholder steps that do nothing
- No `cargo build` step for docs that need the binary
- No `npm ci` cache for Node-based SSG
- No `.nojekyll` creation
- No content-auto-generation step

### 5. Dead/Redundant Modules

```bash
# Probe: duplicate functionality
# e.g., src/devlog/ (placeholder) vs src/chronicle/ssg.rs (real implementation)
ls src/*/ 2>/dev/null | xargs -I{} sh -c 'echo "--- {} ---"; ls {}/*.rs 2>/dev/null | wc -l'
```

**Common pattern:** Placeholder module that promises functionality already implemented elsewhere. Mark for deletion after verifying the real implementation covers all use cases.

### 6. Existing Documentation Health

```bash
# Probe: post count and freshness
ls -la docs/devlog/ 2>/dev/null
git log --oneline --since="30 days ago" -- "docs/**/*.md" | wc -l

# Probe: contributor diversity
git log --format="%an" --since="30 days ago" -- "*.md" "docs/*" | sort | uniq -c | sort -rn

# Probe: was output never generated?
ls -la public/devlog/ 2>/dev/null || echo "SSG OUTPUT NEVER GENERATED"
```

## Report Template

After probes, create a status table:

| Component | Exists? | Status | Notes |
|-----------|---------|--------|-------|
| GitHub Pages config | ✅/❌ | Stable/Broken/Missing | Actions vs branch, .nojekyll |
| SSG (Astro/mdBook/etc) | ✅/❌ | Built/Never run/Placeholder | Framework, output quality |
| Code symbol indexer | ✅/❌ | Complete/Incomplete | What data it extracts |
| CI/CD docs pipeline | ✅/❌ | Full/Broken/Placeholder | What steps exist |
| Auto-doc generation | ✅/❌ | Works/Partial/None | Chronicle-style pipeline |
| Blog/DevLog content | ✅/❌ | N posts, last N days | Volume and freshness |

## Phased Plan Template

### Fase 0 — Quick Wins (1-2d)
- Add `.nojekyll` to dist output
- Run the SSG build (if it was never run)
- Fix any CI workflow placeholders

### Fase 1 — SSG UI Improvement (3-5d)
- Modernize HTML/CSS/JS output
- Add: dark mode, sidebar nav, client-side search, breadcrumbs, tags, responsive design
- Extract templates to separate files (include_str! in Rust)
- Write 8+ unit tests for templates

### Fase 2 — Auto-Documentation from Code (5-7d)
- New module that reads code-graph DB → structures module data
- Use LLM to generate explanatory markdown per module/subsystem
- Commands: `xavier chronicle auto-docs --module <name>`
- Improve code-graph parser: docstrings, visibility, impl blocks, const/static
- Write 10+ unit tests

### Fase 3 — CI/CD Pipeline Complete (2-3d)
- Extend docs workflow: build binary → index code → generate docs → build SSG → deploy
- Sidebar auto-generation for Astro/Starlight
- Real devlog-on-issue-label workflow (not placeholder)

### Fase 4 — Content (3-5d)
- Generate initial module docs for 6-8 modules
- Write 3+ manual DevLog posts (deep-dive technical)
- Review all generated content for accuracy

### Fase 5 — Cleanup (1d)
- Remove dead placeholder modules
- Update README with docs badges and links

## Common Pitfalls

1. **SSG output never generated**: The builder exists but nobody ran it. Run it immediately in Fase 0.
2. **Two modules, same job**: e.g., `src/devlog/` (placeholder) + `src/chronicle/ssg.rs` (real). Delete the placeholder.
3. **CI workflow placeholders**: `echo "Jules will implement this"` — replace or delete.
4. **LLM alucinations in auto-docs**: Mark as "Auto-generated" and add review gates.
5. **No .nojekyll**: Every Astro/Starlight site without it is broken on Pages.
6. **Code-graph data incomplete**: Parser may not extract docstrings, visibility, impl blocks. These are critical for useful auto-documentation.
7. **Signature truncation**: If `signature` field is truncated (e.g., 400 chars), increase limit or extract full source range.

## Verification After Implementation

```bash
# 1. Build the site locally
npm run build --workspace docs/site  # or equivalent

# 2. Check output directory
ls dist/  # or docs/site/dist/

# 3. Test with a local server
python3 -m http.server -d dist/ 8888

# 4. Check: all pages load?
# 5. Check: dark mode works?
# 6. Check: search works?
# 7. Check: responsive (mobile)?
# 8. Check: no broken links?
# 9. Check: assets load (no 404s)?
# 10. Check: sitemap exists?
```
