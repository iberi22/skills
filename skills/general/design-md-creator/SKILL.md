---
name: design-md-creator
description: Create DESIGN.md design system files from websites or existing UIs. Use when starting a new frontend project, documenting an existing design, or creating design references for AI agents. Based on Google Stitch's DESIGN.md concept.
version: "1.0.0"
updated: "2026-04-23"
author: swal
license: MIT
argument-hint: 'URL or description of the design to document'
---

# DESIGN.md Creator

Create a DESIGN.md design system file — plain-text documentation that AI agents read to generate consistent UI.

## What is DESIGN.md?

| File | Who reads it | What it defines |
|------|-------------|-----------------|
| `AGENTS.md` | Coding agents | How to build the project |
| `DESIGN.md` | Design agents | How the project should look and feel |

DESIGN.md is a markdown file describing visual design — colors, typography, spacing, components. No Figma exports, no JSON schemas, no special tooling.

## When to Use

- ✅ Starting a new frontend project
- ✅ Documenting an existing UI for future AI work
- ✅ Creating reference designs for brand consistency
- ✅ Capturing design decisions from a website

## DESIGN.md Format

Values below are illustrative placeholders showing the shape only; derive every token from the source site or brand, and avoid defaulting to indigo accents or Inter.

### Section 1: Visual Theme & Atmosphere

```markdown
## Visual Theme & Atmosphere

**Mood:** [e.g., Professional yet approachable, technical and precise]
**Density:** [e.g., Spacious, content-focused]
**Design Philosophy:** [e.g., Form follows function, accessibility first]
**Brand Personality:** [e.g., Bold and confident, playful and friendly]
```

### Section 2: Color Palette & Roles

```markdown
## Color Palette & Roles

| Token | Hex | RGB | Functional Role |
|-------|-----|-----|-----------------|
| primary | #6366F1 | 99, 102, 241 | Brand, CTAs, links |
| secondary | #8B5CF6 | 139, 92, 246 | Accent highlights |
| success | #10B981 | 16, 185, 129 | Positive actions, confirmations |
| warning | #F59E0B | 245, 158, 11 | Alerts, caution states |
| error | #EF4444 | 239, 68, 68 | Errors, destructive actions |
| background | #FFFFFF | 255, 255, 255 | Page background |
| surface | #F9FAFB | 249, 250, 251 | Card, modal backgrounds |
| text-primary | #111827 | 17, 24, 39 | Headlines, body text |
| text-secondary | #6B7280 | 107, 114, 128 | Captions, placeholders |
| border | #E5E7EB | 229, 231, 235 | Dividers, input borders |
```

### Section 3: Typography Rules

```markdown
## Typography Rules

**Font Family:**
- Display/Headings: Inter (Google Fonts), fallback: system-ui
- Body: Inter, fallback: system-ui
- Code/Monospace: JetBrains Mono, fallback: monospace

**Type Scale (1.25 ratio):**
| Element | Size | Weight | Line Height | Letter Spacing |
|---------|------|--------|-------------|----------------|
| Display | 48px | 700 | 1.2 | -0.02em |
| h1 | 36px | 700 | 1.25 | -0.01em |
| h2 | 30px | 600 | 1.3 | 0 |
| h3 | 24px | 600 | 1.35 | 0 |
| body | 16px | 400 | 1.5 | 0 |
| small | 14px | 400 | 1.5 | 0 |
| caption | 12px | 500 | 1.4 | 0.02em |
```

### Section 4: Component Stylings

```markdown
## Component Stylings

### Buttons

**Primary Button:**
- Background: primary (#6366F1)
- Text: white (#FFFFFF)
- Padding: 12px 24px
- Border radius: 8px
- Font: 16px, weight 600
- Shadow: 0 1px 3px rgba(0,0,0,0.1)
- Hover: brightness(1.1), translateY(-1px)
- Active: brightness(0.95), translateY(0)
- Disabled: opacity 0.5, cursor not-allowed
- Loading: spinner icon, disabled interaction

**Secondary Button:**
- Background: transparent
- Border: 1px solid primary
- Text: primary
- Same sizing as Primary

**Ghost Button:**
- Background: transparent
- Text: text-secondary
- Hover: background surface

### Cards
- Background: white or surface
- Border: 1px solid border
- Border radius: 12px
- Padding: 24px
- Shadow: 0 4px 6px rgba(0,0,0,0.05)
- Hover (if interactive): shadow-lg, translateY(-2px)

### Form Inputs
- Height: 44px
- Border: 1px solid border
- Border radius: 8px
- Padding: 0 16px
- Focus: ring-2 primary, border-primary
- Error: border-error, ring-error
- Disabled: background gray-100, opacity 0.7
```

### Section 5: Layout Principles

