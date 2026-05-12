---
name: tdd
slug: tdd
version: 1.0.0
description: "Test-Driven Development workflow para coding agents: red-green-refactor cycle con tracer bullets verticales en vez de slices horizontales. Actívalo cuando el usuario pida TDD, tests primero, o red-green-refactor."
license: MIT
original_source: https://github.com/mattpocock/skills
category: engineering-workflow
tags: [tdd, testing, red-green-refactor, tracer-bullet, workflow, quality]
goals:
  - Escribir tests ANTES del código de producción (red)
  - Implementar mínimo código para pasar tests (green)
  - Refactorizar manteniendo tests verdes (refactor)
  - Construir vertical slices en vez de horizontales
  - Reducir acoplamiento entre tests e implementación
context:
  when: El usuario pide TDD, tests, red-green-refactor, o test-first
  who: Coding agents con capacidad de escribir y ejecutar tests
  prerequisites: Framework de testing disponible en el proyecto
  avoid_when: Prototipado rápido donde los requisitos cambian cada minuto
authors:
  - mattpocock (repo original)
  - Brahyan Belalcazar (versión estructurada)
---

# Test-Driven Development (TDD)

## 1. Filosofía TDD

**Principio core**: Los tests deben verificar comportamiento a través de interfaces públicas, no detalles de implementación. El código puede cambiar por completo; los tests no deberían.

**Buenos tests** son de estilo integración: ejercitan rutas reales de código a través de APIs públicas. Describen *qué* hace el sistema, no *cómo* lo hace. Un buen test se lee como una especificación: "el usuario puede hacer checkout con un carrito válido" te dice exactamente qué capacidad existe. Estos tests sobreviven a refactors porque no les importa la estructura interna.

**Malos tests** están acoplados a la implementación. Hacen mocks de colaboradores internos, testean métodos privados, o verifican a través de medios externos (como consultar directamente la base de datos en vez de usar la interfaz). La señal de alerta: tu test se rompe cuando haces refactor, pero el comportamiento no ha cambiado. Si renombras una función interna y los tests fallan, esos tests estaban testeando implementación, no comportamiento.

> Ver [tests.md](tests.md) para ejemplos y [mocking.md](mocking.md) para guías de mocking.

## 2. Anti-Patrón: Horizontal Slices

**NO escribas todos los tests primero y luego toda la implementación.** Esto es "horizontal slicing" — tratar RED como "escribir todos los tests" y GREEN como "escribir todo el código."

Esto produce **tests de baja calidad**:

- Tests escritos en masa testean comportamiento _imaginado_, no _real_
- Terminas testeando la _forma_ de las cosas (estructuras de datos, firmas de funciones) en lugar de comportamiento visible para el usuario
- Los tests se vuelven insensibles a cambios reales: pasan cuando el comportamiento se rompe, fallan cuando el comportamiento está bien
- Te adelantas a tus propias luces, comprometiéndote con una estructura de tests antes de entender la implementación

**Enfoque correcto**: Vertical slices via tracer bullets. Un test → una implementación → repetir. Cada test responde a lo aprendido del ciclo anterior. Como acabas de escribir el código, sabes exactamente qué comportamiento importa y cómo verificarlo.

```
❌ MAL (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

✅ BIEN (vertical):
  RED→GREEN: test1 → impl1
  RED→GREEN: test2 → impl2
  RED→GREEN: test3 → impl3
  ...
```

## 3. Patrón Correcto: Vertical Slices / Tracer Bullets

Cada ciclo es una mini-unidad funcional: un test que describe un comportamiento específico, seguido del código mínimo para satisfacerlo. Esto:

- Valida el wiring end-to-end desde el primer ciclo
- Reduce el riesgo de tests "huecos" que no prueban nada real
- Mantiene el feedback loop rápido y cercano
- Permite ajustar el diseño en cada iteración

## 4. Workflow: Planning → Tracer Bullet → Incremental Loop

### 4.1 Planning

Antes de escribir código:

