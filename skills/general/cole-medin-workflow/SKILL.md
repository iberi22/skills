---
name: cole-medin-workflow
description: >
  Implementa los 5 pilares de Cole Medin para desarrollo agente 10x.
  Trigger: Cuando necesitas lanzar agentes en paralelo, implementar worktrees,
  hacer review independiente, o establecer auto-curación en proyectos SWAL.
license: MIT
metadata:
  author: SWAL
  version: "1.0"
  updated: "2026-04-23"
---

# Cole Medin Workflow — 5 Pillars for 10x Agentic Development

## When to Use

- Iniciar desarrollo paralelo con múltiples agentes
- Configurar Git Worktrees para aislamiento de agentes
- Implementar model routing (Haiku/Sonnet)
- Hacer code review sin confirmation bias
- Establecer capa de auto-curación post-bug
- Reducir el rol humano a "simple review"

## The 5 Pillars

### 1. 🎫 Ticket como Especificación

**Regla:** Todo trabajo comienza con GitHub Issue. El issue es la única entrada para el agente.

```
NO hacer esto:
  "haz algo con el auth"

SÍ hacer esto:
  gh issue create --title "feat: implementar refresh token" --body "..."
```

**En SWAL:**
- Issues en `.github/issues/` deben tener labels `jules` para activación automática
- Cada issue = una task atómica
- No aceptar trabajo sin issue reference

### 2. 🌳 Git Worktrees (Aislamiento)

**Regla:** Un task → un branch → un worktree → un agente.

```bash
# Crear worktree para agent isolation
git worktree add -b feature/{issue-id}-{slug} ../repo-{branch}

# Ejemplo:
git worktree add -b fix/token-refresh ../gestalt-fix-token-refresh

# List active worktrees
git worktree list

# Cleanup después de merge
git worktree remove ../gestalt-fix-token-refresh
git branch -d fix/token-refresh
```

**Por qué:** Previene silent overwrites entre agentes.

### 3. 📋 Planificación y Ejecución Estructurada

**Regla:** Ciclo: Planificar → Construir → Validar → Repetir.

```
AGENTE:
1. Leer issue completo
2. Dividir en sub-tareas (max 3 por sesión)
3. Implementar una sub-tarea
4. Validar (build + tests)
5. Commit atómico
6. Repetir hasta completar issue
```

**En SWAL (gestalt-rust):**
- Usar `@architect` para planificación inicial
- Usar `@feature` para implementación
- Validar antes de commit con `cargo check`

### 4. 👀 Revisión Independiente (Confirmation Bias Prevention)

**Regla:** Review en sesión fresca, sin contexto del autor.

```bash
# Sesión NUEVA para review
# NO usar la misma sesión que escribió el código

/review PR #XXX
```

**Criterios de review:**
- ¿El código resuelve el issue?
- ¿Hay tests?
- ¿Sigue conventions?
- ¿Security issues?

**NO hacer:**
- Aprobar solo porque "el agent dijo que funciona"
- Aceptar sin testing

### 5. 🔧 Auto-Curación (Prevenir errores futuros)

**Regla:** Después de bug fix, actualizar rules/skills para prevenir recurrencia.

```
POST-BUG-FIX WORKFLOW:
1. Analizar causa raíz
2. Crear nueva regla en AGENTS.md o .claude/
3. Si es pattern recurrente → actualizar skill
4. Documentar en SWAL knowledge base
```

**Ejemplo:**
```
Si un agent忘记了 validar null:
→ Agregar a AGENTS.md: "NUNCA hacer dereference sin null check"
→ Crear unit test específico para ese case
```

---

## 🔧 Técnicas Avanzadas Complementarias

### DB Branching (Aislamiento de datos)

```bash
# Neon PostgreSQL branching (similar a Git branching)
# Cada worktree tiene su propia DB branch

neon branches create --name feature-auth
neon branches connect --name feature-auth
# DB URL única por branch
```

**Alternativa simple:** Usar SQLite con file path único por worktree.

### Port Allocation (Conflictos de puertos)

```bash
# Pool de puertos para ejecuciones locales simultáneas
AGENT_1_PORT=3001
AGENT_2_PORT=3002
AGENT_3_PORT=3003

# Script port-allocator.ps1
$pool = @(3001..3010)
$used = Get-Content ports-in-use.json -ErrorAction SilentlyContinue | ConvertFrom-Json
$available = $pool | Where-Object { $_ -notin $used }
$next = $available | Select-Object -First 1
$next  # Devuelve puerto disponible
```

### Model Routing (ver skill `llm-routing` — tabla canónica)

| Tarea | Model | Por qué |
|-------|-------|---------|
| Fast planning | `opencode-go/deepseek-v4.1-flash` | Runtime por defecto, ~2s |
| Indexing, tareas simples | `opencode-go/deepseek-v4-flash` | Fallback #1 |
| Coding pesado | Subagente OpenClaw (`deepseek-v4.1-flash`) | Paralelo controlado (máx 4) |
| Offline / privacidad | `ollama` (`phi4-mini`, `qwen2.5:7b`) | Local, sin red |


---

## 🚀 Quick Start para gestalt-rust

```bash
# 1. Crear worktree para nuevo feature
git worktree add -b feat/nuevo-feature ../gestalt-nuevo-feature

# 2. Entrar al worktree
cd ../gestalt-nuevo-feature

# 3. Crear issue en GitHub con label jules
gh issue create --title "feat: nuevo feature" --body "..."

# 4. Delegar la implementación
#    ⛔ codex exec fue RETIRADO (2026-07-01). Opciones vigentes:
#    a) Jules vía API (asíncrono, 30 concurrentes) — skill `jules`
#    b) Subagente OpenClaw:
#       sessions_spawn(runtime="subagent", mode="run", collect=true,
#                      lightContext=true, model="opencode-go/deepseek-v4-flash",
#                      task="Implementar feature desde issue #XXX")

# 5. Crear PR para review
gh pr create --title "feat: nuevo feature"

# 6. Review en sesión fresca
# (Abrir nueva sesión, no la misma)

# 7. Post-merge: auto-curación
# Analizar si hay que actualizar rules
```

---

## 📋 Scripts SWAL para Cole Medin

| Script | Ubicación | Uso |
|--------|-----------|-----|
| `worktree-manager.ps1` | `gestalt-rust/scripts/` | Crear/cleanup worktrees |
| `port-allocator.ps1` | `gestalt-rust/scripts/` | Asignar puertos únicos |

---

## 🔗 Projects SWAL con Cole Medin

| Proyecto | Readiness | Notas |
|----------|-----------|-------|
| **gestalt-rust** | ✅ Listo | Tiene gestalt_swarm, VFS, agentes activos |

**Empezar por gestalt-rust** — tiene la infraestructura Swarm funcionando.

---

## 📚 Referencias

- [Cole Medin YouTube](https://www.youtube.com/@ColeMedin)
- [Multi-Agent AI Coding Workflow: Git Worktrees That Scale](https://blog.appxlab.io/2026/03/31/multi-agent-ai-coding-workflow-git-worktrees/)
- [Agentic Coding 6 Principles](https://agentic-coding.github.io/)
- [Armin Ronacher - Agentic Coding Recommendations](https://lucumr.pocoo.org/2025/6/12/agentic-coding/)
- [Claude Haiku 4.5](https://www.anthropic.com/news/claude-haiku-4-5)
- [autoresearch (Karpathy)](https://github.com/karpathy/autoresearch)
- [LoCoMo Benchmark](https://arxiv.org/html/2402.17753v1)

---

*Creado: 2026-04-23 | SWAL Agentic Development Framework*