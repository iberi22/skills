---
name: prototype
slug: prototype
version: 1.0.0
description: Workflow para prototipado rápido de features. Prioriza velocidad sobre calidad, código descartable sobre mantenible, y validación de hipótesis sobre robustez. Cambia mentalidad de "producción" a "experimento".
license: MIT
original_source: https://github.com/mattpocock/skills
category: engineering-workflow
tags: [prototype, rapid, mvp, experiment, proof-of-concept, workflow]
goals:
  - Validar hipótesis técnicas en el menor tiempo posible
  - Cambiar mentalidad de producción a experimento
  - Reducir costo de exploración de soluciones
  - Decidir rápido si seguir o pivotar
context:
  when: Necesitas validar una idea, probar un approach, o hacer POC
  who: Cualquier coding agent
  prerequisites: Conocimiento básico del dominio del problema
  avoid_when: El código va directo a producción sin refactor
---

# Prototype

Un prototipo es **código descartable que responde una pregunta**. La pregunta define la forma.

No importa si la pregunta es sobre lógica de negocio, una máquina de estados, una API, o la interfaz de usuario. El prototipo existe únicamente para validar una hipótesis concreta en el menor tiempo posible. Si no hay una pregunta clara, no hay prototipo.

## Elige una rama

Identifica qué pregunta estás respondiendo desde el prompt del usuario, el código circundante o preguntando directamente:

- **"¿Esta lógica / modelo de estado se siente bien?"** → Construye una mini app de terminal interactiva que ejercite la máquina de estados en casos difíciles de razonar en papel.
- **"¿Cómo se debería ver esto?"** → Genera varias versiones de UI visualmente distintas en una sola ruta, conmutables mediante un query param y una barra flotante de selección.

Las dos ramas producen artefactos muy diferentes. Elegir mal desperdicia el esfuerzo del prototipo. Si la pregunta es genuinamente ambigua y el usuario no está disponible, elige la rama que mejor coincida con el código circundante (módulo backend → lógica; página o componente → UI) y declara la asunción al inicio del prototipo.

## Mentalidad de prototipo

Adopta estos principios durante todo el ciclo de prototipado:

1. **Velocidad > calidad.** El objetivo es aprender, no entregar código pulido. Cada minuto cuenta.
2. **Código descartable > mantenible.** No inviertas en abstracciones, tests, documentación extensa ni patrones arquitectónicos. Esto se va a tirar.
3. **Validación > robustez.** Si falla en un edge case no crítico o no maneja errores de red, no importa. El objetivo es confirmar o refutar la hipótesis central.
4. **Un comando para correr.** Usa el runner del proyecto (`pnpm dev`, `python script.py`, `bun run`, etc.). El usuario debe poder iniciarlo sin leer instrucciones.
5. **Sin persistencia por defecto.** El estado vive en memoria. Si la pregunta involucra base de datos, usa una scratch DB o archivo local con un nombre inequívoco como `PROTOTYPE_data.json` o `scratch.sqlite`.
6. **Expón el estado.** Después de cada acción imprime o renderiza el estado completo relevante para que sea visible qué cambió y por qué.
7. **Asume que fallará.** La mayoría de los prototipos confirman que una idea no funciona. Eso también es éxito: evitaste invertir semanas en una solución inválida.

## Técnicas de prototipado rápido

Aplica estas tácticas para maximizar velocidad y minimizar fricción:

- **Copy-paste consciente:** Copia código de documentación oficial, StackOverflow, ejemplos de GitHub o proyectos previos sin remordimiento. No refactorices; pega y ajusta lo mínimo indispensable para que funcione.
- **Mock antes que real:** Usa datos fake, stubs y mocks. No conectes a APIs reales, servicios externos o colas de producción si un JSON estático o una función síncrona responde la pregunta.
- **Hardcode antes que configurable:** Si un valor varía raramente en el contexto del experimento, escríbelo directamente en el código. No añadas `config.ts`, variables de entorno, archivos `.env`, ni flags de CLI.
- **Ignora types y lint si relentizan.** Si el proyecto usa TypeScript o un linter estricto, usa `any`, `@ts-ignore` o desactiva reglas puntualmente si eso te permite moverte más rápido. No redefinas interfaces completas para un prototipo.
- **UI: múltiples variaciones radicales.** Si la pregunta es "¿cómo se debería ver esto?", genera varias versiones visualmente distintas en una sola ruta o página. Conmuta entre ellas mediante un query param (ej. `?variant=A`) y una barra flotante de selección. No hagas navegación real.
- **Logic: terminal interactivo.** Si la pregunta es "¿el modelo de estado o la lógica de negocio tiene sentido?", construye una mini aplicación de terminal que ejercite la máquina de estados en casos difíciles de razonar en papel. Permite al usuario interactuar con comandos simples.
- **No versiones, no commits intermedios.** Trabaja en un solo archivo o en la rama más cercana al objetivo. No gastes tiempo en historial de git limpio para código que se va a borrar.

