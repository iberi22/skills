# 🧠 iberi22/skills

[![Skills Count](https://img.shields.io/badge/skills-225-blue.svg)](./_registry/manifest.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Manifest](https://img.shields.io/badge/manifest-auto--generated-success.svg)](./_registry/manifest.yaml)

> Curated registry of **225 reusable AI agent skills** (merged from `swal-skills`, `agents-flows-recipes`, and credited upstreams — see [`THIRD_PARTY.md`](./THIRD_PARTY.md)).  
> Each skill is a self-contained expertise module with YAML frontmatter + markdown instructions.

---

## 📚 Categories

| Category | Skills | Description |
|----------|--------|-------------|
| `autonomous-ai-agents` | 2 | Delegation and multi-agent orchestration (Jules, Codex, OpenCode) |
| `communication` | 1 | Writing, messaging, tone |
| `debugging` | 2 | Bug triage, root-cause analysis |
| `design` | 7 | UI/UX, visual storytelling, brand |
| `devops` | 13 | Deployment, infrastructure, diagnostics |
| `engineering-workflow` | 10 | TDD, prototyping, rapid iteration |
| `framework` | 3 | Next.js, Astro, Vite, Tailwind CSS |
| `frontend` | 2 | Frontend-specific agents |
| `general` | 80 | General-purpose agent skills and tool integrations |
| `github` | 3 | GitHub workflow, PRs, issues |
| `jev` | 9 | Jev decision-model toolkit |
| `language` | 2 | Python, Rust guidelines |
| `marketing` | 6 | Content, growth, social media, ASO |
| `mattpocock` | 33 | Writing, planning, and review workflows (adapted upstream) |
| `operations` | 3 | Analytics, finance, legal, support |
| `orchestration` | 2 | Multi-agent coordination |
| `product` | 2 | Research, feedback, prioritization |
| `productivity` | 3 | Session and skill management |
| `project-management` | 2 | Sprints, shipping, coordination |
| `research` | 2 | Grounded citations, feed reading |
| `rust-development` | 2 | Rust compile optimization and workspace patterns |
| `security` | 1 | Security auditing |
| `social-media` | 1 | Social platform reading |
| `software-development` | 14 | Dev workflows, tooling, quality gates |
| `swal-engineering` | 1 | SWAL engineering protocols |
| `testing` | 5 | QA, benchmarking, optimization |
| `tools` | 12 | CLI tools, agent wrappers, MCP |
| `web` | 1 | Web design guidelines, accessibility |

> **Total: 225 skills** across 28 categories.  
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
- [`agents-flows-recipes`](https://github.com/iberi22/agents-flows-recipes) — Agent flows and reusable recipes

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
