---
name: gemini-key-pool
description: SWAL Gemini Key Pool Manager - Multiple Google AI API keys with automatic rotation and load balancing. Updated 2026-04-21.
version: "1.0.0"
updated: "2026-04-23"
author: swal
license: MIT
metadata:
  version: 1.0.0
---

# Gemini Key Pool Manager

> **⚡ Multiple Google AI API Keys with Automatic Failover**

## ⚠️ CRITICAL: Rate Limits are per PROJECT, NOT per API Key

Each Gemini API key must come from a **DIFFERENT Google AI Studio project** to bypass rate limits effectively.

- 1 Project = 1,500 requests/day + 15 RPM per key
- Multiple Projects = Multiply your capacity

---

## 📊 How It Works

```
Request → Key #1 → Success ✅
                ↓ (if 429)
         Key #2 → Success ✅
                ↓ (if 429)
         Key #3 → Success ✅
                ↓ (if exhausted)
         Return "All keys exhausted"
```

## 🎯 Features

- **Weighted Round-Robin**: Distribute load based on key capacity
- **Auto-Failover**: Automatically switch keys on 429/401/403 errors
- **1-Hour Cooldown**: Exhausted keys rest before retry
- **Daily Reset**: Automatic counter reset at midnight
- **Deep Research**: Multi-key iteration for complex research

---

## 🔑 Required Setup

### Create Multiple Google AI Studio Projects

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Create NEW project for each key you want
3. Generate API key for each project
4. Each project = 1,500 req/day independent limit

### Environment Variables

```bash
# Set up to 4 keys (each from different project)
export GOOGLE_API_KEY="your-key-1-from-project-1"
export GOOGLE_API_KEY_2="your-key-2-from-project-2"
export GOOGLE_API_KEY_3="your-key-3-from-project-3"
export GOOGLE_API_KEY_4="your-key-4-from-project-4"
```

---

## 📁 Script Location

### Usage Commands

```bash
# Check status of all keys
node scripts/gemini-key-pool.js status

# Test all keys
node scripts/gemini-key-pool.js test

# Make a request
node scripts/gemini-key-pool.js call --prompt "Hello Gemini" --model gemini-3.1-pro

# Deep research with multiple iterations
node scripts/gemini-key-pool.js research "Explain quantum computing"
```

---

## 📊 Status Output Example

```
🔑 GEMINI KEY POOL STATUS
============================================================
Date: 2026-04-21
Active Keys: 4

🟢 Google #1   | Req:  234/1500 | Total:  4821 | Weight: 1
🟢 Google #2   | Req:  567/1500 | Total: 12034 | Weight: 1
🟡 Google #3   | Req: 1203/1500 | Total: 28432 | Weight: 1
🟢 Google #4   | Req:   89/1500 | Total:  1203 | Weight: 1

📊 Available keys: 4/4
============================================================
```

---

## 🔄 Integration with LLM Router

The key pool integrates with the existing LLM router:

```javascript
const { GeminiKeyPool } = require('./gemini-key-pool.js');
const pool = new GeminiKeyPool();

// Use for deep research
const result = await pool.deepResearch("Complex research query", 3);

// Or for single calls with auto-failover
const result = await pool.complete({ 
  prompt: "Your prompt here", 
  model: "gemini-3.1-pro" 
});
```

### Key Pool Status Display

| Status | Meaning | Action |
|--------|---------|--------|
| 🟢 OK | Key healthy, <50% used | Normal use |
| 🟡 MEDIUM | Key at 50-80% | Consider switching |
| 🔴 HIGH | Key at 80-100% | Switch provider |
| ⏸️ EXHAUSTED | Rate limited | Wait 1 hour |

---

## 💡 Best Practices

### For Maximum Capacity

1. **Create 4+ Google projects** - Each = 1,500 req/day
2. **Rotate keys wisely** - Don't exhaust all at once
3. **Use Gemini 3.1 Pro** - Only for tasks needing 1M context
4. **Use Gemini 2.0 Flash** - For everything else (faster, cheaper)

### Capacity Calculation

| Keys | Requests/Day | Use Case |
|------|--------------|----------|
| 1 | 1,500 | Light usage |
| 2 | 3,000 | Moderate usage |
| 4 | 6,000 | Heavy usage (our config) |
| 8 | 12,000 | Professional tier |

---

## 🔧 Troubleshooting

### "All keys exhausted"
- Wait 1 hour for cooldown
- Check if all projects have remaining quota
- Consider adding more keys

### "Rate limit still hitting"
- Each key MUST be from DIFFERENT project
- Same project = same quota pool
- Check [Google AI Studio quotas](https://ai.google.com/studio)

### Keys failing with 401/403
- API key may be invalid
- Check if project is still active
- Regenerate key if needed

---

**Version:** 1.0.0
**Updated:** 2026-04-21
**Status:** ✅ OPERATIONAL
