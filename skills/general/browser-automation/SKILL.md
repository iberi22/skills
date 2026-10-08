---
name: browser-automation
description: Create AI agents that control web pages using natural language. Based on Alibaba's page-agent architecture. Use when building browser AI copilots, web automation agents, or DOM-based tool systems.
version: "1.0.0"
updated: "2026-04-23"
license: MIT
argument-hint: 'Describe the automation task or browser agent to build'
---

# Browser Automation Agent

Build AI agents that control web interfaces with natural language — no browser extensions, no Python, no headless browsers. Everything happens in-page.

## Architecture Pattern (page-agent style)

```
User Action (natural language)
    ↓
Agent (LLM + Tools)
    ↓
PageController (DOM operations)
    ↓
Web Page (actual browser DOM)
```

## Core Components

### 1. PageController
Handles all DOM operations — no LLM dependency.

```typescript
// Core methods every PageController must implement
class PageController {
  async updateTree()           // Extract live DOM
  async getSimplifiedHTML()    // Dehydrate for LLM
  async getPageInfo()          // Page metadata
  async clickElement(index)    // Indexed element interaction
  async inputText(index, text) // Form input
  async scroll(direction)      // Navigation
}
```

### 2. Agent Brain (LLM Client)
Stateless LLM client with retry logic and reflection-before-action.

```typescript
interface AgentConfig {
  model: string
  baseURL: string
  apiKey: string
  language: string
}
```

### 3. Tool System
Tools are defined as functions that the LLM can call. Each tool:
1. Calls PageController for DOM operations
2. Returns structured result to LLM
3. LLM decides next action

## Key Files to Create

| File | Purpose |
|------|---------|
| `PageController.ts` | DOM extraction + element operations |
| `Agent.ts` | LLM client + tool executor + ReAct loop |
| `tools/index.ts` | Tool definitions |
| `prompts/system.md` | System prompt for the agent |
| `types.ts` | TypeScript interfaces |

## DOM Pipeline

```
1. Live DOM → FlatDomTree (page-controller)
2. FlatDomTree → Simplified text (dehydration)
3. Simplified text → LLM (action plan)
4. Action plan → PageController operations (by index)
```

## Quick Start Pattern

```typescript
import { PageAgent } from 'page-agent'

const agent = new PageAgent({
  model: 'qwen3.5-plus',
  baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  apiKey: process.env.API_KEY,
  language: 'en-US',
})

await agent.execute('Click the login button')
```

## Monorepo Structure Pattern

```
packages/
├── core/                    # Agent logic without UI (stateless)
├── page-controller/         # DOM operations (no LLM dependency)
├── llms/                    # LLM client with retry/reflection
├── ui/                      # Optional panel/overlay
└── page-agent/              # Main entry (core + controller + ui)
```

## Best Practices

1. **Indexed operations** — Don't pass DOM elements to LLM, use integer indices
2. **Simplified HTML** — Remove noise (styles, scripts) before sending to LLM
3. **Retry logic** — LLM calls fail; implement exponential backoff
4. **Visual feedback** — Optional mask overlay shows agent actions to user
5. **No screenshots** — Text-based DOM manipulation only (faster, cheaper)

## When to Use

- ✅ Building an AI copilot for a web app
- ✅ Automating form filling workflows
- ✅ Creating accessibility overlays
- ✅ Multi-page browser agents
- ❌ Server-side scraping (use puppeteer/playwright instead)
- ❌ Complex visual tasks requiring screenshots

## Integration Options

| Approach | Use Case |
|----------|----------|
| NPM package | Full control, custom UI |
| Chrome extension | Multi-page tasks |
| MCP Server | External agent control |
| IIFE script tag | Quick integration |

## Not the same as agentic testing

This skill builds agents that operate a page for a user (copilots, DOM tools). To TEST an app with an agent —
natural-language steps, replay cache, exploratory bug bashes with repro tests — use `agentic-e2e`
(tester-army/e2e) instead.
