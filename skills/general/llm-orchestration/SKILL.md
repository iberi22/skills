---
name: llm-orchestration
description: "SWAL Unified LLM Orchestration - Combines resource monitoring, multi-key Gemini management, and OpenRouter routing. Intelligent provider selection for code, fast, deep, and reasoning tasks. Version 1.0 | Updated 2026-04-23"
metadata:
  author: swal
  updated: "2026-04-23"
  openclaw:
    autoLoad: false
  version: "1.0.0"
  unified: "2026-04-23"
---

# LLM Orchestration — Unified SWAL LLM Provider System

> **⚡ Intelligent Routing Across All LLM Providers**

Combines `llm-resource-monitor` + `gemini-key-pool` + `openrouter` into a single unified orchestration system.

---

## 🎯 PURPOSE

Unified monitoring and intelligent orchestration of all LLM providers:

1. **Scans** provider capabilities (context, limits, cost)
2. **Tracks** usage in real-time (RPM, daily, tokens)
3. **Manages** multi-key failover (Gemini-specific)
4. **Routes** tasks to optimal provider based on requirements
5. **Orchestrates** intelligent fallback on rate limits

---

## 📊 UNIFIED PROVIDER STATUS

| Provider | Context | Daily Limit | RPM | Cost | Best For |
|----------|---------|-------------|-----|------|----------|
| 🟢 **Groq** | 128K | 14,400 | 30 | Free | Fast tasks, speed |
| 🔵 **Gemini #1-4** | 1M | 1,500/key | 15 | Free | Deep reasoning |
| 🟡 **DeepSeek** | 163K | 10,000 | 60 | $0.81 | Reasoning, cheap |
| 🟠 **OpenRouter** | 262K | 200 | 20 | $0.35 | Model variety |
| 🟣 **MiniMax** | ∞ | ∞ | ∞ | Unlimited | Coding, fallback |
| 🔵 **Codex (GPT-5.4)** | 258K→1M | 30-150/5h | varies | Plus | Heavy coding |

---

## 🚀 USAGE

### Dashboard (Full Status)
```bash
node scripts/llm-resource-monitor.js status
```

### Best Provider for Task
```bash
node scripts/llm-resource-monitor.js best code
node scripts/llm-resource-monitor.js best fast
node scripts/llm-resource-monitor.js best deep
node scripts/llm-resource-monitor.js best cheap
```

### Intelligent Orchestration
```bash
node scripts/llm-resource-monitor.js orchestrate code 50000
```

### Record Usage
```bash
node scripts/llm-resource-monitor.js record groq 500
```

---

## 🔑 GEMINI KEY POOL (Multi-Key Management)

**⚠️ CRITICAL:** Each key must be from a DIFFERENT Google AI Studio project.

### Environment Variables
```bash
export GOOGLE_API_KEY="key-from-project-1"
export GOOGLE_API_KEY_2="key-from-project-2"
export GOOGLE_API_KEY_3="key-from-project-3"
export GOOGLE_API_KEY_4="key-from-project-4"
```

### Check Status
```bash
node scripts/gemini-key-pool.js status
```

### Make a Request
```bash
node scripts/gemini-key-pool.js call --prompt "..." --model gemini-3.1-pro
```

### Deep Research
```bash
node scripts/gemini-key-pool.js research "complex query"
```

### Key Status Display

| Status | Meaning | Action |
|--------|---------|--------|
| 🟢 OK | <50% used | Normal use |
| 🟡 MEDIUM | 50-80% | Consider switching |
| 🔴 HIGH | 80-100% | Switch provider |
| ⏸️ EXHAUSTED | Rate limited | Wait 1 hour |

### Capacity Calculation

| Keys | Requests/Day | Use Case |
|------|--------------|----------|
| 1 | 1,500 | Light usage |
| 2 | 3,000 | Moderate usage |
| 4 | 6,000 | Heavy usage (recommended) |

---

## 🌐 OPENROUTER (Free Models)

### Free Models Available

| Model | Context | Best For |
|-------|---------|----------|
| **DeepSeek R1** | 128K | Reasoning, debugging |
| **Qwen3.5-9B** | 32K | Light tasks, quick fixes |
| **Elephant Alpha** | 256K | General intelligence |
| **Qwen3.6 Plus Preview** | 1M | Complex analysis |

### Setup
```bash
# Set API key
export OPENROUTER_API_KEY="sk-or-v1-your-key"

# Configure in OpenCode
opencode run --model deepseek/deepseek-r1 "task"
```

---

## 🎯 TASK TYPE ROUTING

| Task | Primary | Secondary | Notes |
|------|---------|-----------|-------|
| `code` | MiniMax | Groq | OpenCode for coding |
| `fast` | Groq | MiniMax | Groq for speed |
| `deep` / `research` | Gemini #1-4 | DeepSeek | 1M context |
| `reasoning` | DeepSeek | Groq | Reasoning tasks |
| `cheap` | DeepSeek | OpenRouter | Budget-friendly |
| `heavy` | Codex (GPT-5.4) | MiniMax | Plus account |

---

## 🔍 SCANNING LOGIC

The scanner evaluates:

1. **Context Match** — Can handle tokens needed?
2. **Daily Limit** — Enough remaining quota?
3. **RPM** — Under rate limit currently?
4. **Cost** — Within budget?
5. **Strengths** — Task-specific optimizations?

Output: Ranked list of providers with scores.

---

## ⚠️ ALERT LEVELS

| Level | Meaning | Action |
|-------|---------|--------|
| 🟢 OK | <60% | Normal operation |
| 🟡 WARNING | 60-80% | Monitor closely |
| 🔴 CRITICAL | 80-100% | Consider fallback |
| ⚫ EXHAUSTED | 100% | Use fallback immediately |
| ⏸️ COOLDOWN | Rate limited | Wait for cooldown |

---

## 🔄 INTEGRATION POINTS

### From LLM Router
```javascript
const { ResourceMonitor } = require('./llm-resource-monitor.js');
const monitor = new ResourceMonitor();
const best = monitor.getBestProvider('code', 50000);
```

### From Gemini Key Pool
```javascript
// After 429 error, mark cooldown
monitor.setCooldown('gemini-1', new Date(Date.now() + 60000));
```

### Record After API Call
```javascript
monitor.record('groq', 2500);
```

---

## 📁 DATA FILES

| File | Purpose |
|------|---------|
| `config/llm-resource-state.json` | Current usage state |
| `config/llm-providers.json` | Provider configurations |
| `config/llm-capability-scan.json` | Last capability scan |

---

## 💡 BEST PRACTICES

### For Maximum Capacity
1. **Create 4+ Google projects** for Gemini — Each = 1,500 req/day
2. **Use MiniMax for coding** — Unlimited, fast
3. **Use Groq for quick tasks** — Fast, free
4. **Reserve Gemini for deep research** — 1M context when needed

### Model Selection Quick Guide
```
Heavy coding → Codex (GPT-5.4) or MiniMax
Fast tasks → Groq
Deep research → Gemini 3.1 Pro (1M context)
Reasoning/debugging → DeepSeek R1
Budget tasks → DeepSeek or OpenRouter
```

---

## Related Skills

- `free-llm-providers` — Provider details and API setup
- `subagent-launcher` — Subagent orchestration
- `xavier-memory` — Xavier memory integration

**Version:** 1.0.0
**Unified:** 2026-04-23
**Status:** ✅ OPERATIONAL
