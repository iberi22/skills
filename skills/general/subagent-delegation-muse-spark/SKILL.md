---
name: subagent-delegation-muse-spark
description: "Use when delegating work to subagents/delegations in OpenClaw to save the main API. Routes delegation to muse-spark-1.3-contributor with closed context, anti-exploration bias, and acceptance criteria the parent verifies. Trigger: 'delegar', 'subagente', 'ahorrar api', 'sessions_spawn', 'delegation'."
version: 1.0.0
author: Claw
tags: [subagents, delegation, muse-spark, opencode, cost-saving, swal]
---

# Delegación a subagentes con muse-spark — ahorro de API

> **Mandato del owner:** delegar a subagentes que corran **muse-spark-1.3-contributor** para que
> el modelo principal (deepseek) no consuma la API. Contexto CERRADO: el subagente no explora,
> se le da todo resuelto y verifica criterios de aceptación antes de entregar.

## 1. Configuración vigente (aplicada 2026-09-15)

```json
// ~/.openclaw/openclaw.json → agents.defaults.subagents
{ "model": "opencode-go/muse-spark-1.3-contributor", "maxConcurrent": 6 }
```

El agente **principal** sigue en `opencode-go/deepseek-v4.1-flash`. Solo las delegaciones
usan muse-spark. Así el consumo de API del principal se minimiza.

### Reglas de oro

| Regla | Detalle |
|---|---|
| **Siempre forzar el modelo** | En cada `sessions_spawn` pasar `model: "opencode-go/muse-spark-1.3-contributor"` — no depender del default (un default roto causó fallos en 59ms) |
| **Máx 4 en paralelo** | Techo seguro SWAL (config permite 6) |
| **Contexto cerrado** | Ver §3 — sin esto el delegado explora, gasta contexto y puede dañar archivos |
| **Un entregable en disco** | Nunca "devuélveme el análisis" sin artefacto verificable |
| **El padre verifica** | La checklist de aceptación la valida el PADRE, no se confía en el reporte del hijo |

## 2. Árbol de decisión: ¿subagente o Jules?

| Tarea | Usar |
|---|---|
| Análisis, auditoría, redacción de docs, cálculo | **Subagente muse-spark** |
| Código pesado, PRs, tests en repo | **Jules** (30 slots asíncronos, no consume API) |
| Lecturas paralelas / batch de archivos | **Subagente muse-spark** |
| Builds largos, refactors multi-archivo | **Jules** |

Histórico que justifica la regla: 3 de 4 subagentes fallaron por timeout de LLM en análisis pesado;
Jules completó 3/3 PRs de código. Para **código → Jules; para pensamiento → muse-spark**.

## 3. Payload de contexto cerrado — plantilla obligatoria

Todo `sessions_spawn` debe incluir estas 8 secciones. **Si el delegado tiene que buscar para
entender la tarea, el contexto está mal armado.**

```
## ROL
Eres <rol concreto> trabajando en <proyecto>.

## RUTA EXACTA
Repositorio: <path absoluto>  ·  Rama: <branch>
Archivos clave: <lista de paths exactos>

## ESTADO ACTUAL (verificado <fecha>)
<hechos con fuente, no suposiciones>

## OBJETIVO
<una sola frase verificable>

## CONTEXTO YA RESUELTO (no buscar)
<todo masticado: estructura, nombres, decisiones previas>
<prohibido literal: "NO explores directorios fuera de los paths listados">

## RESTRICCIONES
<qué NO tocar, convenciones, límites>

## CRITERIOS DE ACEPTACION (verificar ANTES de entregar)
<checklist binaria auto-verificable>

## FORMATO DE SALIDA
<archivo exacto a escribir + estructura esperada>
```

### 3.1 Sesgo anti-exploración (las 4 reglas duras)

Caso real que lo motivó: un delegado **borró 4 módulos de `backend/src/business/mod.rs`** porque un
warning de `cargo` le sugirió "dead code", en una tarea que solo pedía **crear un test**.

| Regla | Redacción literal en el prompt |
|---|---|
| No explorar | *"NO explores directorios fuera de los paths listados. El contexto ya está resuelto arriba."* |
| No "limpiar" | *"Si detectas warnings ajenos a tu tarea, IGNÓRALOS. No son tu responsabilidad."* |
| Un solo archivo | *"El único archivo que puedes crear/modificar es `<path>`. Cualquier otro cambio invalida la entrega."* |
| Verificar antes | *"Antes de entregar, corre `<comando>` y confirma el criterio de aceptación."* |

