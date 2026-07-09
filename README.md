# 🧠 iberi22/skills

[![Skills Count](https://img.shields.io/badge/skills-76-blue.svg)](./_registry/manifest.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/license/mit)
[![Manifest](https://img.shields.io/badge/manifest-auto--generated-success.svg)](./_registry/manifest.yaml)

> Curated registry of **76 reusable AI agent skills** migrated from `swal-skills` and `agents-flows-recipes`.
> Each skill is a self-contained expertise module with YAML frontmatter + markdown instructions.

---

## 📚 Categories

| Category | Skills | Description |
|----------|--------|-------------|
| `ai` | 3 | AI/ML tooling, fine-tuning, inference |
| `communication` | 1 | Writing, messaging, tone |
| `debugging` | 1 | Bug triage, root-cause analysis |
| `design` | 5 | UI/UX, visual storytelling, brand |
| `devops` | 1 | Deployment, infrastructure |
| `education` | 3 | Learning content, exam generation |
| `engineering-principles` | 1 | Architecture, code quality |
| `engineering-workflow` | 9 | TDD, prototyping, rapid iteration |
| `framework` | 4 | Next.js, Astro, Vite, Tailwind CSS |
| `frontend` | 2 | Frontend-specific agents |
| `language` | 2 | Python, Rust guidelines |
| `marketing` | 7 | Content, growth, social media, ASO |
| `operations` | 5 | Analytics, finance, legal, support |
| `product` | 3 | Research, feedback, prioritization |
| `project-management` | 4 | Sprints, shipping, coordination |
| `testing` | 5 | QA, benchmarking, optimization |
| `tools` | 17 | CLI tools, agent wrappers, MCP |
| `web` | 1 | Web design guidelines, accessibility |

> **Total: 76 skills** across 18 categories.
> See [`_registry/manifest.yaml`](./_registry/manifest.yaml) for the full machine-readable catalog.

---

## 🚀 Quick Start

### For Agents

Load a skill by referencing its `id` or `raw_url` from the manifest:

```yaml
skills:
  - id: nextjs
  - id: python
  - id: content-creator
```

### For Humans

Browse the [`skills/`](./skills/) directory by category, or read [`AGENTS.md`](./AGENTS.md) for the full agent briefing.

---

## 🔧 Repository Structure

```
iberi22/skills
├── skills/
│   ├── <category>/
│   │   └── <skill-name>/
│   │       └── SKILL.md          # Frontmatter + instructions
├── _registry/
│   └── manifest.yaml             # Auto-generated catalog
├── scripts/
│   ├── manifest-generator.py     # Scans skills/ and rebuilds manifest
│   └── skill-watchdog/
│       └── repos.json            # Upstream repos to monitor
├── .github/workflows/
│   ├── manifest.yml              # Auto-regenerates manifest on changes
│   └── skill-watchdog.yml        # Weekly upstream monitoring
├── AGENTS.md                     # Agent usage guide
└── README.md                     # This file
```

---

## 📝 Contributing

1. Create a new skill folder under `skills/<category>/<skill-name>/`.
2. Add a `SKILL.md` with valid YAML frontmatter (see [`AGENTS.md`](./AGENTS.md#format-conventions-v2)).
3. Run `python3 scripts/manifest-generator.py` to update the manifest.
4. Open a Pull Request — CI will lint frontmatter and verify manifest freshness.

---

## 📜 Origin & Attribution

This registry consolidates skills from previously archived repositories:

- [`swal-skills`](https://github.com/iberi22/swal-skills) — Original SWAL skill modules
- `agents-flows-recipes` — Agent flows and reusable recipes

Both have been archived; this repo is the **single source of truth** going forward.

---

## 📁 License

Skills are provided under their individual licenses (see frontmatter `license` field).  
Default: **MIT** where not specified.

---

## 📤 Installer (Eventual)

A `skills.sh` installer script is planned for one-line skill import into agent environments:

```bash
# Coming soon
curl -fsSL https://iberi22.github.io/skills/skills.sh | bash
```

For now, consume skills directly via raw GitHub URLs or the manifest API.
