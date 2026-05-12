---
id: worldexams-curator
name: worldexams-curator
category: education
tags:
  - worldexams
  - curator
  - education
  - icfes
  - quality-control
goals:
  - "Asegurar que cada bundle de preguntas cumpla con los estándares técnicos y pedagógicos de WorldExams."
  - "Revisar la coherencia entre el contexto y la pregunta, la validez de las opciones y la claridad de la explicación."
context: |
  Integración con Cortex para guías de estilo y registro de bundles procesados.
authors:
  - Brahyan Belalcazar
---

# WorldExams Curator Skill

## Misión
Asegurar que cada bundle de preguntas cumpla con los estándares técnicos y pedagógicos de WorldExams. El curador revisa la coherencia entre el contexto y la pregunta, la validez de las opciones y la claridad de la explicación.

## Funciones
- **Alineación Pedagógica:** Verifica que la dificultad corresponda al grado solicitado.
- **Control de Calidad:** Detecta errores gramaticales o inconsistencias lógicas.
- **Normalización de Formato:** Asegura que el JSON final siga el esquema oficial.

## Integración con Cortex
El curador utiliza Cortex para:
- `projects/worldexams/guidelines` - Guías de estilo y curación.
- `context/worldexams/curation-history` - Registro de bundles procesados.

**Endpoints:**
- `POST http://localhost:8003/memory/add`
- `POST http://localhost:8003/memory/search`

## Uso del Script de Curación

```bash
python3 skills/worldexams-curator/scripts/curator.py --input generated_bundle.json --output curated_bundle.json
```