### 3.2 Criterios de aceptación (obligatorios)

Ejemplos de checklist binaria verificable:

- *"`git diff --name-only` debe mostrar EXACTAMENTE 1 archivo: `<path>`."*
- *"El comando `<X>` debe salir con exit 0."*
- *"Si aparece cualquier archivo bajo `<dir prohibido>` en el diff, la entrega es INVÁLIDA."*
- *"El archivo de salida debe contener las secciones A, B y C."*

## 4. Invocación (spawn)

```python
sessions_spawn(
  task="<payload de §3 completo>",
  taskName="<slug>",
  label="<titulo corto>",
  model="opencode-go/muse-spark-1.3-contributor",   # SIEMPRE explícito
  context="isolated",                                # limpio por defecto
  mode="run",
  visible=False,
)
```

- `context:"isolated"` → contexto limpio (default).
- `context:"fork"` → copia el transcript (solo si necesita el hilo).
- `visible:true` → trabajo que el usuario sigue o pide conservar.

## 5. Verificación del padre (NO delegable)

Tras la entrega del subagente, el padre **comprueba la checklist**:

```bash
# 1) ¿El entregable existe y tiene contenido?
ls -la <path_esperado>
# 2) ¿El diff toca SOLO lo permitido?
git diff --name-only
# 3) ¿El comando de aceptación pasa?
<comando exacto de verificación>
```

Si el hijo reporta "listo" pero la checklist falla → **no está listo**. Corregir o relanzar.

## 6. Pitfalls verificados

| Síntoma | Causa | Fix |
|---|---|---|
| Subagente falla en 59-94 ms | default apunta a provider sin key (`qwencloud`) | forzar `model:` explícito; verificar `openclaw models auth list` |
| Subagente falla por timeout | tarea muy pesada para LLM síncrono | mandar código a Jules |
| Delegado "limpia" código ajeno | warning interpretado como tarea | reglas §3.1 |
| Delegado explora todo el repo | prompt sin rutas exactas ni "no buscar" | §3 completo |
| Reporta éxito sin evidencia | sin criterios de aceptación | §3.2 + verificación del padre §5 |

## Referencias

- Skill `muse-spark-opencode` — invocación del CLI, config del modelo, wiring Xavier.
- Skill `jules` — para trabajo de código pesado vía API (30 slots).
- Config: `~/.openclaw/openclaw.json` → `agents.defaults.subagents`.

---

## 7. Modelo `contributor` — reglas de recolección de datos

Los modelos con sufijo **`-contributor`** (`muse-spark-1.3-contributor`) son el tier de
**contribución/recolección**: cuota propia, pensados para trabajo masivo y repetible.
Todas las delegaciones del ecosistema SWAL (Jules, subagentes opencode CLI, subagentes
OpenClaw, y los agentes que se generen) deben apuntar ahí.

### 7.1 Regla de oro del ecosistema

| Origen de la tarea | Modelo obligatorio |
|---|---|
| `sessions_spawn` (OpenClaw) | `opencode-go/muse-spark-1.3-contributor` |
| subagentes vía `opencode run` | `opencode-go/muse-spark-1.3-contributor` |
| agentes generados por el arnés | `opencode-go/muse-spark-1.3-contributor` |
| Jules (API) | su propio agente (no consume cuota opencode) |

**El agente principal NO se usa para trabajo delegable.** Si la tarea es ejecutable por un
subagente, va a `contributor`.

### 7.2 Cuando la tarea es RECOLECCION DE DATOS

Un `contributor` en modo recolección se comporta distinto a uno en modo edición:

| Aspecto | Regla |
|---|---|
| **Salida** | Esquema ESTRICTO (tabla/JSON), nunca prosa libre |
| **Prohibido** | Inferir o rellenar huecos: si falta un dato, se marca `n/d` honesto |
| **Provenance** | Cada dato cita fuente (`archivo:linea`, URL, comando) |
| **Alcance** | Una sola fuente/entidad por ejecución; no mezclar |
| **Formato de entrega** | Un archivo en disco, parseable por el padre |
| **Verificación** | El padre contrasta ≥2 datos contra la fuente antes de aceptar |

**Anti-alucinación (crítico en recolección):**
```
Prohibido inventar valores. Si un campo no se puede leer, escribir "n/d" y la razón.
Si una ruta no existe, reportarla como AUSENTE — no como error ni como vacío.
```

