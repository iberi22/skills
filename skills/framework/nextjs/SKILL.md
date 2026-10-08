---
id: nextjs
name: NextJS
category: framework
tags:
  - nextjs
goals:
  - "Build Next.js 15 apps with App Router, server components, caching, auth, and production patterns."
---

## When to Use

User needs Next.js expertise — routing, data fetching, caching, authentication, or deployment. Agent handles App Router patterns, server/client boundaries, and production optimization.

## Core Rules

### 1. Server Components by Default
Everything is Server Component in App Router. Add `'use client'` only for useState, useEffect, event handlers, or browser APIs. Server Components can't be imported into Client — pass as children.

### 2. Fetch Data on Server
Fetch in Server Components, not useEffect. Use `Promise.all` for parallel requests.

### 3. Cache Intentionally
`fetch` is not cached by default in Next.js 15 — opt in with `cache: 'force-cache'` or set `revalidate` for ISR.

### 4. Server Actions for Mutations
Use `'use server'` functions for form submissions and data mutations. Progressive enhancement — works without JS.

### 5. Environment Security
`NEXT_PUBLIC_` exposes to client bundle. Server Components access all env vars. Use `.env.local` for secrets.

### 6. Streaming for Large Data
Use `<Suspense>` boundaries to stream content progressively. Wrap slow components individually.

### 7. Auth at Middleware Level
Protect routes in middleware, not in pages. Middleware runs on Edge — lightweight auth checks only.

## Server vs Client

| Server Component | Client Component |
|------------------|------------------|
| Default in App Router | Requires `'use client'` |
| Can be async | Cannot be async |
| Access backend, env vars | Access hooks, browser APIs |
| Zero JS shipped | JS shipped to browser |

**Decision:** Start Server. Add `'use client'` only for: useState, useEffect, onClick, browser APIs.

## Common Traps

| Trap | Fix |
|------|-----|
| `router.push` in Server | Use `redirect()` |
| `<Link>` prefetches all | `prefetch={false}` |
| `next/image` no size | Add `width`/`height` or `fill` |
| Metadata in Client | Move to Server or `generateMetadata` |
| useEffect for data | Fetch in Server Component |
| Import Server→Client | Pass as children/props |
| Middleware DB call | Call API route instead |
| Missing `await params` (v15) | Params are async in Next.js 15 |

## Next.js 15 Changes

- `params` and `searchParams` are now `Promise` — must await
- `fetch` not cached by default — opt-in with `cache: 'force-cache'`
- Use React 19 hooks: `useActionState`, `useFormStatus`

## Related Skills
Related skills to install if relevant:
- `react` — React fundamentals and patterns
- `typescript` — Type safety for better DX
- `prisma` — Database ORM for Next.js apps
- `tailwindcss` — Styling with utility classes
- `nodejs` — Server runtime knowledge

