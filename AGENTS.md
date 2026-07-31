# AGENTS.md — Agent Briefing for iberi22/skills

## Overview

This repository is a curated registry of **agent skills** — reusable expertise modules that can be loaded by AI agents (e.g., via SWAL, Codex, Claude Code, or any agent framework that supports skill injection).

Each skill lives in `skills/<category>/<skill-name>/` and is defined by a `SKILL.md` file with YAML frontmatter.

---

## How to Use These Skills

### 1. Load by ID

Reference a skill by its `id` (declared in frontmatter). Example:

```yaml
skills:
  - id: nextjs
  - id: python
  - id: content-creator
```

### 2. Load by Category

You can also load all skills within a category:

```yaml
skills:
  - category: marketing
```

### 3. Raw URL Access

Each skill exposes a `raw_url` pointing to its `SKILL.md` on GitHub (raw). This is useful for dynamic loading at runtime:

```
https://raw.githubusercontent.com/iberi22/skills/main/skills/<category>/<skill-name>/SKILL.md
```

### 4. Manifest

The canonical registry is at `_registry/manifest.yaml`. It contains metadata for all skills: `id`, `name`, `description`, `category`, `tags`, `path`, `raw_url`, `authors`, etc. Parse this to discover available skills programmatically.

---

## Format Conventions (v2)

All `SKILL.md` files follow the **v2 format**:

```markdown
---
id: unique-skill-id
name: Display Name
category: category-name
tags:
  - tag1
  - tag2
goals:
  - "One-line description of what this skill enables."
  - "Another goal or context."
authors:
  - Author Name
---

# Content

Markdown body with system prompt, instructions, examples, and constraints.
```

### Required Frontmatter Fields

| Field      | Type     | Description                              |
|------------|----------|------------------------------------------|
| `id`       | string   | Unique kebab-case identifier             |
| `name`     | string   | Human-readable name                      |
| `category` | string   | Top-level category folder name           |
| `tags`     | string[] | Searchable tags                          |
| `goals`    | string[] | What the skill enables (1–3 items ideal) |

### Optional Frontmatter Fields

| Field            | Type     | Description                          |
|------------------|----------|--------------------------------------|
| `version`        | string   | Semantic version                     |
| `description`    | string   | Short description (auto-extracted if missing) |
| `authors`        | string[] | Attribution                          |
| `license`        | string   | License identifier                   |
| `original_source`| string   | Upstream URL if ported               |
| `context`        | string   | When/where to apply this skill       |

---

## Category Taxonomy

| Category               | Description                                      | Count |
|------------------------|--------------------------------------------------|-------|
| `ai`                   | AI/ML tooling, fine-tuning, inference              | —     |
| `communication`        | Writing, messaging, tone, translation              | —     |
| `debugging`            | Bug triage, root-cause analysis, diagnostics       | —     |
| `design`               | UI/UX, visual storytelling, brand, whimsy          | —     |
| `devops`               | Deployment, infrastructure, CI/CD                  | —     |
| `education`            | Learning content, exam generation, validation      | —     |
| `engineering-principles`| Architecture, code quality, principles            | —     |
| `engineering-workflow`| TDD, prototyping, rapid iteration, testing         | —     |
| `framework`            | Next.js, Astro, Vite, Tailwind CSS, etc.           | —     |
| `frontend`             | Frontend-specific agents and patterns              | —     |
| `language`             | Language-specific guidelines (Python, Rust, etc.)  | —     |
| `marketing`            | Content, growth, social media, ASO                 | —     |
| `operations`           | Analytics, finance, legal, support                 | —     |
| `product`              | Research, feedback, prioritization                 | —     |
| `project-management`   | Sprints, shipping, studio coordination             | —     |
| `testing`              | QA, benchmarking, workflow optimization            | —     |
| `tools`                | CLI tools, agent wrappers, MCP integrations        | —     |
| `web`                  | Web design guidelines, accessibility, performance  | —     |

> **Note:** Category counts are auto-generated in `_registry/manifest.yaml`.

---

## Contributing

### Adding a New Skill

1. Create a folder: `skills/<category>/<skill-name>/`
2. Add `SKILL.md` with valid YAML frontmatter and markdown body.
3. Optionally add companion files (e.g., `setup.md`, `examples/`).
4. Run `python3 scripts/manifest-generator.py` to regenerate the manifest.
5. Open a Pull Request.

### PR Checklist

- [ ] `SKILL.md` frontmatter is valid YAML (run a YAML linter).
- [ ] `id` is unique across the entire registry.
- [ ] `category` matches an existing folder or is added to taxonomy.
- [ ] `goals` are concise and actionable.
- [ ] No sensitive data (API keys, passwords, internal URLs) in content.

### CI / Lint

Pull requests are validated by GitHub Actions:

- **YAML lint** — all `SKILL.md` frontmatters must parse cleanly.
- **ID uniqueness** — no duplicate skill IDs.
- **Manifest freshness** — `manifest.yaml` must be up to date (or the `manifest` workflow will auto-commit it after merge).

---

## Automation

| Workflow                 | Trigger                              | Purpose                              |
|--------------------------|--------------------------------------|--------------------------------------|
| `manifest.yml`           | Push to `skills/**`                  | Regenerates `_registry/manifest.yaml` and commits it. |
| `skill-watchdog.yml`     | Weekly (cron) + manual dispatch      | Monitors upstream repos for new skills and opens issues. |

---

## Questions?

Open an issue or reach out via the repo discussions.