### 7.3 Plantilla de recolección (payload cerrado)

```
## ROL
Eres recolector de datos. NO interpretas, NO opinas, NO diseñas.

## FUENTES EXACTAS
<lista cerrada de rutas/URLs/comandos — nada fuera de esta lista>

## ESQUEMA DE SALIDA (obligatorio)
| campo | tipo | fuente |
|---|---|---|
<columnas fijas; si un valor no existe -> "n/d" + razón>

## PROHIBIDO
- Explorar fuera de las fuentes listadas
- Modificar cualquier archivo
- Inferir valores ausentes
- Resumir u opinar

## CRITERIOS DE ACEPTACION
- Cada fila tiene fuente citada
- Valores ausentes marcados "n/d" con razón
- Salida en `<path>` exacto

## FORMATO
Escribe `<path>` con el esquema de arriba. Nada más.
```

### 7.4 Por qué `contributor` y no el modelo grande

- **Cuota separada** — no consume la cuota del agente principal
- **Costo** (~$0.0013 por llamada medida) — viable para barridos masivos
- **1M de contexto** — cabe un repo entero en una pasada
- **Limitación real:** el tier contributor suele ser más lento y con más rate-limit.
  Para volumen alto, **respetar rate limits**: lotes pequeños + backoff, nunca ráfagas.

---

## 8. MANDATO: el modelo principal es ORQUESTADOR, no ejecutor

> **Instrucción del owner (2026-09-15):** *"la idea es que el modelo principal sea el
> orquestador y siempre deleguemos"*.

### 8.1 Regla de decisión

Antes de ejecutar cualquier cosa, el principal se pregunta:

| ¿La tarea es…? | Acción |
|---|---|
| Análisis, auditoría, barrido, comparación, reporte | **DELEGAR** a `muse-spark` (contributor) |
| Recolección de datos con esquema | **DELEGAR** (modo recolección §7.2) |
| Código pesado / PR / refactor en repo | **DELEGAR** a Jules |
| Decisión de arquitectura, criterio, verificación final | **HACER** en el principal |
| Responder al humano | **HACER** en el principal |

**Antipatrón:** el principal haciendo greps, md5sums, diffs y conteos por sí mismo.
Eso **quema cuota del modelo grande** para trabajo que un contributor hace igual de bien.

### 8.2 Reparto de roles

```
PRINCIPAL (orquestador)
  ├─ arma el briefing cerrado (contexto resuelto + criterios de aceptacion)
  ├─ delega en N subagentes contributor (max 4 en paralelo)
  ├─ VERIFICA los resultados contra los criterios
  └─ sintetiza y responde al humano

SUBAGENTE contributor (ejecutor)
  ├─ recibe contexto CERRADO (no explora)
  ├─ ejecuta la tarea acotada
  └─ entrega en disco con evidencia
```

### 8.3 Lo que el principal SÍ debe hacer

- **Recolectar los datos de contexto** para armar el briefing (una pasada, no el trabajo entero).
- **Escribir el briefing cerrado** — es el producto de mayor valor del orquestador.
- **Verificar** el resultado del delegado (regla §5: el padre verifica, no confía).
- **Sintetizar** y responder.

### 8.4 Lo que el principal NO debe hacer

- Barridos largos, conteos, comparaciones masivas, clasificaciones → delegar.
- Leer 50 archivos para "entender" → delegar la lectura.
- Generar informes largos → delegar la generación.

### 8.5 Cómo armar el briefing de una tarea de análisis

1. **Una pasada rápida** de reconocimiento (para saber QUÉ existe, no para analizarlo).
2. Escribir un archivo de briefing con: rutas exactas, estado verificado, objetivo,
   prohibiciones, criterios de aceptación, formato de salida.
3. Delegar apuntando al briefing: *"LEELO PRIMERO. Contiene todo el contexto."*
4. El briefing es reusable y auditable — queda en disco.

### 8.6 Paralelización segura

Antes de lanzar N subagentes en paralelo, verificar que **no colisionen**:

- ¿Tocan los mismos archivos? → secuenciar, no paralelizar.
- ¿Escriben en el mismo directorio con nombres distintos? → paralelo OK.
- ¿Uno escribe y otro lee lo mismo? → secuenciar o dar el dato ya resuelto al lector.

**Límite duro: 4 subagentes en paralelo.**
