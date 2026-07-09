---
id: xavier2-context
name: xavier2-context
category: tools
tags:
  - xavier2
  - context-engine
  - memory
  - cortex
  - orchestration
goals:
  - "Xavier2 as the central context engine for SWAL - intelligent memory, decision-making, and context orchestration."
  - "Xavier2 is the CEO brain that stores memories, coordinates agents, and maintains project state."
context: |
  Xavier2 es el cerebro central de SWAL. No es solo memoria — es el CEO que conecta contexto, decisiones y agentes.
authors:
  - Brahyan Belalcazar
---

# Xavier2 - SWAL Context Engine 🧠

**Xavier2 es el cerebro central de SWAL.** No es solo memoria — es el CEO que conecta contexto, decisiones y agentes.

## Arquitectura

```
┌────────────────────────────────────────────────────────────────────┐
│                    XAVIER2 (CEO Brain)                   │
│              http://localhost:8006                      │
│                    🧠 Cortex                            │
├────────────────────────────────────────────────────────────────────┤
│  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  │
│  │ memoria │  │ recall  │  │ decisions│  │ agents  │  │
│  │ (VEC)   │  │ (query) │  │ (facts)  │  │ coord.  │  │
│  └───────┘  └───────┘  └───────┘  └───────┘  │
├────────────────────────────────────────────────────────────────────┤
│                    SKILLS LAYER                         │
│  ┌───────────────────────────────────────────────────┐   │
│  │  coding-agent | jules | gestalt-swarm | etc.   │   │
│  └───────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

## Conexión Directa

```powershell
# Helper script
C:\Users\belal\clawd\agents\xavier2\scripts\xavier2-helper.ps1

# CLI directo
node C:\Users\belal\clawd\agents\xavier2\scripts\xavier2-cli.js search "query"
node C:\Users\belal\clawd\agents\xavier2\scripts\xavier2-cli.js query "synthesize"
node C:\Users\belal\clawd\agents\xavier2\scripts\xavier2-cli.js add "memory content"

# API
POST http://localhost:8006/memory/search  # Vector search
POST http://localhost:8006/memory/add      # Add memory
GET  http://localhost:8006/memory/stats    # Stats
```

## Reglas de Contexto

### 1. ANTES de cualquier decisión → Consultar Xavier2
Antes de responder preguntas sobre el proyecto, hacer decisiones de arquitectura, o resumir estado:
```
→ Buscar en Xavier2: "¿qué sabemos sobre X?"
→ Si no hay resultado, agregar después de resolver
```

### 2. Después de cada milestone → Guardar en Xavier2
Cuando complete una tarea, resuelva un bug, o tome una decisión:
```
→ "Proyecto X: decisión Y tomada porque Z"
→ "Bug #123 resuelto - causa era..."
→ "Arquitectura cambiada a..."
```

### 3. Coordinar agentes → Xavier2 como fuente de verdad
Para spawnear subagentes con contexto correcto:
```
1. Consultar Xavier2: "¿qué estado tiene el proyecto?"
2. Incluir contexto relevante en el prompt
3. Al completar, guardar nuevo estado en Xavier2
```

### 4. Decisiones de CEO (Xavier2 puede tomar solo)
- Actualizar MEMORY.md con nuevas decisiones
- Actualizar roadmap
- Identificar deuda técnica
- Proponer refactors
- Coordinar con subagentes

### 5. Decisiones que requieren BELA
- Inversiones o cambios de arquitectura mayores
- Nuevos productos o servicios
- Partnerships estratégicos
- Cambios en prioridades del roadmap

## Integración con Skills

### coding-agent
Antes de lanzar un coding agent:
```
1. Consultar Xavier2: estado del repo, issues activos
2. Incluir contexto en prompt del agent
3. Agent reporta resultados
4. Xavier2 guarda outcome
```

### jules
```
1. Xavier2 coordina qué issues asignar a Jules
2. Jules reporta completions
3. Xavier2 actualiza estado
```

### gestalt-swarm
```
1. Xavier2 define tasks para swarm
2. Swarm ejecuta en paralelo
3. Xavier2 consolida resultados
```

## Métricas Xavier2

| Métrica | Valor |
|---------|-------|
| Total Memories | ~99 |
| Last Health | ✅ OK |
| Vector Search | ~7ms |
| LLM Synthesis | ~380ms |

## Archivos de Workspace

- **MEMORY.md**: Estado global del proyecto
- **SOUL.md**: Identidad y directivas de Xavier2
- **AGENTS.md**: Directorio de agentes SWAL
- **memory/YYYY-MM-DD.md**: Logs diarios de sesión

## Comandos de Health Check

```powershell
# Health del sistema
node C:\Users\belal\clawd\agents\xavier2\scripts\xavier2-cli.js health

# Docker containers
swal-node.sh docker

# Build test
cd E:\scripts-python\xavier2; cargo build --lib
```

---

_Xavier2 🧠 — Construyendo el futuro con memoria._
