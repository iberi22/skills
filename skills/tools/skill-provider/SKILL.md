---
id: skill-provider
name: skill-provider
category: tools
tags:
  - skill-provider
goals:
  - "Dynamically load and manage skills from the SWAL registry. Use when you need to access a specific skill (like astro, nextjs, tailwindcss) or when you want to list available skills. The skill provider fetches skills from raw GitHub URLs or serves them from local cache. Perfect for agents that need skills on-the-fly without pre-installation."
authors:
  - Brahyan Belalcazar
---

# SWAL Skill Provider

Dynamic skill loader for all coding agents. Access any skill on-demand.

## Quick Commands

### List All Available Skills
```bash
node "E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js" list
```

### List Only Public Skills
```bash
node "E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js" list --public
```

### List Only Private Skills
```bash
node "E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js" list --private
```

### List All POML Recipes (Executable Agents)
```bash
node "E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js" recipes
```

### Get a Specific Skill Content
```bash
node "E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js" get <skill-id>
```
Examples:
- `node ... get astro` - Get Astro framework skill
- `node ... get nextjs` - Get Next.js 15 skill
- `node ... get tailwindcss` - Get Tailwind CSS skill

### Get a POML Recipe
```bash
node "E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js" recipe <recipe-id>
```
Examples:
- `node ... recipe ai-engineer` - Get AI Engineer recipe
- `node ... recipe frontend-developer` - Get Frontend Developer recipe
- `node ... recipe content-creator` - Get Content Creator recipe

### Install a Skill Locally
```bash
node "E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js" install <skill-id>
```
This installs the skill to `C:\Users\belal\clawd\skills\<skill-id>`

### Search Skills
```bash
node "E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js" search <query>
```
Examples:
- `node ... search react` - Find React-related skills
- `node ... search frontend` - Find frontend skills

### Sync All Public Skills
```bash
node "E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js" sync
```

## Available Skills

### Coding Frameworks (PUBLIC)
| Skill ID | Name | Description | Agents |
|----------|------|-------------|--------|
| astro | Astro Framework | Static sites with Cloudflare deployment | all |
| nextjs | Next.js 15 | App Router, server components, caching | all |
| tailwindcss | Tailwind CSS | Utility-first CSS with dark mode | all |
| vite | Vite | Build tool and dev server | all |
| react | React | Component patterns and hooks | all |
| rust | Rust | Systems programming patterns | all |
| python | Python | Python best practices | all |

### SWAL Agent Skills (PRIVATE)
| Skill ID | Name | Description | Agents |
|----------|------|-------------|--------|
| sales-pro | Sales Pro | RFIs, proposals, prospect research | openclaw |
| src-generator | SRC Generator | IEEE 830 document generation | openclaw |

### OpenClaw Tools (PUBLIC)
| Skill ID | Name | Description |
|----------|------|-------------|
| github | GitHub CLI | Issues, PRs, CI via gh |
| web-research | Web Research | Tavily, Brave search |
| frontend-agent | Frontend Agent | Full frontend development |
| frontend-doctor | Frontend Doctor | UI debugging with DevTools |
| gemini | Gemini CLI | Summaries and Q&A |
| codex | Codex CLI | Code generation |
| qwen | Qwen Coder | Code generation |

### POML Recipes (PUBLIC)
| Recipe ID | Department | Name |
|----------|------------|------|
| ai-engineer | engineering | AI Engineer |
| frontend-developer | engineering | Frontend Developer |
| backend-architect | engineering | Backend Architect |
| test-writer-fixer | engineering | Test Writer/Fixer |
| rapid-prototyper | engineering | Rapid Prototyper |
| content-creator | marketing | Content Creator |
| growth-hacker | marketing | Growth Hacker |
| studio-coach | bonus | Studio Coach |

## Usage Examples

### When Starting a New Frontend Project
```
1. Load the framework skill: node ... get nextjs
2. Load CSS skill: node ... get tailwindcss
3. Read the skill content to understand best practices
```

### When You Need to Debug UI
```
1. Load frontend-doctor: node ... get frontend-doctor
2. Follow the debugging workflow in the skill
```

### When You Want to Research Something
```
1. Load web-research: node ... get web-research
2. Use the research tools described
```

### When You Need a Recipe Agent
```
1. List recipes: node ... recipes
2. Get a recipe: node ... recipe frontend-developer
3. Follow the POML workflow
```

## Direct Raw URLs

For agents that can fetch URLs directly:
- Manifest: https://raw.githubusercontent.com/iberi22/agents-flows-recipes/main/_registry/manifest.yaml
- Astro: https://raw.githubusercontent.com/iberi22/agents-flows-recipes/main/skills/astro/SKILL.md
- Next.js: https://raw.githubusercontent.com/iberi22/agents-flows-recipes/main/skills/nextjs/SKILL.md
- Tailwind: https://raw.githubusercontent.com/iberi22/agents-flows-recipes/main/skills/tailwindcss/SKILL.md

## Architecture

```
agents-flows-recipes/
├── _registry/
│   ├── manifest.yaml        # Central registry of all skills
│   └── skill-provider.js   # CLI tool for skill management
├── skills/                   # Skills source files
│   ├── astro/
│   ├── nextjs/
│   ├── tailwindcss/
│   └── ... (more skills)
└── poml/                    # POML recipe files
    ├── engineering/
    ├── marketing/
    └── ...
```

## For Agents

- **OpenClaw**: Use the skill-provider.js script directly
- **Claude Code**: Read skills from `C:\Users\belal\clawd\skills\` or fetch raw URLs
- **Codex**: Configured in `C:\Users\belal\.codex\config.toml` to point to shared skills
- **Other agents**: Can fetch skills via raw GitHub URLs