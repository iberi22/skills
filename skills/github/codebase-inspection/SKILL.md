---
name: codebase-inspection
description: "Deep-dive codebase analysis: LOC, structure, CI/CD, docs infrastructure, code symbol indexing, GitHub Pages readiness, and improvement planning."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [LOC, Code Analysis, pygount, Codebase, Metrics, Repository, Documentation, CI/CD]
    related_skills: [github-repo-management, writing-plans, ecosystem-analysis]
prerequisites:
  commands: [pygount]
---

# Codebase Inspection

Analyze codebases for structure, documentation infrastructure, CI/CD readiness, code symbol indexing, GitHub Pages setup, and improvement planning.

For documentation infrastructure deep-dives (SSG analysis, GitHub Pages audit, auto-documentation pipeline planning), see:

📄 [`references/docs-infrastructure-audit.md`](references/docs-infrastructure-audit.md)

## When to Use

- User asks for LOC count or language breakdown
- User asks about codebase size or composition
- User asks about documentation readiness for public release
- User wants to understand a project's CI/CD for docs, GitHub Pages setup, or static site generation
- User asks about auto-documentation from code (rustdoc, code symbol indexing)
- User wants a plan to improve documentation infrastructure
- General "what does this project look like" questions

## Prerequisites

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

For Rust projects with code symbol indexing: `cargo build` (needs compiled binary to analyze code-graph or similar).

## 1. Basic Summary (Most Common)

Get a full language breakdown with file counts, code lines, and comment lines:

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**IMPORTANT:** Always use `--folders-to-skip` to exclude dependency/build directories, otherwise pygount will crawl them and take a very long time or hang.

## 2. Common Folder Exclusions

Adjust based on the project type:

```bash
# Python projects
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript projects
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# General catch-all
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. Filter by Specific Language

```bash
# Only count Python files
pygount --suffix=py --format=summary .

# Only count Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. Detailed File-by-File Output

```bash
# Default format shows per-file breakdown
pygount --folders-to-skip=".git,node_modules,venv" .

# Sort by code lines (pipe through sort)
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. Output Formats

```bash
# Summary table (default recommendation)
pygount --format=summary .

# JSON output for programmatic use
pygount --format=json .

# Pipe-friendly: Language, file count, code, docs, empty, string
pygount --format=summary . 2>/dev/null
```

## 6. Documentation Infrastructure Audit

For projects that need public documentation, analyze the full docs pipeline:

### 6.1 GitHub Pages / Deploy

```bash
# Check if GitHub Pages is configured (Actions or branch)
ls -la .github/workflows/*.yml 2>/dev/null
grep -l "deploy-pages\|gh-pages\|pages:" .github/workflows/*.yml 2>/dev/null

# Check Astro/Starlight setup
ls docs/site/astro.config.mjs 2>/dev/null && head -20 docs/site/astro.config.mjs

# Check mdBook setup
ls book.toml 2>/dev/null && head -10 book.toml

# Check Docusaurus setup
ls docusaurus.config.js 2>/dev/null || ls docusaurus.config.ts 2>/dev/null

# Check for .nojekyll (critical for Astro/Starlight, _astro/ directory)
ls docs/site/dist/.nojekyll 2>/dev/null || echo "MISSING: .nojekyll — GitHub Pages will ignore _astro/ assets"

# Check git remote
git remote -v
```

### 6.2 Static Site Generator (SSG)

Identify what generates the docs site:

| SSG | Config File | Dependency | Build Command |
|-----|------------|------------|---------------|
| Astro/Starlight | `astro.config.mjs` | Node.js | `npm run build` |
| mdBook | `book.toml` | Rust | `mdbook build` |
| Docusaurus | `docusaurus.config.js` | Node.js | `npm run build` |
| VitePress | `.vitepress/config.js` | Node.js | `vitepress build` |
| Custom Rust SSG | `src/**/ssg.rs` | Rust binary | `cargo run -- chronicle build` |

### 6.3 Code Symbol Indexing

For auto-documentation from source code, check what code indexing exists:

```bash
# Rust: check for code-graph or similar indexers
find . -name "*.rs" -path "*/code-graph/*" -o -name "*.rs" -path "*/code_graph/*" | head -5

# Check for tree-sitter usage (Rust, TypeScript, Python parsers)
grep -r "tree-sitter" Cargo.toml */Cargo.toml 2>/dev/null

# Check if code-graph DB schema has symbols, edges, refs tables
# (common pattern: SQLite with symbols, refs, imports, edges tables)

