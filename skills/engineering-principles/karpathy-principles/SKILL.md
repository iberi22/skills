---
name: karpathy-principles
slug: karpathy-principles
version: 1.0.0
description: 4 principios de ingeniería de Andrej Karpathy para coding agents. Úsalo cuando el agente vaya a escribir, revisar o refactorizar código para evitar sobreingeniería, cambios masivos y falta de validación.
license: MIT
original_source: https://github.com/forrestchang/andrej-karpathy-skills
category: engineering-principles
tags: [karpathy, coding-principles, best-practices, simplicity, code-quality, agent-guidelines]
goals:
  - Reducir código innecesario y sobreingeniería en cada cambio
  - Forzar al agente a pensar antes de escribir código
  - Hacer cambios quirúrgicos (no refactors masivos)
  - Validar cada cambio con criterios de éxito verificables
  - Explicitar suposiciones ocultas del agente
context:
  when: Antes de escribir, revisar o refactorizar cualquier bloque de código
  who: Coding agents (Claude, Codex, OpenCode, Copilot)
  prerequisites: Ninguno — principios universales
  avoid_when: El agente ya está en medio de una ejecución que no puede interrumpir
authors: 
  - forrestchang (repo original)
  - Brahyan Belalcazar (versión estructurada)
---

# Karpathy Principles

