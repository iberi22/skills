---
id: worldexams-generator
name: worldexams-generator
category: education
tags:
  - worldexams
  - generator
  - education
  - icfes
  - minimax
  - mcp
goals:
  - "Generar bundles de preguntas ICFES Colombia (Matemáticas, Lectura Crítica, Ciencias, Sociales, Inglés) para grados 6, 9 y 11 usando MiniMax MCP."
  - "Obtener contextos actualizados y generar preguntas de opción múltiple con única respuesta."
context: |
  Utiliza MiniMax M2.7 y web_search para investigar estándares curriculares actuales.
authors:
  - Brahyan Belalcazar
---

# WorldExams Generator Skill

## Misión
Generar contenido pedagógico de alta calidad alineado con los estándares del ICFES Colombia. El skill utiliza MiniMax M2.7 y la herramienta `web_search` para obtener contextos actualizados y generar preguntas de opción múltiple con única respuesta.

## Alcance
- **Grados:** 6, 9, 11
- **Materias:**
  - Matemáticas
  - Lectura Crítica
  - Ciencias Naturales
  - Sociales y Ciudadanas
  - Inglés

## Herramientas Utilizadas
- `minimax-coding-plan-mcp`: Para búsqueda web (`web_search`) y razonamiento complejo.
- `cortex-memory`: Para persistencia de patrones de preguntas y temas generados.

## Integración con Cortex
Este skill debe persistir y consultar la memoria central en los siguientes paths:
- `projects/worldexams/overview` - Resumen del proyecto y metas de generación.
- `context/worldexams/active` - Estado actual de la generación de bundles.
- `projects/worldexams/patterns` - Estándares de preguntas validados.

**Endpoints:**
- `POST http://localhost:8003/memory/add`
- `POST http://localhost:8003/memory/search`

## Uso del Script de Generación

```bash
python3 skills/worldexams-generator/scripts/generator.py --grade 11 --subject math --count 10 --output bundle.json
```

## Formato de Bundle (JSON)
```json
{
  "metadata": {
    "grade": 11,
    "subject": "math",
    "version": "1.0"
  },
  "questions": [
    {
      "id": "q1",
      "context": "Texto o planteamiento del problema...",
      "question": "¿Cuál es el valor de X?",
      "options": ["A", "B", "C", "D"],
      "answer": 0,
      "explanation": "Explicación pedagógica..."
    }
  ]
}
```
