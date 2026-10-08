---
name: skill-orchestrator
description: "Pipeline de orquestación multi-agente del ecosistema SWAL. Usar ANTES de cualquier delegación o sessions_spawn. Define los roles (orquestador/ejecutores), el reparto de trabajo, los modos de ejecución y el pipeline completo. Triggers: orquestar, delegar, sessions_spawn, lanzar subagentes, pipeline, reparto de trabajo, spawn Jules."
version: "4.0.0"
updated: "2026-09-15"
author: swal
license: MIT
metadata:
  openclaw:
    autoLoad: false
    forSubagents: true
    lightContext: true
---

# Skill Orchestrator v4 — Orquestación multi-agente

> **v4 (2026-09-15):** reescrito sobre v3.0.0. Se retiraron ClaudeCode, GLM 5.2/z.ia y las
> rutas Windows (los tres obsoletos). Los ejecutores actuales son **Jules** y
> **opencode CLI con muse-spark-1.3-contributor**.

## 1. Modelo mental

**El modelo principal es ORQUESTADOR, no ejecutor.** No hace greps, conteos, diffs ni
barridos: arma el briefing, delega, verifica y sintetiza.

```
PRINCIPAL (orquestador)
  ├─ 1 pasada de reconocimiento (saber QUÉ existe, no analizarlo)
  ├─ escribe el briefing cerrado (contexto resuelto + criterios de aceptación)
  ├─ delega en N subagentes contributor (máx 4 en paralelo)
  ├─ VERIFICA los resultados contra los criterios
  └─ sintetiza y responde al humano

SUBAGENTE contributor (ejecutor)
  ├─ recibe contexto CERRADO (no explora)
  ├─ ejecuta la tarea acotada
  └─ entrega en disco con evidencia
```

## 2. Roles y ejecutores (v4)

| Rol | Quién | Responsabilidad |
|---|---|---|
| **Orquestador** | Claw (modelo principal) | briefings, priorizar, lanzar, verificar, sintetizar |
| **Ejecutor — código pesado** | **Jules** (API, 2 cuentas) | features, fixes, refactors, PRs, E2E |
| **Ejecutor — análisis/recolección** | **opencode CLI + `muse-spark-1.3-contributor`** | auditorías, barridos, informes |
| **Ejecutor — subagente OpenClaw** | `sessions_spawn` con muse-spark | tareas acotadas con contexto cerrado |
| **Gobernanza del backlog** | **Atlas** (`atlas` CLI) | DAG de tareas, priorización, dispatch |
| **Observabilidad** | **Gestalt bus :8081** + opencode DB | ver qué hacen los otros agentes |

### Por qué muse-spark para delegar

Tier **contributor** = cuota separada + costo bajo (~$0.0013/llamada) + 1M contexto.
Así **no se consume la cuota de la suscripción** del modelo principal.

## 3. Reparto de decisión

| ¿La tarea es…? | Va a |
|---|---|
| Análisis, auditoría, barrido, comparación, informe | **muse-spark** (contributor) |
| Recolección de datos con esquema | **muse-spark** (modo recolección) |
| Código pesado / PR / refactor en repo | **Jules** |
| Decisión de arquitectura, criterio, verificación final | **principal** |
| Responder al humano | **principal** |

## 4. Modos de ejecución

### 4a. Subagente OpenClaw (preferido para delegación acotada)
```
sessions_spawn({
  task: "<payload cerrado de 8 secciones>",
  model: "opencode-go/muse-spark-1.3-contributor",
  mode: "run",
  context: "isolated"
})
```

### 4b. opencode CLI (para lotes / trabajo en paralelo fuera del gateway)
```bash
opencode run --model opencode-go/muse-spark-1.3-contributor \
  --dir /tmp "<prompt>" 2>&1 | tail -6
```

### 4c. Jules (código pesado asíncrono)
Vía API con 2 llaves = 30 tareas concurrentes. Crear issue + label `jules`.

## 5. Payload cerrado (8 secciones) — obligatorio

```
## ROL            → quién es (y qué NO es)
## RUTA EXACTA    → archivos concretos, nada más
## ESTADO ACTUAL  → hechos verificados por el orquestador
## CONTEXTO YA RESUELTO (no buscar) → lo que NO debe re-investigar
## OBJETIVO       → resultado esperado en 1 frase
## RESTRICCIONES  → prohibiciones explícitas
## CRITERIOS DE ACEPTACIÓN → binarios, verificables
## FORMATO DE SALIDA → esquema exacto
```

**Anti-exploración (las 4 reglas):**
1. Listar las rutas exactas (`Archivo: /ruta/exacta`) y decir *"ningún otro archivo es relevante"*.
2. Declarar el contexto ya resuelto y ordenar *"no buscar"*.
3. Prohibir explícitamente salirse del esquema.
4. **Regla anti-deriva:** *"si detectas un problema ajeno a tu tarea, IGNÓRALO y no lo menciones."*

⚠️ **Justificación real:** un delegado borró 4 módulos porque un warning le sugirió "dead code".
Sin la regla 4, el delegado "mejora" cosas fuera de alcance.

## 6. Verificación (el padre NO confía en el reporte)

**El orquestador verifica contra los criterios de aceptación**, no contra el resumen del hijo:
- Leer el **artefacto en disco** (no el mensaje de vuelta).
- Re-ejecutar el comando de verificación si es determinista.
- Contrastar ≥2 datos contra la fuente original.

## 7. Paralelización segura

Antes de lanzar N subagentes:

| Chequeo | Acción |
|---|---|
| ¿Tocan los mismos archivos? | **secuenciar**, no paralelizar |
| ¿Escriben en el mismo dir con nombres distintos? | paralelo OK |
| ¿Uno escribe y otro lee lo mismo? | secuenciar, o dar el dato ya resuelto |

**Límite duro: 4 subagentes en paralelo.**
**Límite Jules: máx 8 sesiones simultáneas por cuenta** (regla del owner).

### Lección real (2026-09-15)
Dos delegados en paralelo sobre los mismos skills → el que movía directorios dejó
**6 symlinks huérfanos** que el otro había creado. Misma zona de archivos = secuenciar.

## 8. Pipeline completo

```
1. RECONOCER   1 pasada: qué existe (rutas, estado, git) — poco profundo
2. BRIEFING    escribir el payload cerrado en un .md reusable y auditable
3. DELEGAR     N subagentes (máx 4) o Jules, según el tipo de tarea
4. VERIFICAR   leer artefactos en disco + contrastar contra criterios
5. SINTETIZAR  reportar al humano: hecho / verificado / pendiente
```

## 9. Anti-patrones

| ❌ No hacer | ✅ Hacer |
|---|---|
| Principal haciendo barridos largos | delegar a muse-spark |
| Leer 50 archivos "para entender" | delegar la lectura |
| Confiar en el resumen del hijo | verificar el artefacto |
| Paralelizar sobre los mismos archivos | secuenciar |
| Delegar sin criterios binarios | criterios verificables siempre |
| Contexto abierto ("investiga X") | rutas exactas + "no busques" |