```markdown
## Layout Principles

**Base Unit:** 4px

**Spacing Scale:**
| Token | Value | Usage |
|-------|-------|-------|
| 0 | 0px | |
| 1 | 4px | Tight gaps |
| 2 | 8px | Icon gaps |
| 3 | 12px | Inline spacing |
| 4 | 16px | Standard gap |
| 6 | 24px | Section gaps |
| 8 | 32px | Component spacing |
| 12 | 48px | Section padding |
| 16 | 64px | Large section gaps |

**Grid System:**
- Columns: 12
- Gutter: 24px
- Max width: 1280px
- Breakpoints: 640px (sm), 768px (md), 1024px (lg), 1280px (xl)

**Whitespace Philosophy:**
- Sections: 64px vertical padding minimum
- Components: 24px internal padding
- Cards: 24px padding, 16px gap between
```

### Section 6: Depth & Elevation

```markdown
## Depth & Elevation

**Shadow System:**
| Level | Value | Usage |
|-------|-------|-------|
| sm | 0 1px 2px rgba(0,0,0,0.05) | Subtle, inline elements |
| md | 0 4px 6px rgba(0,0,0,0.1) | Cards, dropdowns |
| lg | 0 10px 15px rgba(0,0,0,0.1) | Modals, popovers |
| xl | 0 20px 25px rgba(0,0,0,0.15) | Dialogs, overlays |

**Border Widths:**
- Thin: 1px (dividers, inputs)
- Medium: 2px (focus rings)
- Strong: 4px (active states)

**Border Radius:**
| Token | Value | Usage |
|-------|-------|-------|
| none | 0 | Sharp edges |
| sm | 4px | Small badges |
| md | 8px | Buttons, inputs |
| lg | 12px | Cards |
| xl | 16px | Large cards |
| full | 9999px | Pills, avatars |
```

### Section 7: Do's and Don'ts

```markdown
## Do's and Don'ts

**DO:**
- ✅ Use primary color for primary CTAs only
- ✅ Maintain 4px base unit for all spacing
- ✅ Use semantic colors for state feedback
- ✅ Keep typography scale consistent
- ✅ Design for mobile-first

**DON'T:**
- ❌ Use more than 3 font weights
- ❌ Mix multiple typefaces
- ❌ Use color alone for information (always pair with icons/text)
- ❌ Hardcode pixel values outside spacing scale
- ❌ Create custom shadows outside the shadow system
```

### Section 8: Responsive Behavior

```markdown
## Responsive Behavior

**Breakpoints:**
| Name | Width | Columns | Gutter |
|------|-------|---------|--------|
| mobile | < 640px | 4 | 16px |
| tablet | 640-1023px | 8 | 24px |
| desktop | 1024-1279px | 12 | 24px |
| large | ≥ 1280px | 12 | 24px |

**Touch Targets:**
- Minimum: 44x44px (WCAG 2.1)
- Recommended: 48x48px

**Mobile Considerations:**
- Hamburger menu below tablet
- Bottom navigation on mobile apps
- Cards stack vertically
- Typography scales down 10-15%
```

### Section 9: Agent Prompt Guide

```markdown
## Agent Prompt Guide

### Quick Color Reference
```
Primary: #6366F1
Success: #10B981
Background: #FFFFFF
Text: #111827
```

### Ready-to-Use Prompts
- "Build a landing page following DESIGN.md"
- "Create a form with validation matching the design system"
- "Add dark mode support following the existing color tokens"
- "Implement a card grid with responsive breakpoints"
```

## Creation Workflow

### Option 1: From Website URL
```
1. Use page-agent to navigate to URL
2. Inspect key pages (home, features, pricing, contact)
3. Extract: colors (computed styles), fonts, spacing, components
4. Create DESIGN.md following format above
```

### Option 2: From Screenshot/Image
```
1. Use image analysis to extract colors
2. Identify typography from visual inspection
3. Note component patterns
4. Create DESIGN.md from observations
```

### Option 3: From Scratch (Brand Guidelines)
```
1. Apply brand colors to palette section
2. Set typography from brand fonts
3. Define spacing based on brand consistency
4. Document components from brand patterns
```

## Output Location

Save to one of:
- `DESIGN.md` (project root)
- `docs/DESIGN.md`
- `design/DESIGN.md`

## Reference Designs

| Brand | Style |
|-------|-------|
| claude | Warm terracotta, editorial |
| linear | Ultra-minimal, purple accent |
| vercel | Black/white, Geist font |
| stripe | Purple gradients, elegant |
| supabase | Dark emerald, code-first |
| figma | Vibrant multi-color |
| apple | Premium white space |

## Tips for Good DESIGN.md

1. **Be specific** — Include actual hex values, not "blue-ish"
2. **Include all states** — Hover, active, disabled, error
3. **Document spacing** — Don't leave gaps undefined
4. **Keep it updated** — DESIGN.md drifts from reality
5. **Test with agents** — Run an AI agent with it and refine
