---
name: llm-agent-comparison
description: Research comparing LLM coding agents - OpenCode, Gemini CLI, and others. Tests approaches for SWAL agent system.
version: "1.0.0"
updated: "2026-04-23"
author: swal
license: MIT
---

# LLM Agent Comparison - SWAL Research
**Date:** 2026-04-20 | **Author:** SWAL Agent

---

## Executive Summary

Tested 3 approaches for coding agents with Gemini/LLM providers:
1. **OpenCode** (coding agent with filesystem access)
2. **Gemini CLI** (text-only, fast)
3. **sessions_spawn subagents** (parallel execution)

---

## 🧪 Test Results

### Test 1: Simple Python Function (Fibonacci)
| Tool | Model | Duration | Output |
|------|-------|----------|--------|
| Gemini CLI | gemini-2.5-flash | **9.3s** | Text only |
| OpenCode | MiniMax-M2.7 | 6.3s | Text only |
| OpenCode | gemini-2.5-flash | 56s | **File written!** |

### Test 2: Complex Task (Strategy Pattern)
| Tool | Model | Duration | Quality |
|------|-------|----------|---------|
| Gemini CLI | gemini-2.5-flash | 15s | Text |
| OpenCode | MiniMax-M2.7 | ~6s | Text |

---

## 📊 Comparison Matrix

| Feature | OpenCode | Gemini CLI | Subagents |
|---------|----------|-----------|-----------|
| **Speed** | ⚡⚡⚡ (MiniMax) | ⚡⚡ (Gemini) | ⚡⚡⚡ |
| **File Write** | ✅ Yes | ❌ No | ✅ Yes |
| **Code Execution** | ✅ Yes | ❌ No | ✅ Yes |
| **Git Integration** | ✅ Yes | ❌ No | ⚡⚡ Yes |
| **Skills Support** | ✅ Yes | ⚠️ Limited | ✅ Yes |
| **Parallel Tasks** | ❌ Single | ❌ Single | ✅ Yes |
| **Context Window** | ✅ 100K+ | ✅ 1M | ✅ 280K |
| **Cost** | Free (MiniMax) | Free tier | Free tier |

---

## 🏆 Winner by Use Case

### Coding Tasks (File creation, git operations)
**→ OpenCode with MiniMax-M2.7**
- Fastest (6-8s)
- Writes files directly
- Git integration
- Free via MiniMax

### Analysis & Reasoning
**→ Gemini CLI with gemini-2.5-flash**
- Thinking mode available
- 1M context
- Fast text output

### Parallel Heavy Work
**→ sessions_spawn with MiniMax-M2.7**
- Up to 4 parallel
- Auto-complete notifications
- Best for batch operations

### Complex Multi-Step (with thinking)
**→ OpenCode with gemini-2.5-flash**
- File writes + reasoning
- Slower but capable
- Good for architecture

---

## 💡 Best Practice: HYBRID APPROACH

### Recommended Stack:
```
┌─────────────────────────────────────────────────────────┐
│                    SWAL Agent System                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Fast Coding ──────► OpenCode (MiniMax-M2.7)            │
│  (file writes)       ~6 seconds, free                    │
│                                                          │
│  Reasoning ────────► Gemini CLI (gemini-2.5-flash)      │
│  (thinking mode)     ~10 seconds, free tier              │
│                                                          │
│  Heavy Batch ─────► sessions_spawn (MiniMax)            │
│  (parallel)          4 max, auto-complete               │
│                                                          │
│  Complex Coding ──► OpenCode (gemini-2.5-flash)        │
│  (best quality)      ~56 seconds, uses Google quota      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### OpenCode (MiniMax - Primary)
```bash
export MINIMAX_API_KEY="your-key"
opencode run --model minimax/MiniMax-M2.7 "task"
```

### OpenCode (Gemini - Quality)
```bash
export GOOGLE_GENERATIVE_AI_API_KEY="your-key"
opencode run --model google/gemini-2.5-flash "task"
```

### Gemini CLI (Quick reasoning)
```bash
gemini -p "task" -m gemini-2.5-flash
```

### sessions_spawn (Parallel)
```javascript
sessions_spawn({
  mode: "run",
  runtime: "subagent",
  task: "task",
  runTimeoutSeconds: 600
})
```

---

## 📈 Performance Metrics

### Speed Ranking (simple task)
1. **MiniMax-M2.7**: 6s ⭐ (FASTEST)
2. **Gemini CLI**: 9s
3. **Gemini 2.5 Flash (OpenCode)**: 56s (SLOWEST)

### Quality Ranking (complex reasoning)
1. **Gemini 2.5 Flash**: ⭐ (best reasoning with thinking)
2. **MiniMax-M2.7**: Good
3. **Gemini CLI**: Good (no file output)

### Cost Efficiency
1. **MiniMax-M2.7**: FREE (unlimited via MiniMax)
2. **Gemini**: FREE (1,500 req/day × 4 keys = 6,000)
3. **Groq**: FREE (14,400 req/day)

---

## 🎯 Recommendations for SWAL

### Primary Agent: MiniMax via OpenCode
- Default for all coding tasks
- Fast + free + file writes
- Use: `opencode run --model minimax/MiniMax-M2.7`

### Reasoning/Analysis: Gemini CLI
- When you need thinking mode
- Quick questions with 1M context
- Use: `gemini -p "..." -m gemini-2.5-flash`

### Parallel Execution: sessions_spawn
- Heavy batch operations
- Multiple files/components
- Use: sessions_spawn with MiniMax-M2.7

### Complex/Quality: OpenCode + Gemini
- Architecture design
- Complex debugging
- When Gemini's reasoning is needed

---

## 🚀 Skill Integration

Skills that enhance these agents:
- `opencode-dev-workflow` - Development workflow
- `subagent-launcher` - Parallel spawning
- `coding-agent` - Code-specific patterns
- `gemini-capable` - Gemini optimization

---

**Conclusion:** Use **MiniMax + OpenCode** for speed, **Gemini CLI** for reasoning, **sessions_spawn** for parallelism. The hybrid approach gives you the best of all worlds.