## Boundary conditions: cuándo parar

Es crucial reconocer el momento de detenerse. Un prototipo que se extiende indefinidamente deja de ser experimento y se convierte en deuda técnica disfrazada:

- **La pregunta fue respondida.** Tienes suficiente información para decidir si la idea es viable o si debes pivotar.
- **El costo de seguir supera el beneficio esperado.** Si lleva más tiempo "arreglar" el prototipo para un edge case que rehacerlo limpio desde cero, detente inmediatamente.
- **Se identificó un bloqueador desconocido.** El prototipo cumplió su función al revelar un riesgo, limitación técnica o dependencia bloqueante que invalida el approach.
- **Pasaron más de 2–4 horas de trabajo neto.** Un prototipo efectivo debería responder su pregunta en pocas horas. Si se extiende más, probablemente estás construyendo algo más grande de lo necesario.
- **Se empieza a añadir tests unitarios, manejo de errores exhaustivo o logging estructurado.** Esa señal es clara: ya no estás en modo experimento; estás escribiendo código de producción sin darte cuenta.
- **Alguien dice "esto ya casi está listo para deployar".** Esa frase es una trampa. Detente, valida la hipótesis, y luego replanifica.

## Transición a producción

Nunca promuevas un prototipo directamente a producción. El código descartable está diseñado para ser borrado, no para evolucionar:

1. **No transformes el prototipo en producción directamente.** Aunque "funcione", está lleno de atajos, deuda técnica intencional y supuestos no validados.
2. **Extrae la decisión validada.** Captura la respuesta obtenida en un ADR, un commit message descriptivo, un issue de seguimiento o un archivo `NOTES.md` junto a la pregunta original.
3. **Documenta los hallazgos.** Apunta qué funcionó, qué no, qué edge cases se ignoraron y qué decisiones arquitectónicas surgieron del experimento.
4. **Reescribe desde cero con mentalidad de producción.** Ahora que sabes que el approach es viable, diseña la solución robusta, testeable, mantenible y segura.
5. **Borra el prototipo.** No dejes código muerto en el repositorio. O absórbelo explícitamente en la nueva implementación, o elimínalo por completo. No lo dejes comentado ni en una carpeta `_old`.

## Reglas compartidas entre ramas (Logic / UI)

Independientemente de si el prototipo es de lógica o de interfaz, estas reglas aplican siempre:

1. **Descartable desde el día uno, claramente marcado.** Coloca el código cerca de donde se usará finalmente (mismo módulo, misma página, misma carpeta) pero con un nombre obvio de prototipo (ej. `prototype-cart.ts`, `PlaygroundVariants.tsx`, `/prototype/page.tsx`). No inventes una estructura de rutas nueva ni un directorio `experiments/` a nivel raíz.
2. **Sin pulido.** Sin tests, sin manejo de errores más allá de lo mínimo necesario para que corra, sin abstracciones genéricas, sin i18n, sin analytics. El punto es aprender rápido y luego borrar.
3. **Eliminar o absorber al terminar.** Cuando el prototipo haya respondido su pregunta, bórralo o integra la decisión validada al código real. No lo dejes pudriéndose en el repositorio durante semanas.

## Al finalizar

La **respuesta** es lo único que vale la pena conservar de un prototipo. El código en sí es irrelevante una vez cumplido su propósito.

Si el usuario está disponible al terminar, captura la respuesta en una conversación rápida y decide juntos si absorber, reescribir o descartar. Si el usuario no está disponible, deja un placeholder claro (un `TODO` o un `NOTES.md`) para que pueda completarse antes de eliminar definitivamente el prototipo.

Recuerda: un buen prototipo es aquel que te permite decidir rápido. A veces la mejor decisión es "no funciona, descartemos esta idea". Eso ahorra semanas de trabajo.
