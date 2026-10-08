---
name: doc-generator
description: Creates professional documentation for SWAL projects using real code analysis. Use when projects have low doc score or missing ARCHITECTURE.md/STATE.md.
version: "1.0.0"
updated: "2026-04-23"
author: swal
license: MIT
---

# Documentation Generator Skill

Creates professional documentation for SWAL projects using real code analysis.

## When to Use
- Project has < 50% doc score
- Missing ARCHITECTURE.md, STATE.md, or TODO.md
- Need to update existing documentation

## Process

### Phase 1: Research (REQUIRED)
1. Read `README.md` if exists
2. Read `package.json` for tech stack and scripts
3. Explore `src/` folder structure
4. Run `npm run build` to verify build status
5. Check GitHub issues if available

### Phase 2: Create .gitcore/ folder
```bash
mkdir -Force .gitcore\
```

### Phase 3: Write ARCHITECTURE.md
Project-specific content covering:
- What the project does (specific, not generic)
- Tech stack (from package.json)
- Module structure (from src/ exploration)
- Data flow (from code reading)
- API endpoints (from routes)

### Phase 4: Write STATE.md
Project-specific content covering:
- Build status (from npm run build)
- Test status (from npm test)
- Module status table (real modules you found)
- Known issues (real issues from code or GitHub)

### Phase 5: Write TODO.md
Real tasks found in the code or issues:
- HIGH: What needs to be done next
- MEDIUM: What should be done
- LOW: Future improvements
- NO "TODO: Add..." content

### Phase 6: Commit
```bash
git add .gitcore/
git commit -m "docs: add professional documentation"
```

## Rules
- REAL content only - no stubs
- If you don't know, research more
- Every section must have specific content
- Length follows what the project actually has

## Output Format
Report:
- Files created
- Line counts
- Key findings
- Commit hash
