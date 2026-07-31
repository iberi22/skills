---
id: skill-launcher
name: skill-launcher
category: tools
tags:
  - skill-launcher
goals:
  - Automatically inject skill context into subagent spawning. Use this skill when launching any subagent to ensure they have the right skills loaded for their task. This skill provides the launching protocol and skill context injection.
authors:
  - Brahyan Belalcazar
---

# Skill Launcher

This skill ensures ALL subagents launched via `sessions_spawn` get the appropriate skill context automatically.

## How It Works

When spawning a subagent, you MUST prepend skill context to the task prompt. This skill provides the template and protocol for doing so.

## Protocol for Subagent Skill Injection

### Step 1: Identify Relevant Skills

Before spawning, identify which skills are relevant to the task:

```
Task Analysis → Required Skills → Fetch Skill Content → Inject into Prompt
```

### Step 2: Skill Context Template

Prepend this template to ALL subagent task prompts:

```
## SKILL CONTEXT FOR THIS TASK

You have access to the following skills. Read them before starting work:

### [SKILL NAME]
[Fetch skill content from: C:\Users\belal\clawd\skills\<skill>\SKILL.md]
[OR from raw GitHub: https://raw.githubusercontent.com/iberi22/agents-flows-recipes/main/skills/<skill>/SKILL.md]

---

## TASK

[Your actual task here]
```

### Step 3: Quick Skill Reference

| Task Type | Skills to Inject |
|-----------|-----------------|
| Frontend (React/Next.js) | astro OR nextjs + tailwindcss + react |
| Backend (Rust/Python) | rust OR python |
| UI Debug | frontend-doctor + playwright |
| GitHub Operations | github |
| Research | web-research + tavily-search |
| Security Audit | healthcheck |
| Sales/Prospects | sales-pro |

### Step 4: Skill Paths

Skills are available at:
- **Local**: `C:\Users\belal\clawd\skills\<skill>\SKILL.md`
- **Raw GitHub**: `https://raw.githubusercontent.com/iberi22/agents-flows-recipes/main/skills/<skill>/SKILL.md`
- **Skill Provider**: `node E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js get <skill>`

### Step 5: Fetching Skill Content

```bash
# Get skill locally
Read: C:\Users\belal\clawd\skills\<skill>\SKILL.md

# Or via skill provider
node E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js get <skill>
```

## Example: Spawning a Frontend Subagent

### BAD (No Skill Context):
```
sessions_spawn(task: "Fix the login button on mobile")
```

### GOOD (With Skill Context):
```
sessions_spawn(task: `## SKILL CONTEXT FOR THIS TASK

You are working on a Next.js 15 project with Tailwind CSS.

### nextjs Skill
Read: C:\Users\belal\clawd\skills\nextjs\SKILL.md

### tailwindcss Skill
Read: C:\Users\belal\clawd\skills\tailwindcss\SKILL.md

---

## TASK

Fix the login button on mobile. The button is too small and hard to tap on phones.
`)
```

## Automatic Skill Detection

For each subagent task, automatically detect required skills:

1. **Analyze the task description**
2. **Match keywords to skills**:
   - "frontend", "react", "next", "button", "ui" → nextjs, tailwindcss
   - "rust", "cargo", "backend" → rust
   - "python", "pip", "venv" → python
   - "deploy", "cloudflare", "astro" → astro
   - "debug", "fix", "error", "chrome" → frontend-doctor
   - "github", "pr", "issue", "repo" → github
   - "research", "search", "tavily" → web-research
   - "security", "vulnerability", "scan" → healthcheck
   - "sales", "proposal", "rfi", "client" → sales-pro

3. **Fetch the top 2-3 most relevant skills**
4. **Inject into prompt before the actual task**

## Skill Provider CLI

To list available skills:
```bash
node E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js list --public
```

To search for a skill:
```bash
node E:\scripts-python\agents-flows-recipes\_registry\skill-provider.js search <keyword>
```

## Priority Rules

1. **Always include at least ONE skill** for any coding task
2. **Max 3 skills** to avoid prompt bloat
3. **Order by relevance**: Primary skill first, dependencies after
4. **For multi-tool tasks**: Include the tool skill (github, web-research) plus domain skill

## This Skill

This skill (`skill-launcher`) is automatically loaded for ALL subagent spawns. It provides:
- The skill injection protocol
- Quick reference tables
- Example templates

Use it every time you spawn a subagent via `sessions_spawn`.