# Check for rustdoc setup
grep -r "cargo doc" .github/workflows/*.yml 2>/dev/null || echo "No cargo doc in CI"
```

Key capabilities to evaluate:
- **Symbol extraction**: Does it index functions, structs, enums, traits?
- **Call graph**: Does it track caller/callee relationships?
- **Dependencies**: Does it map module-to-module imports?
- **Doc comments**: Does it extract `///` or `//!` documentation?
- **Visibility**: Does it track `pub`/`pub(crate)`/private modifiers?

### 6.4 Auto-Documentation Pipeline

Check if there's a generation pipeline that connects code → docs:

```bash
# Chronicle-style: harvest → LLM generate → SSG build
grep -r "chronicle\|auto.docs\|generate.*doc" src/ --include="*.rs" | head -10

# Check for LLM-based doc generation
grep -r "generate_text\|ModelProviderClient\|LLM" src/ --include="*.rs" | head -5

# Check for doc generation CI workflows
grep -l "devlog\|doc.*generat\|auto.*doc" .github/workflows/*.yml 2>/dev/null
```

### 6.5 Existing Documentation Content

```bash
# Count docs
find . -name "*.md" -not -path "*/node_modules/*" -not -path "*/target/*" | wc -l

# Check devlog/blog posts
ls -la docs/devlog/ 2>/dev/null || echo "No devlog directory"

# Check if SSG output was ever generated (e.g., public/devlog/)
ls -la public/devlog/ 2>/dev/null || echo "SSG output never generated"

# Check git activity on docs
git log --oneline --since="30 days ago" -- "*.md" "docs/*" | head -10
git log --format="%an" --since="30 days ago" -- "*.md" "docs/*" | sort | uniq -c | sort -rn
```

### 6.6 Improvement Planning

After the audit, create a phased plan:

1. **Fase 0 — Quick Wins**: .nojekyll, run SSG build, fix CI workflow placeholders
2. **Fase 1 — SSG UI**: Modernize generated HTML/CSS/JS (dark mode, sidebar, search, breadcrumbs)
3. **Fase 2 — Auto-Docs**: Connect code-graph → LLM → markdown generator per module
4. **Fase 3 — CI/CD Pipeline**: Extend workflow to build binary → index code → generate docs → build SSG → deploy
5. **Fase 4 — Content**: Write initial posts, generate module docs, review manually
6. **Fase 5 — Cleanup**: Remove dead code (duplicate modules), update README

Each phase should include:
- Tests (unit + integration) for new Rust/JS code
- Verification steps (open site, check links, check responsive)
- CI workflow changes with caching strategy

### 6.7 Tests to Write for Documentation Infrastructure

```rust
// SSG tests
#[test] fn test_html_template_has_nav()     // Sidebar and navigation
#[test] fn test_css_is_responsive()          // Media queries exist
#[test] fn test_dark_mode_toggle_in_html()   // Dark mode support
#[test] fn test_index_has_search_input()     // Client-side search
#[test] fn test_generated_html_has_breadcrumbs()
#[test] fn test_build_with_all_posts()       // Integration test

// Auto-docs tests
#[test] fn test_extract_module_data_from_code_graph()
#[test] fn test_extract_doc_comments_from_source()
#[test] fn test_extract_visibility_from_symbol()
#[test] fn test_auto_docs_generates_valid_markdown()
#[test] fn test_auto_docs_output_writes_files()

// Parser improvement tests
#[test] fn test_parse_rust_doc_comment()
#[test] fn test_parse_rust_visibility()
#[test] fn test_parse_rust_methods_in_impl()
#[test] fn test_parse_rust_const_and_static()
```

## 7. Interpreting Results

The pygount summary table columns:
- **Language** — detected programming language
- **Files** — number of files of that language
- **Code** — lines of actual code (executable/declarative)
- **Comment** — lines that are comments or documentation
- **%** — percentage of total

Special pseudo-languages:
- `__empty__` — empty files
- `__binary__` — binary files (images, compiled, etc.)
- `__generated__` — auto-generated files (detected heuristically)
- `__duplicate__` — files with identical content
- `__unknown__` — unrecognized file types

## Pitfalls

1. **Always exclude .git, node_modules, venv** — without `--folders-to-skip`, pygount will crawl everything and may take minutes or hang on large dependency trees.
2. **Markdown shows 0 code lines** — pygount classifies all Markdown content as comments, not code. This is expected behavior.
3. **JSON files show low code counts** — pygount may count JSON lines conservatively. For accurate JSON line counts, use `wc -l` directly.
4. **Large monorepos** — for very large repos, consider using `--suffix` to target specific languages rather than scanning everything.
