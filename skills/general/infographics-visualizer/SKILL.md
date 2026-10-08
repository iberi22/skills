---
name: infographics-visualizer
description: Create modern, production-grade interactive infographics, animated SVG diagrams, architectural flows, and data radars using pure SVG, GSAP, CSS Keyframes, and Tailwind.
version: 1.0.0
author: Antigravity / SWAL
tags: [svg, infographics, animation, gsap, dataviz, visual-engineering]
---

# Infographics Visualizer Skill

Guía canónica y patrones para construir infografías interactivas, técnicas y de alto impacto visual sin frameworks pesados, basadas en estándares web modernos (SVG vectorial, gradientes reactivos, animaciones GSAP/CSS y Bento Grids).

---

## 1. Principios de Diseño Visual para Infografías Técnicas

1. **Jerarquía Vectorial Limpia:**
   - Usar `viewBox` responsive (`viewBox="0 0 800 500"`) con `preserveAspectRatio="xMidYMid meet"`.
   - Separar capas: Background Grid / Conectores animados / Nodos interactivos / Badges y Métricas.
2. **Animaciones de Flujo de Datos (Pulse & Stream):**
   - Efecto de "energía o paquetes viajando" sobre caminos SVG usando `stroke-dasharray` y `stroke-dashoffset` con CSS keyframes.
   - Glow dinámico mediante filtros SVG (`<feDropShadow>`, `<feGaussianBlur>`).
3. **Bento Grid Arquitectónico:**
   - Presentación modular en tarjetas con micro-interacciones (`hover:border-cyan-500/50`, `backdrop-blur-md`).
4. **Accesibilidad y Nitidez:**
   - Los textos críticos se renderizan en tipografía legible (Mono/Inter) con contraste alto (`text-white`, `text-slate-300`).

---

## 2. Patrones Técnicos Canónicos

### Patrón A: Flujo de Paquetes Animados (Animated Data Flow)
```svg
<svg viewBox="0 0 600 200" class="w-full h-auto">
  <defs>
    <linearGradient id="flowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.2"/>
      <stop offset="50%" stop-color="#3b82f6" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0.2"/>
    </linearGradient>
  </defs>
  <!-- Ruta base estática -->
  <path d="M 50 100 H 550" stroke="#1e293b" stroke-width="4" fill="none" stroke-linecap="round"/>
  <!-- Paquete animado que fluye -->
  <path d="M 50 100 H 550" stroke="url(#flowGrad)" stroke-width="4" fill="none"
        stroke-dasharray="20 180" stroke-linecap="round" class="animate-flow"/>
</svg>
```

### Patrón B: Radar de Madurez / Anillos de Métrica Circular
```svg
<svg viewBox="0 0 160 160" class="w-32 h-32">
  <circle cx="80" cy="80" r="70" stroke="#1e293b" stroke-width="12" fill="none" />
  <circle cx="80" cy="80" r="70" stroke="#10b981" stroke-width="12" fill="none"
          stroke-dasharray="440" stroke-dashoffset="44" stroke-linecap="round"
          transform="rotate(-90 80 80)" class="transition-all duration-1000 ease-out" />
  <text x="80" y="85" text-anchor="middle" class="fill-white font-mono font-bold text-xl">90%</text>
</svg>
```

### Patrón C: Bento HUD con Métricas Reactivas
- Uso de contadores animados (`counter.svelte` con `requestAnimationFrame`).
- Tooltips contextuales con detalles criptográficos al hacer hover sobre los nodos.
