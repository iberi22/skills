---
name: dom-pipeline
description: DOM extraction and AI processing pipeline for browser automation. Use when building DOM-based AI tools, web automation, or text-based page understanding systems.
version: "1.0.0"
updated: "2026-04-23"
author: swal
license: MIT
argument-hint: 'Describe the DOM task or pipeline component to implement'
---

# DOM Pipeline

Text-based DOM manipulation pipeline — no screenshots, no multi-modal LLMs needed.

## Pipeline Stages

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DOM Extraction                                           │
│    Live DOM → FlatDomTree                                   │
│    (page-controller/src/dom/dom_tree/)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Dehydration                                             │
│    Full DOM → Simplified HTML                               │
│    Remove: styles, scripts, hidden elements, noise          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. LLM Processing                                           │
│    Simplified text → Action plan                            │
│    Tool definitions + system prompt                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Indexed Operations                                       │
│    Action → PageController method calls by index           │
│    clickElement(42), inputText(15, "hello")                │
└─────────────────────────────────────────────────────────────┘
```

## FlatDomTree Structure

```typescript
interface FlatDomTree {
  nodes: DomNode[]        // Flat list with depth info
  parent_map: Map<number, number>  // index → parent index
  element_map: Map<number, HTMLElement>  // index → actual element
}

interface DomNode {
  index: number
  tag: string             // 'button', 'input', 'div', etc.
  text: string            // Visible text content
  depth: number           // DOM nesting level
  attributes: Record<string, string>
  interactable: boolean    // Can this element be interacted with?
  visible: boolean
  disabled: boolean
}
```

## Dehydration Rules

Remove from DOM before sending to LLM:

| Remove | Why |
|--------|-----|
| `<style>` tags | No visual info for text LLM |
| `<script>` tags | Executed, not displayed |
| `display: none` | Not visible to user |
| `visibility: hidden` | Not visible to user |
| `aria-hidden: true` | Hidden from accessibility tree |
| Inline styles | Often noise for decision making |
| CSS classes | LLM doesn't render CSS |

Keep:
- Semantic tags (`button`, `input`, `a`, `select`)
- `data-*` attributes (often have meaning)
- `aria-label`, `placeholder`, `title`
- Form field names and IDs
- Interactive element text content

## Index-Based Operations

Instead of passing DOM elements to LLM:

```typescript
// ❌ Bad: fragile, breaks on re-render
LLM: "Click the <button class='btn-primary'>Submit</button>"

// ✅ Good: stable index
LLM: "Click element 42"
PageController: clickElement(42)

// Element 42 mapping is maintained by PageController internally
```

## Element Index Table (sent to LLM)

```
┌───────┬────────┬─────────────────────────┬──────────────────┐
│ Index │ Tag    │ Text / Label           │ Attributes       │
├───────┼────────┼─────────────────────────┼──────────────────┤
│ 0     │ body   │                        │                  │
│ 1     │ nav    │ My App                 │                  │
│ 2     │ button │ Login                 │ aria-label="Log" │
│ 3     │ input  │                      │ type="email"      │
│ ...   │ ...    │ ...                   │ ...              │
│ 42    │ button │ Submit                │ type="submit"    │
└───────┴────────┴─────────────────────────┴──────────────────┘
```

## PageController Interface

```typescript
interface PageController {
  // Tree management
  updateTree(): Promise<void>           // Re-extract DOM
  getSimplifiedHTML(): string           // Get dehydrated DOM
  getPageInfo(): PageInfo               // URL, title, etc.

  // Element operations (by index)
  clickElement(index: number): Promise<void>
  inputText(index: number, text: string): Promise<void>
  selectOption(index: number, value: string): Promise<void>
  hoverElement(index: number): Promise<void>

  // Navigation
  scroll(direction: 'up' | 'down', pages?: number): Promise<void>
  goBack(): Promise<void>
  goForward(): Promise<void>
  navigateTo(url: string): Promise<void>

  // Wait conditions
  waitForSelector(selector: string, timeout?: number): Promise<void>
  waitForNavigation(callback: () => Promise<void>): Promise<void>
}

interface PageInfo {
  url: string
  title: string
  viewport: { width: number, height: number }
}
```

## Tool Definition Pattern

```typescript
interface Tool {
  name: string
  description: string
  parameters: z.ZodSchema
  execute: (params: unknown, controller: PageController) => Promise<ToolResult>
}

const tools: Tool[] = [
  {
    name: 'click',
    description: 'Click an interactive element',
    parameters: z.object({ index: z.number() }),
    execute: async ({ index }, controller) => {
      await controller.clickElement(index)
      await controller.updateTree()
      return { success: true, html: controller.getSimplifiedHTML() }
    }
  },
  {
    name: 'input',
    description: 'Type text into an input field',
    parameters: z.object({ index: z.number(), text: z.string() }),
    execute: async ({ index, text }, controller) => {
      await controller.inputText(index, text)
      return { success: true }
    }
  }
]
```

## Visual Mask (Optional)

Overlay that blocks user interaction during automation:

```typescript
// SimulatorMask shows agent's target element
// Prevents user from interfering with automation
const mask = new SimulatorMask(container)
mask.highlight(42)  // Highlight element 42
mask.block()        // Block all clicks
mask.release()      // Allow interaction again
```

## Error Handling

| Error | Recovery Strategy |
|-------|-------------------|
| Element stale | Re-call `updateTree()` and retry |
| Element moved | Re-index and retry with new index |
| Navigation needed | Call `waitForNavigation()` wrapper |
| LLM timeout | Retry with exponential backoff |
| Invalid action | Return error to LLM for replanning |

## Best Practices

1. **Always `updateTree()` after DOM-changing actions** — indices change
2. **Include `waitFor` tools** — pages load asynchronously
3. **Batch operations when possible** — reduce round trips to LLM
4. **Include page context** — URL, title help LLM understand state
5. **Track element stability** — indices can change on DOM updates
