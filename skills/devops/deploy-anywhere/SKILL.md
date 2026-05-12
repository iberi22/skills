---
id: deploy-anywhere
name: deploy-anywhere
category: devops
tags:
  - deploy
  - cloudflare
  - vercel
  - netlify
  - railway
  - render
  - flyio
goals:
  - "Deploy applications to any hosting platform — Cloudflare Pages, Vercel, Railway, Render, Fly.io, Netlify, and more."
  - "Use when: 'Deploy my app', 'Deploy to production', 'Push this live', 'Host this website'."
context: |
  Supports all major hosting platforms with zero-configuration defaults.
  Auto-detects frameworks and builds accordingly.
authors:
  - Brahyan Belalcazar
---

# Deploy Anywhere

Universal deployment skill for static sites and full-stack applications. Supports all major hosting platforms with zero-configuration defaults.

## When to Use

Trigger on these requests:
- "Deploy my app"
- "Deploy to production"
- "Push this live"
- "Host this website"
- "Deploy to [platform]"
- "CI/CD setup"

## Supported Platforms

| Platform | Best For | Auto-Detects | Output |
|----------|----------|--------------|--------|
| **Cloudflare Pages** | Static + SSR, free tier | ✅ Next.js, Astro, Vite, React | `pages.dev` |
| **Vercel** | Next.js, frontend | ✅ 40+ frameworks | `.vercel.app` |
| **Netlify** | Static, forms | ✅ Most static | `.netlify.app` |
| **Railway** | Full-stack, Node.js | ✅ Node projects | `.railway.app` |
| **Render** | Full-stack, databases | ✅ | `.onrender.com` |
| **Fly.io** | Docker, global edge | ✅ Dockerfiles | `.fly.dev` |
| **GitHub Pages** | Free static hosting | ✅ Jekyll, plain HTML | `*.github.io` |

## Quick Deploy Commands

### Cloudflare Pages (Recommended — Free)

```bash
# Static sites
npx wrangler pages deploy dist

# With GitHub integration
# Connect repo at: https://pages.cloudflare.com/
```

### Vercel

```bash
npx vercel --prod
# Or: npx vercel deploy --prod
```

### Netlify

```bash
npx netlify deploy --prod --dir dist
```

### Railway

```bash
railway up
```

### Render

```bash
render deploy
```

## Framework Auto-Detection

The skill auto-detects these frameworks:

| Framework | Build Command | Output Dir |
|-----------|--------------|-----------|
| Next.js | `npm run build` | `.next` |
| Astro | `npm run build` | `dist` |
| Vite | `npm run build` | `dist` |
| React | `npm run build` | `build` |
| Vue | `npm run build` | `dist` |
| Nuxt | `npm run build` | `.output` |
| SvelteKit | `npm run build` | `build` |
| Plain HTML | None needed | `/` |

## Environment Variables

Always check for required env vars before deploying:

```bash
# Common required variables
DATABASE_URL=
API_KEY=
NEXTAUTH_SECRET=
```

## Build Settings Reference

### Cloudflare Pages

| Setting | Value |
|---------|-------|
| Build command | `npm run build` |
| Build output | `dist` (or `.next`, `build`) |
| Node version | `20` |

### Vercel

Vercel auto-detects everything. No config needed.

### Netlify

| Setting | Value |
|---------|-------|
| Build command | `npm run build` |
| Publish directory | `dist` |

## Post-Deploy Checklist

- [ ] Site loads without errors
- [ ] Environment variables set in dashboard
- [ ] Custom domain configured (if needed)
- [ ] SSL certificate active
- [ ] Build logs show no errors

## Example: Full Deploy Flow

```bash
# 1. Build the project
npm run build

# 2. Deploy to Cloudflare
npx wrangler pages deploy dist

# Output:
# ✅ Deployment complete!
# URL: https://my-project.pages.dev
```

## Docker Deploy (Fly.io)

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

```bash
fly launch
fly deploy
```

---

*Part of SWAL Skills — swal/iberi22*
