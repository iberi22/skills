---
name: page-agent-dev
description: Development workflow for Alibaba's page-agent monorepo. Use when working with page-agent packages, building browser AI agents, or extending the page-agent architecture.
version: "1.0.0"
updated: "2026-04-23"
author: swal
license: MIT
argument-hint: 'Describe the page-agent task or feature to implement'
---

# Page Agent Development

Working with the `iberi22/page-agent` fork or similar page-agent-based monorepos.

## Monorepo Structure

```
packages/
├── core/                    # PageAgentCore (headless, stateless)
│   └── src/
│       ├── PageAgentCore.ts  # Main agent class
│       ├── tools/            # Agent tools
│       ├── prompts/          # System prompts
│       └── types.ts         # Type definitions
├── page-controller/         # DOM operations (no LLM)
│   └── src/
│       ├── PageController.ts # Main controller
│       ├── actions.ts        # Element interactions
│       └── dom/              # DOM extraction
├── llms/                    # LLM client
│   └── src/
│       ├── index.ts          # Main LLM class
│       ├── OpenAIClient.ts   # OpenAI-compatible client
│       └── types.ts          # MacroToolInput, AgentBrain
├── ui/                      # Panel and i18n
├── page-agent/              # Main package (core + controller + ui)
└── website/                 # Documentation site
```

## Key Commands

```bash
npm run build        # Build all packages
npm run build:libs  # Build libraries only
npm run typecheck   # TypeScript type checking
npm run lint        # ESLint
```

## Architecture Principles

### 1. Layered Dependencies
```
page-agent
  ├── core (UI-less agent)
  │     ├── llms (LLM client)
  │     └── page-controller (DOM ops)
  └── ui (Panel)
```

### 2. ReAct Agent Loop

```
observe()  →  think()  →  act()  →  loop
   ↓           ↓          ↓
 DOM tree   LLM call   PageController
```

### 3. Tool Definition Contract

Tools follow `MacroToolInput` pattern:

```typescript
interface MacroToolInput {
  thought: string       // Reasoning
  action: {
    name: string         // Tool name
    args: Record<string, unknown>
  }
}
```

## Adding a New Tool

### Step 1: Add to PageController (if new DOM op)

```typescript
// packages/page-controller/src/actions.ts
export async function newAction(controller: PageController, index: number) {
  // Implementation
}
```

### Step 2: Expose in PageController class

```typescript
// packages/page-controller/src/PageController.ts
async newAction(index: number): Promise<void> {
  await actions.newAction(this, index)
}
```

### Step 3: Create Tool

```typescript
// packages/core/src/tools/index.ts
const newTool: PageAgentTool = {
  name: 'new_action',
  description: 'Does something useful',
  schema: z.object({ index: z.number() }),
  async execute({ index }, context) {
    await context.controller.newAction(index)
    return { success: true }
  }
}
```

### Step 4: Export from tools index

```typescript
// packages/core/src/tools/index.ts
export const tools: PageAgentTool[] = [
  // ... existing tools
  newTool
]
```

## PageController ↔ PageAgent Communication

```typescript
// All communication is async and isolated

// PageAgent (core) calls:
await this.pageController.updateTree()
await this.pageController.clickElement(index)
await this.pageController.getSimplifiedHTML()

// PageController exposes state via:
const simplifiedHTML = await this.pageController.getSimplifiedHTML()
const pageInfo = await this.pageController.getPageInfo()
```

## System Prompt Structure

```markdown
# Role
You are a web automation agent...

# Capabilities
- Click elements by index
- Type text into input fields
- Scroll the page
- Wait for elements to appear

# Rules
1. Always update the DOM tree after actions
2. Use simplified HTML for decisions
3. Index numbers are stable until DOM changes

# Output Format
{
  "thought": "Why I'm taking this action",
  "action": { "name": "click", "args": { "index": 42 } }
}
```

## Event System

```typescript
agent.on('statuschange', (status: AgentStatus) => {
  // idle → running → completed/error
})

agent.on('historychange', (events: HistoricalEvent[]) => {
  // Persistent agent memory
})

agent.on('activity', (activity: AgentActivity) => {
  // Real-time UI feedback (transient)
})
```

## Browser Integration Options

| Method | Use Case |
|--------|----------|
| NPM import | Full control, custom UI |
| IIFE script tag | Quick integration, no build |
| Chrome extension | Multi-page tasks |
| MCP Server | External agent control |

## Publishing Flow

```
src/*.ts (dev)
    ↓ [scripts/pre-publish.js]
dist/*.ts → dist/*.js (publish)
    ↓ [scripts/post-publish.js]
src/*.ts (restore)
```

## Development Workflow

1. **Clone**: `git clone https://github.com/iberi22/page-agent.git`
2. **Install**: `npm install`
3. **Dev**: `npm start` (website dev server)
4. **Build**: `npm run build:libs` (for library changes)
5. **Test**: Manual testing in browser
6. **PR**: Follow `.github/PULL_REQUEST_TEMPLATE.md`

## Common Patterns

### Retry with Backoff
```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (e) {
      if (i === maxRetries - 1) throw e
      await sleep(Math.pow(2, i) * 1000)
    }
  }
}
```

### Reflection Before Action
```typescript
// Before taking action, agent reflects on:
// 1. What happened in previous steps
// 2. Current page state
// 3. Whether to continue or replan
```

## File Naming Conventions

| Type | Convention |
|------|-----------|
| Source | `camelCase.ts` |
| Tests | `*.test.ts` |
| Types | `types.ts` |
| Index | `index.ts` |
| Constants | `UPPER_SNAKE_CASE.ts` |
