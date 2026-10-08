---
name: pr-review
description: PR Review Agent with Security and Decision Framework. Orchestrates code reviews with security analysis, code quality checks, and interactive decisions.
version: "1.0.0"
updated: "2026-04-23"
license: MIT
---

# PR Review Agent with Security & Decision Framework

## Overview
This skill orchestrates PR reviews with:
1. **Security Analysis** - Code review + dependency audit
2. **Code Quality** - Linting, testing, patterns
3. **Interactive Decisions** - Buttons/questions for user input

## Usage
```
/pr-review [owner/repo] [--pr number] [--security-only] [--interactive]
```

## Workflow

### Phase 1: Fetch PR
- Get PR diff and files changed
- Identify language/tech stack

### Phase 2: Security Scan
```
# Run security checks
- dependency-auditor: npm audit, pip-audit
- code-review-agent: semgrep scan
- secrets scanner: gitrob, trufflehog
```

### Phase 3: Code Quality
```
- Lint check
- Test coverage diff
- Pattern violations
```

### Phase 4: Decision Points

**When to ask user:**
| Condition | Action |
|-----------|--------|
| Security finding HIGH/CRITICAL | Block merge + notify |
| Breaking change detected | Ask: proceed/abort |
| New dependency added | Ask: approve/reject |
| Test coverage dropped >5% | Ask: proceed anyway? |
| Complex refactor | Show diff summary |

**Interactive Buttons:**
```
🔒 Security: {high|critical} - BLOCK
⚠️ Breaking Change - [Proceed] [Abort]
📦 New Dependency: {package} - [Approve] [Reject]
📉 Coverage dropped {x}% - [Proceed] [Ignore]
```

### Phase 5: Report
- Summary for each category
- Merge recommendation
- Action items

## Integration with gh-issues

Add to gh-issues skill:
```
--security-scan     # Run security analysis
--interactive      # Enable decision prompts
--block-on-high    # Block merge on HIGH findings
```

## Decision Types

### 1. Binary Decision
```
{title}
[✅ Approve] [❌ Reject]
```

### 2. Multi-option
```
{title}
[A] Option A  [B] Option B  [C] Skip
```

### 3. Override
```
Finding: {description}
Severity: {HIGH}
[🛡️ Override] [✅ Acknowledge] [❌ Block]
```

## Implementation

### Create pr-review skill
Location: `skills/pr-review/`

### Files:
- SKILL.md - Main skill
- tools/security-scanner.js - Run security audits
- tools/decision-prompt.js - Generate interactive prompts

## Integration Points

### With gh-issues
- Add --security flag
- Auto-trigger on PR creation
- Block on critical findings

### With cron jobs
- Periodic security scans
- Dependency vulnerability alerts
- Compliance checks

## Example Output

```
══════════════════════════════════════════
🔍 PR #42: Add new payment integration
══════════════════════════════════════════

📁 Files: 12 changed (+234, -89)

──────────────────────────────────────────
🔒 SECURITY ANALYSIS
──────────────────────────────────────────
✅ Dependencies: 0 vulnerabilities
⚠️ Secrets: 1 potential (line 45: API_KEY)
   → [🔒 View] [✅ False Positive] [❌ Block]

🔍 Code Review:
   - 2 LOW findings
   - 1 MEDIUM: Unsafe input sanitization

──────────────────────────────────────────
📊 CODE QUALITY  
──────────────────────────────────────────
✅ Linting: Pass
✅ Tests: 45/48 passed (93%)
⚠️ Coverage: -2% (was 78%, now 76%)

──────────────────────────────────────────
⚡ DECISION REQUIRED
──────────────────────────────────────────
1. New dependency: stripe@14.0.0
   [✅ Approve] [❌ Reject]

2. Test coverage dropped 2%
   [✅ Proceed] [❌ Abort]

3. Unsafe input on line 45
   [🔒 Override] [✅ Fix Required] [❌ Block]

──────────────────────────────────────────
📋 SUMMARY
──────────────────────────────────────────
Merge: ⚠️ REQUIRES APPROVAL
- Must fix: Unsafe input (MEDIUM)
- Must decide: 3 items above
```

---

*This skill integrates security scanning with interactive decision making for PR reviews.*