- [ ] Confirmar con el usuario qué cambios de interfaz se necesitan
- [ ] Confirmar con el usuario qué comportamientos testear (priorizar)
- [ ] Identificar oportunidades para [deep modules](deep-modules.md) (interfaz pequeña, implementación profunda)
- [ ] Diseñar interfaces pensando en [testabilidad](interface-design.md)
- [ ] Listar los comportamientos a testear (no pasos de implementación)
- [ ] Obtener aprobación del usuario sobre el plan

**Pregunta clave**: "¿Cómo debería verse la interfaz pública? ¿Qué comportamientos son más importantes de testear?"

> **No puedes testear todo.** Confirma con el usuario exactamente qué comportamientos importan más. Enfoca el esfuerzo de testing en paths críticos y lógica compleja, no en cada edge case posible.

### 4.2 Tracer Bullet

Escribe UN test que confirme UNA cosa sobre el sistema:

```
RED:   Escribir test para el primer comportamiento → test falla
GREEN: Escribir código mínimo para pasar → test pasa
```

Este es tu tracer bullet — prueba que el camino funciona end-to-end.

### 4.3 Incremental Loop

Para cada comportamiento restante:

```
RED:   Escribir siguiente test → falla
GREEN: Código mínimo para pasar → pasa
```

**Reglas**:

- Un test a la vez
- Solo el código necesario para pasar el test actual
- No anticipar tests futuros
- Mantener tests enfocados en comportamiento observable

### 4.4 Refactor

Después de que todos los tests pasen, busca [candidatos de refactor](refactoring.md):

- [ ] Extraer duplicación
- [ ] Profundizar módulos (mover complejidad detrás de interfaces simples)
- [ ] Aplicar principios SOLID donde sea natural
- [ ] Considerar qué revela el nuevo código sobre el existente
- [ ] Ejecutar tests después de cada paso de refactor

> **Nunca refactorices en RED.** Llega a GREEN primero.

## 5. Ejemplo Práctico Paso a Paso

Escenario: Endpoint POST /checkout que procesa un carrito y devuelve una orden.

### Paso 1 — Tracer Bullet

```
RED:  Test "debería crear una orden con carrito válido"
      → Llama POST /checkout con { items: [...] }
      → Espera 201 + body con orderId
      → FALLA (endpoint no existe)

GREEN: Crear ruta mínima POST /checkout que devuelva 201
       con un orderId hardcodeado
      → PASA
```

### Paso 2 — Segundo comportamiento

```
RED:  Test "debería rechazar carrito vacío con 400"
      → Llama POST /checkout con { items: [] }
      → Espera 400
      → FALLA (no valida)

GREEN: Agregar validación de items vacíos
      → PASA
```

### Paso 3 — Tercer comportamiento

```
RED:  Test "debería calcular el total correctamente"
      → Llama POST /checkout con items de precios conocidos
      → Espera total: 150.00 en la respuesta
      → FALLA (total hardcodeado)

GREEN: Reemplazar total hardcodeado por cálculo real
      → PASA
```

### Paso 4 — Refactor

```
- Extraer lógica de cálculo a una función pura
- Extraer validación a un middleware
- Ejecutar tests tras cada cambio → todos PASAN
```

> Observa: nunca escribimos todos los tests de golpe. Cada test guió el siguiente paso de implementación.

## 6. Checklist de TDD para Agents

### Por ciclo
- [ ] El test describe comportamiento, no implementación
- [ ] El test usa solo la interfaz pública
- [ ] El test sobreviviría un refactor interno
- [ ] El código es mínimo para este test
- [ ] No se agregan features especulativos

### Por feature
- [ ] Se planificó con el usuario antes de empezar
- [ ] Se usó tracer bullet para validar el wiring
- [ ] Cada test se escribió justo antes de su implementación
- [ ] Se refactorizó solo en GREEN
- [ ] Todos los tests pasan al finalizar

### Señales de alerta
- [ ] Tests fallan al renombrar funciones internas → acoplamiento a implementación
- [ ] Tests pasan pero el feature está roto → tests huecos
- [ ] Se escribieron 5+ tests sin ejecutar código → horizontal slicing
- [ ] Código tiene features no solicitadas → especulación en GREEN
