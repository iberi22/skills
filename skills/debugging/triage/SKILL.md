---
name: triage
slug: triage
version: 1.0.0
description: Workflow sistemático para diagnosticar bugs en código. Sigue 1) entender el symptom, 2) crear hipótesis, 3) probar cada hipótesis con el mínimo experimento posible, 4) aislar la causa raíz, 5) fix + test de regresión.
license: MIT
original_source: https://github.com/mattpocock/skills
category: debugging
tags: [triage, debugging, bug, diagnosis, root-cause, workflow]
goals:
  - Diagnosticar bugs de forma sistemática y no aleatoria
  - Reducir tiempo entre symptom y causa raíz
  - Probar hipótesis con el mínimo experimento posible
  - Documentar hallazgos para evitar bugs similares
context:
  when: Reportan un bug, error, o comportamiento inesperado
  who: Cualquier coding agent
  prerequisites: Acceso al código y logs del sistema
authors:
  - mattpocock (repo original)
  - Brahyan Belalcazar (versión estructurada)
---

# Triage — Workflow de Diagnóstico de Bugs

Este skill establece un proceso sistemático de 5 pasos para diagnosticar bugs sin cambiar código al azar. Cada paso genera información que alimenta el siguiente.

## Principios

1. **No toques código sin una hipótesis.** Si no sabes qué estás probando, estás adivinando.
2. **El experimento más pequeño gana.** Reduce el scope hasta que la respuesta sea un sí o un no.
3. **Reproduce antes de diagnosticar.** Si no puedes reproducirlo, no puedes confirmar que lo arreglaste.
4. **Documenta en cada paso.** Un bug no resuelto hoy es información útil mañana.

---

## Paso 1: Entender el Symptom

Antes de tocar el código, caracteriza el problema:

- ¿Qué comportamiento se espera vs. qué ocurre?
- ¿Es consistente o intermitente?
- ¿En qué entorno ocurre? (local, staging, producción)
- ¿Cuándo empezó? ¿Qué cambió justo antes?
- ¿Hay stack traces, logs o mensajes de error?

**Entregable:** Un párrafo de 2-3 líneas que describa el symptom sin mencionar causas.

---

## Paso 2: Crear Hipótesis

Genera 2-4 explicaciones plausibles ordenadas por probabilidad. Usa tu conocimiento del sistema, no intuiciones vagas.

Formato de cada hipótesis:

```
H1: <qué está fallando> → <por qué crees eso> → <qué experimento lo confirma o rechaza>
```

Ejemplo:

```
H1: El servicio de auth retorna 401 porque el token expira antes de lo esperado.
    → El bug ocurre solo después de 15 min de inactividad.
    → Experimento: loggear el TTL del token en el momento del 401.
```

---

## Paso 3: Probar con el Mínimo Experimento Posible

Para cada hipótesis, diseña un experimento que sea:

- **Rápido:** menor a 10 minutos de setup.
- **Aislado:** no dependa de otros sistemas si es posible.
- **Binario:** produce un resultado que confirma o rechaza la hipótesis.

Técnicas útiles:

| Técnica | Cuándo usarla |
|---|---|
| **Log points** | Necesitas ver el valor de variables en runtime sin detener el flujo. |
| **Binary search en git** | El bug apareció en algún commit reciente. Usa `git bisect`. |
| **Minimal reproduction** | Elimina dependencias, código y datos hasta que el bug siga ocurriendo en lo mínimo posible. |
| **Monkey-patch temporal** | Forzar un valor o bypass para confirmar si una dependencia es la culpable. |
| **Diff de estado** | Comparar el estado del sistema (DB, cache, config) entre un entorno que funciona y uno que no. |

**Regla:** Si un experimento no reduce el espacio de búsqueda a la mitad, es demasiado grande.

---

## Paso 4: Aislar la Causa Raíz

Cuando una hipótesis se confirma, sigue bajando hasta encontrar la causa raíz, no solo el symptom.

Preguntas guía:

- ¿Es un bug en mi código o en una dependencia?
- ¿Es un error de lógica, de configuración o de datos?
- ¿Por qué este input produce este output? Sigue el flujo de datos.
- ¿Hay un invariante que se rompe? ¿Dónde se debería haber validado?

**Entregable:** Una oración que explique la causa raíz, enlazando el defecto con el efecto observable.

---

## Paso 5: Fix + Test de Regresión

1. **Corrige lo mínimo necesario.** Un fix grande es sospechoso.
2. **Verifica que el fix funciona.** Reproduce el bug con los pasos del Paso 1; debe desaparecer.
3. **Añade un test de regresión.** Si es posible, escribe un test que falle antes del fix y pase después.
4. **Documenta brevemente.** Nota en el commit o en un doc por qué ocurría y cómo se evita.

---

## Anti-patrones a evitar

- **Cambiar código y ver qué pasa.** Esto destruye información.
- **Depurar sin reproducir primero.** Pierdes la confirmación de éxito.
- **Asumir que el bug está "obvio"."** La causa raíz suele estar 2-3 niveles más abajo del symptom.
- **Saltar al fix sin hipótesis confirmada.** Arreglas el symptom, no el bug.

---

## Checklist rápido

- [ ] Symptom claramente descrito
- [ ] Hipótesis escritas y ordenadas
- [ ] Experimento mínimo ejecutado
- [ ] Causa raíz identificada
- [ ] Fix aplicado y verificado
- [ ] Test de regresión añadido
- [ ] Hallazgos documentados
