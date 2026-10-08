---
name: informe-tui
description: "Use when el usuario pida el informe TUI de 4 areas o el prompt viejo. Bloques fijos, sin relleno."
version: 1.0.0
author: Hermes Agent
tags: [informe, tui, formato, markdown, entrega, control]
related_skills: [informe-final]
---

# Informe TUI — patron de 4 areas (version mejorada del prompt viejo)

Formato de respuesta para cuando BELA pide "el prompt viejo", "respondeme por
el TUI", "informe TUI", "las 4 areas". Es un MODO: se activa por comando y se
sale por comando. Fuera de este modo manda `informe-final`.

## Triggers (activar)

Cualquiera de estos, literal o casi:
- "prompt viejo", "el viejo prompt", "devuélvete al prompt"
- "respondeme por el TUI", "en formato TUI", "informe TUI"
- "las 4 areas", "estructura de control", "formato de 4 bloques"
- "dale con el patrón", "control limpio"

## Anti-triggers (NO activar, ni en forma parcial)

- "informe final", "handoff", "cierre de fase" → `informe-final`.
- Una pregunta puntual ("¿qué hace este script?") → respuesta normal, sin bloques.
- Petición de código o edicion → se ejecuta y se responde corto. El patron de 4
  areas es un INFORME, no un sustituto de hacer el trabajo.

## Como salir del modo

"informe normal", "ya no TUI", "veredicto normal" → volver a `informe-final`.
El modo no persiste entre sesiones: solo vive mientras el usuario lo pide.

## EL PATRON (copiar/pegar tal cual)

```
### 1. ESTADO
- **Contexto:** <1 linea: stack y objetivo de la sesion, con viabilidad>
- **Hecho:** <2-5 vinetas; cada una con evidencia: commit, test o ruta:linea>

### 2. AVANCE
- **Progreso:** <% medido + fuente, o "no medible: <motivo>">
- **Problema mayor:** <mecanismo en 1 linea, o "Ninguno en esta sesion">

### 3. ENTREGA
- **Listo para probar:** <ruta exacta con :linea, endpoint o comando de prueba>
- **Decision del usuario:** <opcion A/B con default recomendado, o "Ninguna: siguiente paso ya definido">

### 4. RUTA
- **Todo:** <bloque cerrado -> siguiente bloque | bloque abierto -> 3 micro-pasos>
- **Opciones:**
  1. <orden> - <que hace> - `<comando real, ejecutable tal cual>`
  2. ...
  3. ...
```

## Escala: completo vs compacto (regla que el prompt viejo no tenia)

- **Completo** (el de arriba, 4 areas con 2-4 bullets cada una): el turno
  cerro trabajo — commit, verify, gate en verde, o se completo una fase. Aplica
  REGLA #7: cada bullet de "Hecho" lleva su evidencia.
- **Compacto** (mismos 4 encabezados, UNA linea por area, <= 12 lineas): turno
  informativo, lectura, respuesta a duda, estado sin cambios. Los 4 bloques
  siguen presentes; lo que se comprime es el relleno, nunca la estructura.

Criterio de corte: si no hay nada que "entregar" ni commit en el turno, compacto.
Si hay diff, completo.

## Por que este patron es MEJOR que el prompt viejo (8 diffs, con el porque)

El prompt viejo (el de `~`) fallaba en siete puntos concretos. No volver a
ellos:

1. **"Progreso estimado en porcentaje" → % con fuente o "no medible".** El viejo
   pedia un numero inventado cuando no habia medicion; por eso salia "80%" sin
   base. Ahora: `62% (features.json 31/50)` o `no medible: sin PLAN`.
2. **"Mayor problema abordado" → admite "Ninguno".** El viejo exigia narrativa
   de dificultad siempre: era relleno. Si no hubo problema real, una linea de
   "Ninguno" y punto.
3. **"Decisiones del usuario" solo si es ROJO de verdad.** El viejo pedia
   exponer "un dilema tecnico critico" aunque no existiera. Aqui: dilema
   irreversible/bloqueante, con **default recomendado** (orden permanente:
   decidir default y seguir; preguntar solo lo que no se puede deshacer).
4. **"Entregables" con prueba.** Cada entregable es `ruta:linea`, endpoint o
   comando — no "el modulo X esta listo". El viejo permitia afirmarlo sin cita.
5. **Los comandos de las opciones se ejecutan de verdad.** Nunca placeholders
   inventados (`cargo test --release` en un repo que no lo usa, flags de npm que
   no existen). Si no se ha corrido en esta sesion, marcarlo `(sin ejecutar)`.
6. **Escala compacto/completo.** El viejo obligaba 4 areas infladas a una
   pregunta de una linea: mas tokens, menos senal.
7. **Reglas de render TUI medidas, no supuestas.** Ver abajo — el patron viejo
   prohibia emoji y "caracteres complejos" por miedo al padding, pero hacia
   cosas que no eran el problema: el fallo real de Rich no son los acentos, son
   los bloques de dibujo en lineas consecutivas (Rich los funde en un parrafo).
8. **El JSON de sesion va aparte.** Este modo no entrega `.md`. Si el turno tuvo
   commits, el artefacto para agentes sigue siendo el JSON compacto de
   `informe-final` en `docs/SWAL/sessions/` — el patron TUI es la capa de chat.

## Reglas de render para el TUI (medidas, no supuestas)

Con `display.final_response_markdown: render` la respuesta pasa por
`rich.markdown.Markdown` dentro de un Panel. Comprobado:

- `### H3` SI renderiza (H1 queda centrado → usar H2/H3, nunca H1).
- Tabla GFM SI, alineada por ESPACIOS, sin gutter: max 4 columnas, celdas <40
  chars, ninguna fila por encima de ~100 columnas.
- `-` y `1.` SI, anidados con sangria. `> cita` SI. `---` (hr) SI.
- **NO**: mermaid, imagenes, y **NO** cajas/ASCII art (`┌─┐`, `█ █`) en lineas
  seguidas — Rich las funde en un parrafo y se rompen. Para separar: `---`.
- **NO**: bloques de codigo multi-linea esperando el fence; el texto sale pero
  sin marco. Comandos en inline `` `cmd` `` o en celda de tabla.
- Acentos y `ñ` van bien. Emoji: usar solo ASCII/plain en bloques de control.

## Estilo de cada linea

- Una idea por vineta, una linea. Cero parrafos, cero "en esta seccion analizo".
- Cada frase lleva un numero, una ruta o una decision.
- Si un area no aplica: `Ninguna requerida en este punto` / `Ninguno` — una
  linea, no un parrafo justificandolo.

## Interaccion con otras reglas (no contradicciones, sino prioridad)

- Idioma: chat en **espanol** siempre (regla dura). Los identificadores,
  rutas y comandos van tal cual.
- REGLA #7: "Hecho" sin evidencia (commit, test, `git status`) NO cuenta como
  hecho; se mueve a RUTA como pendiente.
- Tablas: solo cuando haya 3+ filas comparables. Una cifra va en texto.

Bloques listos para pegar y tabla de "viñetas que NO valen": ver
`references/patron-tui.md`.