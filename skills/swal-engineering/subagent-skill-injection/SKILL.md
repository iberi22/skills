---
name: subagent-skill-injection
description: "Inyectar skills del catálogo iberi22/skills a subagentes Hermes (delegate_task). Catálogo de los 17 skills instalados y protocolo de inyección inline."
version: 1.0.0
author: BeRi + Belal
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagent, skills, injection, iberi22, catalog, delegate_task]
    related_skills: [subagent-driven-development, swal-wave-execution, xavier-cycle-harness]
---

# Subagent Skill Injection — Catálogo iberi22/skills en Hermes

## Cuándo usar

Al lanzar subagentes con `delegate_task` para tareas de ingeniería, testing, frontend,
backend o frameworks. Los skills del catálogo iberi22/skills ya están instalados en
`~/.hermes/skills/` — el objetivo es que el subagente los USE.

## Regla de oro (de subagent-driven-development)

> Los subagentes tienen CERO contexto de tu sesión. NO les hagas releer el archivo
> del skill — extrae las 3-5 reglas clave del skill y ponlas INLINE en el campo
> `context` del delegate_task. Alternativa válida: indicarles `skill_view(name='X')`
> si tienen el toolset `skills` habilitado.

## Catálogo instalado (17 skills, jul-2026)

### Ingeniería (engineering-workflow / engineering-principles)
| Skill | Uso | Inyectar cuando... |
|-------|-----|--------------------|
| `karpathy-principles` | Anti-sobreingeniería, cambios quirúrgicos, goal-driven | Cualquier tarea de código |
| `backend-architect` | Diseño backend escalable/seguro | Arquitectura de APIs, servicios |
| `frontend-developer` | Frontend moderno (JS frameworks, responsive) | Tareas de UI/components |
| `ai-engineer` | ML/AI práctico, integración de modelos | Features con IA/ML |
| `devops-automator` | CI/CD, infraestructura resiliente | Pipelines, deploys, infra |
| `mobile-app-builder` | iOS/Android/cross-platform | Apps móviles |

### Testing (testing/)
| Skill | Uso |
|-------|-----|
| `api-tester` | Testing de APIs (contratos, edge cases) |
| `performance-benchmarker` | Benchmarks y optimización de performance |
| `test-results-analyzer` | Análisis de resultados de tests |
| `test-writer-fixer` | Escribir tests faltantes, arreglar rotos |

### Frameworks (framework/)
| Skill | Uso |
|-------|-----|
| `nextjs` | Next.js 15 App Router, caching, auth |
| `astro` | Sitios estáticos/multilenguaje en Cloudflare Pages |
| `vite` | Config/optimización de Vite |
| `tailwindcss` | Utility classes, responsive, dark mode |

### Frontend / Prototipado
| Skill | Uso |
|-------|-----|
| `frontend-doctor` | Diagnóstico de UI rota (white screen, JS errors) |
| `prototype` | Validar hipótesis técnicas rápido |
| `rapid-prototyper` | MVPs funcionales rápido |

## Protocolo de inyección

### Opción A (recomendada): reglas inline en context

```python
delegate_task(
    goal="Implementar endpoint de login con validación",
    context="""
    TAREA: ...
    
    REGLAS DEL SKILL karpathy-principles (APLICAR):
    1. Piensa antes de codear: explicita suposiciones antes de escribir
    2. Simplicidad primero: mínimo código que resuelve el problema, sin features extras
    3. Cambios quirúrgicos: toca solo lo necesario, no refactorices código adyacente
    4. Goal-driven: define criterios de éxito verificables antes de empezar
    
    REGLAS DEL SKILL backend-architect (APLICAR):
    - [extraer 3-5 reglas clave del skill antes de dispatch]
    """,
    toolsets=['terminal', 'file']
)
```

### Opción B: subagente carga el skill con skill_view

```python
delegate_task(
    goal="Implementar X siguiendo el skill karpathy-principles",
    context="""
    PRIMERO: llama a skill_view(name='karpathy-principles') y sigue sus instrucciones.
    LUEGO: implementa la tarea...
    """,
    toolsets=['skills', 'terminal', 'file']  # 'skills' necesario para skill_view
)
```

### Opción C: extraer contenido completo del skill al context

Para skills cortos (<2KB), copiar el cuerpo completo del SKILL.md al context del
subagente garantiza adherencia total (sin depender de que el subagente haga skill_view).

## Tabla de dispatch rápida

| Tipo de tarea | Skills a inyectar |
|---------------|-------------------|
| Backend/API | backend-architect + karpathy-principles |
| Frontend/UI | frontend-developer + tailwindcss |
| Next.js app | nextjs + karpathy-principles |
| Sitio estático | astro + tailwindcss |
| Tests de API | api-tester + test-writer-fixer |
| Performance | performance-benchmarker |
| UI rota/debug | frontend-doctor |
| MVP rápido | rapid-prototyper o prototype |
| Cualquier código | karpathy-principles (siempre) |

## Fuente del catálogo

- Repo: https://github.com/iberi22/skills (público, 75 skills totales)
- Instalados vía `hermes skills install --yes <raw-url>` (formato v2 compatible)
- Los 4 duplicados no instalados: codex, jules, sqlite-pro, web-research (ya existían en Hermes)
- No instalados por política SWAL (negocio privado): synapse, swal-finetune,
  worldexams-*, xavier2-context, sales-pro

## Actualizar catálogo (nuevos skills del repo)

```bash
# 1. Inspeccionar
hermes skills inspect "https://raw.githubusercontent.com/iberi22/skills/main/skills/<cat>/<skill>/SKILL.md"

# 2. Instalar (si falla el fetch, copiar manualmente:
#    cp <repo>/skills/<cat>/<skill>/SKILL.md ~/.hermes/skills/<skill>/SKILL.md)
hermes skills install --yes "https://raw.githubusercontent.com/iberi22/skills/main/skills/<cat>/<skill>/SKILL.md"

# 3. Verificar
find ~/.hermes/skills -name SKILL.md | wc -l
```
