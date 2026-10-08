---
name: opencode-dev-workflow
description: >
  Workflow for launching OpenCode CLI sub-agents (opencode run) for SWAL
  development tasks. Use only when delegating to opencode.
license: Apache-2.0
updated: "2026-04-23"
metadata:
  author: SWAL
  version: "2.0"
---

# SWAL Development Workflow — OpenCode (MiniMax-M2.7)

> **⚠️ OPENCODE GO DESACTIVADO — Usar MiniMax-M2.7**

## When to Use

Load this skill when:
- Launching OpenCode sub-agents for software development
- Creating features, fixing bugs, or refactoring
- Reviewing code or creating PRs
- Any development task in SWAL projects

## Development Pipeline

### Phase 1: Explore & Analyze
```
1. Read relevant skills for the tech stack:
   - typescript/ (TypeScript projects)
   - react-19/ (React projects)
   - nextjs-15/ (Next.js projects)
   - playwright/ (E2E testing)
   
2. Check project structure:
   - README.md, SPEC.md, docs/
   - package.json, Cargo.toml, pyproject.toml
   
3. Run existing tests to establish baseline
```

### Phase 2: Implement
```
1. Apply skill patterns for the tech:
   - Read ~/.config/opencode/skills/{tech}/SKILL.md
   
2. Write code following:
   - Conventional commits (feat/, fix/, chore/)
   - TypeScript strict patterns
   - Test coverage > 80%
   
3. Commit with conventional commit format:
   feat(project): add new feature
```

### Phase 3: Verify & PR
```
1. Run tests: npm test / cargo test
2. Run linting: npm run lint / cargo clippy
3. Build: npm run build / cargo build
4. Create PR with github-pr skill
5. Apply appropriate labels
```

## Skills Available

### For Development
| Skill | Path | Use |
|-------|------|-----|
| typescript | ~/.config/opencode/skills/typescript/ | TypeScript strict mode |
| react-19 | ~/.config/opencode/skills/react-19/ | React 19 patterns |
| nextjs-15 | ~/.config/opencode/skills/nextjs-15/ | Next.js 15 |
| playwright | ~/.config/opencode/skills/playwright/ | E2E testing |
| github-pr | ~/.config/opencode/skills/github-pr/ | PR workflow |

### For Project Management
| Skill | Path | Use |
|-------|------|-----|
| jira-task | ~/.config/opencode/skills/jira-task/ | Create tasks |
| skill-creator | ~/.config/opencode/skills/skill-creator/ | Create new skills |

## Recommended Models

| Task | Model | Reason |
|------|-------|--------|
| Heavy coding | minimax/MiniMax-M2.7 | Best for complex logic |
| Medium tasks | minimax/MiniMax-M2.5 | Good balance |
| Light/economical | qwen-coder | Free tier |

## SWAL Project Conventions

### Repository
- Main repo: `iberi22/*` (NOT southwest-ai-labs)
- Projects: `E:\scripts-python`

### Code Quality Gates
- [ ] Tests pass
- [ ] Lint clean
- [ ] Build success
- [ ] Conventional commits
- [ ] Coverage > 80% (critical paths)

### Commit Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: feat, fix, docs, refactor, chore, test, perf, build, ci

## Commands

### Launch Development Sub-agent
```bash
opencode run --model minimax/MiniMax-M2.7 --dir E:/scripts-python/PROJECT "Your development task here"
```

### Launch with Specific Skill
```bash
opencode run --model minimax/MiniMax-M2.7 --dir E:/scripts-python/PROJECT "Read the typescript skill first, then implement..."
```

---

**Version:** 2.0
**Last Updated:** 2026-04-10
**Status:** ✅ MiniMax-M2.7 PRIMARY
