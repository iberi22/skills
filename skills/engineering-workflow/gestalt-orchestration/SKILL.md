---
name: gestalt-orchestration
description: "Protocolo de orquestación multi-agente: Hermes orquesta, Gestalt ejecuta, Xavier persiste, GitCore gatilla"
category: orchestration
triggers:
  - "orquestar agentes"
  - "lanzar enjambre"
  - "gestalt orchestrate"
  - "oleada de agentes"
  - "orquestación multi-agente"
---

# 🧠 Protocolo de Orquestación Multi-Agente

```
═══════════════════════════════════════════════════════════════
 HERMES (orquestador estratégico)
   ↓ decide qué, quién, cuándo
 GESTALT (backend técnico — VFS, conflictos, paralelo)
   ↓ ejecuta, aísla, versiona
   ↓ editan, analizan, implementan
 XAVIER (memoria persistente — PRE contexto, POST archivo)
═══════════════════════════════════════════════════════════════
```

## 📋 Inventario de Agentes (agent-registry.toml)

| Agente | Modelo | RPM | Rol |
|--------|--------|-----|-----|
| **opencode-low** | deepseek-v4-flash-0731 | 120 | Implementación en enjambre, editar, fix |
| **agy** | Gemini 3.6 Flash | 30 | Editar, buscar, code-review |
| **hermes** | DeepSeek V4 Flash | 200 | **Orquestar, delegar, skills, memoria** |
| **gestalt** | router-v1 | ∞ | VFS, conflictos, paralelo, Xavier sync |
| **tiny-insert-line** | phi-3-mini | ∞ | Insertar 1 línea exacta |
| **tiny-delete-line** | tinyllama-1.1b | ∞ | Eliminar 1 línea exacta |
| **tiny-replace-line** | qwen2.5-coder-0.5b | ∞ | Reemplazar 1 línea exacta |
| **tiny-search** | all-MiniLM-L6-v2 | ∞ | Búsqueda semántica |

## 🔄 Flujo de Orquestación

### Fase 1: RECIBIR tarea
```
Hermes recibe instrucción del usuario
  → Analiza con qué agente(s) ejecutar
  → Consulta AgentRegistry (select_agent)
  → Verifica rate limits (RPM/TPM disponibles)
```

### Fase 2: PRE — Consultar Xavier
```
  → Xavier search(query) → contexto relevante
  → ¿Hay sesiones previas? ¿Planes? ¿Decisiones?
  → Inyectar contexto al agente
```

### Fase 3: DELEGAR al mejor agente
```
  → Tarea simple/edición → tiny-* (phi-3-mini / qwen2.5-coder-0.5b)
  → Tarea mediana        → agy (Gemini 3.6 Flash) / opencode (DeepSeek V4)
  → Enjambre             → opencode-low (deepseek-v4-flash-0731) × N instancias
  → Orquestación         → Hermes (delegate_task) o Gestalt (swarm)
  
  delegate_task(goal, context=Xavier_ctx, agent=selected)
```

### Fase 4: EJECUTAR con Gestalt VFS
```
  Si requiere edición de archivos:
  → Gestalt crea VFS overlay aislado
  → Agente edita archivos virtualizados
  → Gestalt captura BlockEdits (diff por línea)
  → Gestalt detecta conflictos en tiempo real (G4)
  → Si paralelo: JoinSet con N agentes, cada uno en su VFS
```

### Fase 5: POST — Archivar en Xavier
```
  → Archivar resultado como kind=execution
  → Indexar cambios como kind=plan si es documento
  → Actualizar rate limits del agente usado
```

### Fase 6: ENTREGAR sin conflictos
```
  → Merge de VFS overlays
  → Aplicar diffs secuencialmente
  → Si conflicto: reportar y resolver vía agent-cli-high
  → Commit + push (gitcore hooks validan)
```

## 🎯 Estrategias de Enrutamiento

1. **CapabilityMatch** (default): El agente con más capacidades relevantes para la tarea
2. **Cheapest**: El de menor costo por millón de tokens
3. **MostCapable**: El de mayores capacidades
4. **RoundRobin**: Rotación entre disponibles

Para ediciones de 1 línea → **tiny agents** (preferencia configurable)
Para tareas cortas (<200 chars) → **tiny agents o agy**
Para implementación → **agent-cli-low (enjambre) o agy**
Para orquestación → **Hermes o Gestalt**

## 📁 Dónde Vive Cada Componente

| Componente | Ubicación | Propósito |
|-----------|-----------|-----------|
| **Skill de orquestación** | `~/.hermes/skills/gestalt-orchestration/` | Lógica de IA para decidir agente |
| **Agent Registry** | `gestalt/agent-registry.toml` | Inventario + rate limits |
| **Registry Parser** | `gestalt/gestalt_core/src/application/agent/registry.rs` | Motor Rust de selección |
| **Protocolo CLI** | `gestalt/gestalt_cli/src/main.rs` (Xavier command) | Tool `gestalt xavier` |
| **Backend Técnico** | `gestalt/gestalt-router/` | VFS, router, state, conflictos |
| **Cliente Xavier** | `gestalt/gestalt_core/src/application/agent/xavier/` | Sync PRE/POST |
| **Git Hooks** | `gestalt/.git/hooks/` + `gestalt/hooks/` | Triggers automáticos |
| **Documentación** | Indexada en Xavier como kind=plan | Conocimiento compartido |

## 🚀 Cómo Usar

### Desde Hermes (recomendado):
```
Con el skill cargado:
1. "lanzar agy para editar main.rs"
   → Hermes consulta registry, selecciona agy, ejecuta
2. "enjambre con deepseek-v4-flash-0731 para 3 issues"
   → Hermes lanza N agent-cli-low en paralelo via Gestalt
4. "ciclo completo con Xavier"
   → PRE search → EXEC agente → POST archive
```

### Desde CLI:
```bash
# Ver agentes disponibles
gestalt xavier search "agents"
# O usar el registry directamente
cat agent-registry.toml
```

### Vía Git Hooks:
```bash
# Post-commit: archivar en Xavier
.git/hooks/post-commit → gestalt xavier add "commit msg"
```

## ⚙️ Rate Limits por Proveedor

| Provider | RPM | TPM | Prioridad |
|----------|-----|-----|-----------|
| openrouter | 200 | 2M | 1 (más prioritario) |
| local (Ollama) | 9999 | 10M | 10 |
| opencode | 100 | 1M | 2 |
| hermes | 100 | 1M | 3 |

## 🔮 Próximos Pasos (Roadmap)

1. **Block Editing real** — Implementar AgentWrapper.execute() (hoy es stub)
2. **Conflict Detection (G4)** — LiveConflictDetector existe, falta integrar solucionador
3. **Tiny Agents fine-tuned** — Dataset desde BlockEdits reales → LoRA fine-tune
4. **Git Hooks integrados** — post-commit → Xavier, pre-push → Gestalt
5. **Xavier memory kinds** — kind=plan, kind=execution, kind=config

## 📚 Documentación Indexada en Xavier

| Documento | Kind | Path |
|-----------|------|------|
| Este skill | plan | hermes/skills/gestalt-orchestration |
| Agent Registry | config | gestalt/agent-registry.toml |
| GLOBAL_GOAL.md | plan | gestalt/GLOBAL_GOAL.md |
| ARCHITECTURE.md | plan | gestalt/ARCHITECTURE.md |
