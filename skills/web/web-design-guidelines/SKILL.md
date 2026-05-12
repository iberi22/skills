---
id: web-design-guidelines
name: web-design-guidelines
category: web
tags:
  - web-design
  - accessibility
  - performance
  - ux
  - audit
goals:
  - "Review UI code for compliance with web interface best practices. Audits your code for 100+ rules covering accessibility, performance, and UX."
  - "Use when: 'Review my UI', 'Check accessibility', 'Audit design', 'Review UX', 'Check my site against best practices'."
context: |
  Inspired by Vercel's web-design-guidelines.
  Covers HTML, React, Vue components.
authors:
  - Brahyan Belalcazar
---

# Web Design Guidelines

Comprehensive UI audit skill for accessibility, performance, and UX best practices. Inspired by Vercel's web-design-guidelines.

## When to Use

Trigger on these requests:
- "Review my UI"
- "Check accessibility"
- "Audit design"
- "Review UX"
- "Check my site against best practices"
- "Fix accessibility issues"

## Rule Categories (100+ Rules)

### 🔴 Critical — Accessibility

| Rule | Description |
|------|-------------|
| `a11y-aria-labels` | All interactive elements have `aria-label` |
| `a11y-semantic-html` | Use `<button>`, `<nav>`, `<main>`, `<article>` instead of `<div>` |
| `a11y-keyboard-nav` | Focusable elements are keyboard navigable |
| `a11y-lang-attr` | `<html>` has `lang` attribute |
| `a11y-color-contrast` | Text has ≥4.5:1 contrast ratio |
| `a11y-image-alt` | All images have `alt` text |
| `a11y-form-labels` | All form inputs have associated labels |
| `a11y-error-messages` | Form errors are announced to screen readers |

### 🟡 High — Focus & Interaction

| Rule | Description |
|------|-------------|
| `focus-visible` | Custom focus styles use `:focus-visible`, not `:focus` |
| `focus-trap` | Modals trap focus within the dialog |
| `skip-link` | Page has skip-to-content link |
| `touch-target` | Touch targets ≥44x44px |
| `tap-highlight` | `tap-highlight-color` disabled on mobile |

### 🟢 Medium — Forms & Validation

| Rule | Description |
|------|-------------|
| `form-autocomplete` | Inputs use `autocomplete` attribute |
| `form-validation` | Inline validation on blur, not on submit |
| `form-error-style` | Errors are red, visible, and specific |
| `form-required-mark` | Required fields are visually marked |

### 🔵 Medium — Animation & Motion

| Rule | Description |
|------|-------------|
| `motion-reduced` | `prefers-reduced-motion` respected |
| `motion-safe` | Animations use `transform`/`opacity` only |
| `motion-duration` | No animation exceeds 300ms |
| `no-autooplay` | Videos/animations require user interaction |

### 🟣 Low-Medium — Typography

| Rule | Description |
|------|-------------|
| `typo-curly-quotes` | Use `"` and `"` (curly quotes), not straight |
| `typo-ellipsis` | Use `…` (ellipsis char), not three dots |
| `typo-tabular-nums` | Numbers in tables use `tabular-nums` |
| `typo-line-height` | Body text has line-height ≥1.5 |

### ⚫ Low — Performance

| Rule | Description |
|------|-------------|
| `perf-lazy-load` | Images below fold use `loading="lazy"` |
| `perf-preconnect` | Third-party origins use `<link rel="preconnect">` |
| `perf-font-display` | Web fonts use `font-display: swap` |
| `perf-no-layout-shift` | Images have explicit `width`/`height` |

### 🔘 Low — Dark Mode & Theming

| Rule | Description |
|------|-------------|
| `theme-color-scheme` | `<meta>` includes `color-scheme` |
| `theme-dark-mode` | Dark mode styles use `prefers-color-scheme` or CSS vars |
| `theme-toggle` | Theme switcher is accessible and visible |

### 🏁 Low — Images & Media

| Rule | Description |
|------|-------------|
| `img-width-height` | All images have explicit dimensions |
| `img-srcset` | Responsive images use `srcset` |
| `img-format` | Use WebP/AVIF over JPEG/PNG when possible |
| `video-captions` | Videos have captions/subtitles |

### Navigation & State

| Rule | Description |
|------|-------------|
| `nav-url-state` | URL reflects current state |
| `nav-deep-link` | Sections are linkable via hash |
| `state-no-flash` | No flash of unstyled content (FOUC) |

## How to Audit

```markdown
1. Scan the codebase for HTML/React/Vue components
2. Check against each rule category above
3. Report findings grouped by severity
4. Provide specific code fixes for each issue
```

## Example Audit Output

```markdown
## 🔴 Critical Issues Found: 3

### a11y-aria-labels
**File:** `Button.tsx:12`
```tsx
// ❌ Missing
<button onClick={handleClick}>Click</button>

// ✅ Fixed
<button onClick={handleClick} aria-label="Submit form">Submit</button>
```

## 🟡 Medium Issues Found: 5
...
```

## Reference Files

For detailed rule implementations, see:
- `rules/a11y-aria-labels.md`
- `rules/motion-reduced.md`
- `rules/focus-visible.md`

---

*Part of SWAL Skills — swal/iberi22*
