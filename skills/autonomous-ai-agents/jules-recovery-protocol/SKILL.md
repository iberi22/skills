---
name: jules-recovery-protocol
description: "Protocolo de recuperación para Jules cuando falla una sesión. Incluye prompt optimizado en 3 fases: Diagnóstico → Investigación Enfocada → Implementación+PR. Versión validada con Ola 8 Xavier."
version: 1.0.0
author: Hermes Agent + BELA
tags: [jules, recovery, failed-task, prompt-engineering]
---

# Jules Recovery Protocol — Prompt Optimizado

> Cuando Jules falla, el prompt de recovery es crítico. Un mal prompt = Jules vuelve a fallar.
> Este skill contiene el prompt probado y las reglas para aplicarlo.

## 🚨 Diagnóstico Rápido

Antes de recovery, clasificar la falla:

| Síntoma | Causa | Acción |
|---------|-------|--------|
| "unexpected error" | Task creada pero falló en ejecución | Comentar recovery prompt en el issue |
| "failed to create a task" | Rate limit / server error | Remover label jules → re-aplicar |
| "Completed" sin cambios | No pudo pushear o task era research | Verificar git diff, relanzar |
| PR con errores de CI | Tests fallaron | Fix manual o relanzar con más contexto |

## Prompt de Recovery (PROBADO)

**CUÁNDO USARLO:** Cuando Jules comenta "I apologize, but I encountered an unexpected error"
**CÓMO USARLO:** Comentar en el issue como respuesta al mensaje de error de Jules.

### Prompt Mejorado v2

```
## 🔄 Recovery — Research + Implementation Protocol

### Phase 1: Diagnosis (2 min)
1. Read the ENTIRE issue body — every section matters
2. Identify the EXACT failure: compile error? test failure? missing file? wrong path?
3. Read the last error message from your previous attempt (if available)

### Phase 2: Focused Web Research (5 min)
Only research what's BLOCKING you:
- `search: "[exact error message or library name] 2026 rust"`
- `search: "[alternative approach for the specific blocking issue]"`
- `search: "[crate documentation or reference implementation]"`

Do NOT research concepts already working. Only the blocker.

### Phase 3: Implementation & Validation
1. Write MINIMAL code solving the issue — follow "Files to Modify" section
2. For EACH Acceptance Criteria in the issue body, verify:
   - `grep -c "[expected pattern]" [file]` matches
   - `cargo check --workspace` → 0 errors
   - `cargo test -p xavier --lib [module]` → 0 failures
3. If stuck after 3 attempts: post the EXACT failing command + output

### Hard Rules
- ONLY modify files listed in "Files to Modify" or "DO NOT touch" allows
- NO Cargo.toml changes unless the issue body explicitly requires it
- NO new files unless "NEW" is specified in the issue
- If you can't make it compile, submit a draft PR anyway with the closest working version

### Recovery Output
After successful implementation:
1. Branch: `fix/recovery-{issue-number}-{short-description}`
2. Commit: `feat: {feature description} (#{issue})`
3. Push + Create PR
4. Comment on issue: "Fixed in PR #{number}"
```

## Comparativa: Prompt Antiguo vs Prompt Mejorado

| Aspecto | Prompt Antiguo | Prompt Mejorado v2 |
|---------|---------------|-------------------|
| Estructura | 1 oración larga | 3 fases claras + hard rules |
| Diagnóstico | ❌ No pide identificar la falla | ✅ Fase 1: Diagnosis |
| Investigación | "investigación en la web" (vaga) | ✅ Queries específicas para el bloqueo |
| Referencia al issue | ❌ No menciona el body | ✅ "Read the ENTIRE issue body" |
| Acceptance Criteria | ❌ No las menciona | ✅ Verificar contra cada AC |
| Output esperado | ❌ No especifica formato | ✅ Branch → Commit → PR |
| Fallback | ❌ Ninguno | ✅ "Post exact failing command" |
| Límites | ❌ No protege archivos | ✅ Hard Rules con "DO NOT touch" |
| Typo | "verificacio" | ✅ Corregido |

## Reglas de Aplicación

1. **Siempre leer el último comentario de Jules** antes de aplicar recovery
2. **Si Jules ya empezó a implementar algo parcial**, preservar su progreso
3. **Para issues con PR parcial**, comentar en el PR, no en el issue
4. **Para issues sin task creada** (#992, #993): remover label jules → esperar 5s → re-aplicar
5. **Si recovery falla 2 veces seguidas**, el issue necesita revisión humana del body

## Post-Recovery Checklist

- [ ] Jules reconoció el recovery ("on it" comment)
- [ ] Task ID creada (no "failed to create task")
- [ ] PR creado en < 10 min
- [ ] PR pasa CI (cargo check + test)
- [ ] Acceptance Criteria cumplidos
- [ ] features.json actualizado
