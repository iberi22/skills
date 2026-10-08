---
name: subagent-output-truncation
description: Fix subagents that hit max output tokens and ship nothing.
---

# Subagent output truncation

Un subagente que muere con `finish_reason='length'` no fallo: se quedo sin
presupuesto de tokens antes de emitir su entregable. Casi siempre la causa es
`reasoning_effort` alto sobre un modelo con ventana chica, no el prompt.

## Diagnostico primero

1. `delegate_task(action='list')` -> el estado real (`running` / `completed`).
   Un `running` con 20+ minutos y sin artefacto en disco es el caso problematico.
2. Verificar si el ARTEFACTO existe. El log del hijo puede estar lleno de
   `result | terminal ok` y aun asi no haber escrito nada. El log miente
   sobre el progreso; el archivo en disco no.
3. Contar las lineas `finish_reason='length'` del log vivo
   (`~/.hermes/cache/delegation/live/<id>/task-N.log`).

## La causa raiz

`reasoning_effort: xhigh` gasta el presupuesto en razonamiento antes de que el
modelo escriba. Con un modelo de ventana corta el hijo razona 20 minutos y
muerre sin emitir. Medido 2026-10-01 en GOS con `space-bunny-free`: 2 de 3
hijos truncaron sin dejar archivo; el que completo habia escrito en <7 min.

```bash
hermes config get delegation.reasoning_effort   # antes: xhigh
hermes config set  delegation.reasoning_effort high
hermes config set  model.reasoning_effort high   # el padre sufre igual
```

Hermes REFUSA que el agente escriba `~/.hermes/config.yaml` con la herramienta
de patch/write. Usar `hermes config set`; el patch directo falla por diseño
(archivo marcado como sensible).

## Cuando el hijo ya esta atascado

`delegate_task(action='steer')` encola el texto para su siguiente tool result.
Sirve para: "deja de investigar, escribe el archivo", "maximo N lineas",
"responde en menos de K lineas". No corta la llamada en curso.

Un steer que funciona contiene: prohibicion explicita de seguir leyendo,
limite de tamano, y el esqueleto exacto con los datos ya verificados para que
no tenga que volver a buscarlos.

## Reglas de prompt que evitan el truncamiento

- Dar los datos verificados EN el prompt. El hijo que busca 20 archivos
  pierde el presupuesto; el que recibe los datos escribe.
- Poner un limite de tamano explicito ("maximo 250 lineas", "responde en 20").
- Un entregable, un archivo. "Audita y ademas implementa" = ninguno de los dos.
- Exigir el path absoluto del artefacto en la respuesta final.

## Lo que NO es la causa

- `max_summary_chars` (12000): recorta el resumen de vuelta, no la generacion.
- `max_iterations` (500): son iteraciones de herramientas, no tokens.
- `child_timeout_seconds`: da 1800s y los hijos murieron a los ~1200s sin
  timeout, por tokens.

## Verificacion del fix

Un hijo que completa debe dejar el archivo Y responder corto. Comprobar el
archivo en disco, no el estado `completed`: un hijo puede marcarse completado
y haber entregado la mitad.