4 principios de ingeniería de software para coding agents, derivados de las observaciones de [Andrej Karpathy](https://x.com/karpathy/status/2015883857489522876) sobre errores comunes de LLMs al escribir código.

**Tradeoff:** Estos principios priorizan la precisión sobre la velocidad. Para tareas triviales, usar el juicio propio.

---

## 1. Think Before Coding (Piensa antes de codear)

> **No asumas. No ocultes la confusión. Expón los tradeoffs.**

### Definición
Antes de escribir una sola línea de código, el agente debe explicitar sus suposiciones, identificar ambigüedades y validar su comprensión del problema.

### Checklist pre-coding
- [ ] ¿Tengo claridad absoluta sobre lo que pide el usuario?
- [ ] ¿Existen múltiples interpretaciones posibles? Si sí, las enumeré.
- [ ] ¿Existe un enfoque más simple? Lo mencioné.
- [ ] ¿Estoy haciendo suposiciones implícitas? Las explicité.
- [ ] ¿Hay algo confuso? Pregunté antes de avanzar.

### Ejemplo: antes vs después

**❌ Antes (suposiciones ocultas):**
```
Usuario: "Agrega validación al formulario de login"
Agente: Escribe 150 líneas de validación con regex complejos,
        validación de contraseñas fuertes, 2FA, rate limiting...
        (sin preguntar qué tipo de validación se necesitaba)
```

**✅ Después (suposiciones explicitadas):**
```
Usuario: "Agrega validación al formulario de login"
Agente: "Entendido. Algunas preguntas para clarificar:
        1. ¿Validación de formato de email, contraseña vacía, ambos?
        2. ¿Mensajes de error personalizados o genéricos?
        3. ¿Validación solo en frontend o también en backend?
        Enfoque más simple: validar email con formato básico
        y contraseña no vacía. ¿Procedo con eso?"
```

---

## 2. Simplicity First (Simplicidad primero)

> **Mínimo código que resuelve el problema. Nada especulativo.**

### Definición
Escribe exactamente lo que se pide. No anticípates a necesidades futuras. Prefiere código explícito y directo sobre abstracciones prematuras.

### Reglas de oro
1. **Sin features extras.** Si no lo pidieron, no existe.
2. **Sin abstracciones para un solo uso.** Una función usada una vez debe ser código inline.
3. **Sin "flexibilidad" no solicitada.** No parametrices lo que no cambia.
4. **Sin manejo de errores imposibles.** No defensas contra escenarios teóricos.
5. **Si escribiste 200 líneas y podrían ser 50, reescríbelo.**

### Anti-patrones comunes
| Anti-patrón | Síntoma | Solución |
|-------------|---------|----------|
| **Gold plating** | Agregar funcionalidad "por si acaso" | Eliminar. Solo lo pedido. |
| **Premature abstraction** | Extraer funciones/clases con un solo uso | Inline hasta el segundo uso. |
| **Configuritis** | Variables de configuración para valores constantes | Hardcodear hasta que cambie. |
| **Defensive overkill** | Try/catch para operaciones seguras | Manejar solo errores probables. |

> **Pregunta de sanidad:** ¿Un ingeniero senior diría que esto está sobrecomplicado? Si sí, simplifica.

---

## 3. Surgical Changes (Cambios quirúrgicos)

> **Toca solo lo que debes. Limpia solo tu propio desorden.**

### Definición
Cada cambio debe ser mínimo, enfocado y directamente trazable a la solicitud del usuario. No aproveches para "mejorar" código adyacente.

### Cómo hacer cambios mínimos
1. **No "mejores" código adyacente.** No reformatees, no renombres, no extraigas.
2. **No refactorices lo que no está roto.** Si funciona y no es parte del ticket, déjalo.
3. **Respeta el estilo existente.** Aunque uses otro en tu código personal.
4. **Código muerto no relacionado:** menciónalo, no lo borres.

### Diff-driven development
- Antes de commit, revisa el diff línea por línea.
- Cada línea modificada debe justificarse con la solicitud del usuario.
- Si una línea no tiene justificación directa, reviértela.

### Regla de orfanatos
- ✅ **Sí** eliminar imports/variables/funciones que **TUS** cambios hicieron no usados.
- ❌ **No** eliminar código muerto preexistente a menos que se te pida.

> **El test:** ¿Cada línea cambiada se traza directamente a la petición del usuario? Si no, reviértela.

---

## 4. Goal-Driven Execution (Ejecución orientada a metas)

> **Define criterios de éxito. Itera hasta verificar.**

### Definición
Transforma tareas vagas en metas concretas y verificables. Antes de empezar, define cómo sabrás que terminaste.

### Transformar tareas en metas verificables
| Tarea vaga | Meta verificable |
|------------|------------------|
| "Agrega validación" | "Escribir tests para inputs inválidos, luego hacerlos pasar" |
| "Arregla el bug" | "Escribir test que lo reproduzca, luego hacerlo pasar" |
| "Refactoriza X" | "Tests pasan antes y después del refactor" |
| "Mejora el performance" | "Benchmark baseline, optimizar, benchmark mejora > 20%" |

### Plan de pasos verificables
Para tareas multi-paso, usa este formato:

```
1. [Paso] → verificar: [check concreto]
2. [Paso] → verificar: [check concreto]
3. [Paso] → verificar: [check concreto]
```

### Validar antes y después
- **Antes:** captura el estado actual (tests, logs, benchmarks).
- **Durante:** aplica cambios quirúrgicos.
- **Después:** ejecuta los mismos checks. ¿Mejoró? ¿Emporó? ¿Neutro?

> **Criterios fuertes** = puedes iterar solo. **Criterios débiles** ("que funcione") = requieren clarificación constante.

---

## Referencia rápida

| Principio | Esencia en una frase | Cuándo aplicar |
|-----------|----------------------|----------------|
| **Think Before Coding** | Explicita suposiciones antes de codear | Antes de escribir cualquier archivo nuevo |
| **Simplicity First** | Mínimo código, máximo valor | Durante la implementación |
| **Surgical Changes** | Toca solo lo necesario | Al editar código existente |
| **Goal-Driven Execution** | Define cómo sabrás que ganaste | Antes de empezar cualquier tarea |

---

## Checklist pre-commit

- [ ] **Think:** ¿Explicité mis suposiciones? ¿Pregunté lo que no entendí?
- [ ] **Simplicity:** ¿Este código es el mínimo necesario? ¿No hay features extras?
- [ ] **Surgical:** ¿Cada línea del diff se justifica con la petición del usuario?
- [ ] **Goal:** ¿Definí criterios de éxito verificables? ¿Los validé?
- [ ] **Sanity check:** ¿Un ingeniero senior aprobaría este PR?

---

**Estos principios funcionan si:** los diffs tienen menos cambios innecesarios, hay menos reescrituras por sobrecomplicación, y las preguntas de clarificación vienen *antes* de la implementación, no después de los errores.
