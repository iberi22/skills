---
name: gemini-deep-research
description: Advanced deep research agent using Gemini 3.1 Pro with customtools endpoint for optimal agent performance. Deep research, thinking mode, and project management for 50+ SWAL projects. Updated 2026-04-20.
version: "1.0.0"
updated: "2026-04-23"
author: swal
license: MIT
metadata:
  provider: Google AI Studio
  model: gemini-3.1-pro-preview
  features: thinking, code-execution, google-search, customtools
---

# SWAL Deep Research Agent - Gemini 3.1 Pro Edition

> **🧠 Most Advanced Research System**
> Using Gemini 3.1 Pro with customtools endpoint

---

## 🤖 Model Selection (UPDATED)

### ⭐ PRIMARY: `gemini-3.1-pro-preview-customtools`
- **Released**: February 19, 2026
- **Why**: Optimized for agent tool use - prioritizes custom tools over bash
- **Endpoint**: Native Google API (not OpenAI compatible)
- **Cost**: Same as standard

### BACKUP: `gemini-2.5-pro`
- **Why**: Proven, stable
- **Endpoint**: OpenAI compatible available

---

## 🔑 API Keys (4 Keys Available)

```
Keys: AIzaSyBXo..., AIzaSyCxp..., AIzaSyDtx..., AIzaSyDj9...
```

---

## 🚨 IMPORTANT: API Endpoint

**Gemini 3.1 uses NATIVE Google API, NOT OpenAI compatible:**

```javascript
// Native Google API (REQUIRED for 3.1)
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent

// NOT the OpenAI endpoint!
POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions  // ❌ Won't work
```

---

## 📡 API Configuration

### Native Google API (for 3.1 Pro)
```javascript
const response = await fetch(
  `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key=${API_KEY}`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        maxOutputTokens: 8192,
        temperature: 0.2
      }
    })
  }
);
```

### OpenAI Compatible (for 2.5 Flash)
```javascript
// Works with OpenAI-compatible apps
POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
```

---

## 🛠 CustomTools Endpoint

### What it does:
- **Better tool prioritization**: Uses custom tools (view_file, search_code) instead of generic bash
- **Less hallucinations**: More reliable file operations
- **Agent-optimized**: Built for coding agents

### Function Declarations (Recommended Names)
```javascript
{
  "tools": [{
    "function_declarations": [
      {
        "name": "view_file",
        "description": "Read a file from the filesystem",
        "parameters": {
          "type": "object",
          "properties": {
            "path": { "type": "string" }
          }
        }
      },
      {
        "name": "search_code",
        "description": "Search for code patterns",
        "parameters": {
          "type": "object",
          "properties": {
            "query": { "type": "string" }
          }
        }
      },
      {
        "name": "execute_bash",
        "description": "Execute a bash command",
        "parameters": {
          "type": "object",
          "properties": {
            "command": { "type": "string" }
          }
        }
      }
    ]
  }]
}
```

---

## 🔍 Available Models on Your Keys

| Model | Type | Available |
|-------|------|-----------|
| `gemini-3.1-pro-preview` | Reasoning | ✅ |
| `gemini-3.1-pro-preview-customtools` | Agent Tools | ✅ |
| `gemini-3.1-flash-lite-preview` | Fast | ✅ |
| `gemini-2.5-pro` | Reasoning | ✅ |
| `gemini-2.5-flash` | Balance | ✅ |

---

## 🧠 Thinking Mode

Gemini 3.1 has enhanced thinking:

```javascript
{
  "model": "gemini-3.1-pro-preview",
  "contents": {
    "parts": [{ "text": "Your complex research query" }]
  },
  "generationConfig": {
    "thinkingConfig": {
      "thinkingBudgetTokens": 16384
    }
  }
}
```

---

## 🔄 Auto-Research Loop

```
┌─────────────────────────────────────────────────────────┐
│                   DEEP RESEARCH LOOP                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Gemini 3.1 analyzes query                           │
│  2. Generates search strategy                           │
│  3. Uses google_search for web grounding               │
│  4. Synthesizes findings                               │
│  5. Identifies gaps                                     │
│  6. Iterates if needed                                  │
│  7. Final comprehensive report                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Research Prompt Template
```javascript
const researchPrompt = `
PERFORM DEEP RESEARCH on: {TOPIC}

Requirements:
1. Use google_search for current information
2. Cite sources with URLs
3. Identify knowledge gaps
4. Provide actionable recommendations

Output: Comprehensive Markdown report
`;
```

---

## 📊 Rate Limit Strategy (4 Keys)

```javascript
class ResearchRouter {
  constructor() {
    this.keys = [
      '${GEMINI_API_KEY}',
      '${GEMINI_API_KEY}',
      '${GEMINI_API_KEY}',
      '${GEMINI_API_KEY}'
    ];
    this.index = 0;
  }

  getKey() {
    const key = this.keys[this.index];
    this.index = (this.index + 1) % this.keys.length;
    return key;
  }
}
```

---

## 🎯 Model Selection Guide

| Task | Model | Why |
|------|-------|-----|
| **Coding Agent** | 3.1-pro-customtools | Best tool use |
| **Deep Research** | 3.1-pro-preview | Best reasoning |
| **Quick Analysis** | 2.5-flash | Fast, cheap |
| **Long Context** | 3.1-pro (1M) | 1M tokens |

---

## 🚀 Quick Usage

### Deep Research (Native API)
```bash
# Use the research script with 3.1
node scripts/deep-research-loop.js "AI agent frameworks 2026"
```

### Coding Agent (CustomTools)
```bash
# Use OpenCode with customtools model
opencode run --model google/gemini-3.1-pro-preview-customtools "Create a React component"
```

### Quick Analysis (OpenAI Compatible)
```bash
# Use Gemini CLI
gemini -p "Analyze this code architecture" -m gemini-2.5-flash
```

---

## 📁 Files

- `scripts/deep-research-loop.js` - Auto-research
- `scripts/research-router.js` - Key rotation
- `scripts/swal-project-manager.js` - Project tracking

---

**Version:** 2.0 (Gemini 3.1 Pro)
**Updated:** 2026-04-20
**Status:** ✅ Ready with Gemini 3.1 Pro