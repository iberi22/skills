---
id: worldexams-validator
name: worldexams-validator
category: education
tags:
  - worldexams
  - validator
  - education
  - icfes
  - quality-assurance
goals:
  - "Garantizar que el 100% de los bundles entregados sean válidos técnicamente y aptos para su uso académico."
  - "Verificar integridad técnica y calidad pedagógica, activando regeneración automática si es necesario."
context: |
  Si un bundle falla la validación, este skill puede solicitar al worldexams-generator la regeneración de las preguntas defectuosas.
authors:
  - Brahyan Belalcazar
---

# WorldExams Validator Skill

## Misión
Garantizar que el 100% de los bundles entregados sean válidos técnicamente y aptos para su uso académico. Si un bundle falla la validación, este skill puede solicitar al `worldexams-generator` la regeneración de las preguntas defectuosas.

## Reglas de Validación
- **Esquema JSON:** Debe cumplir estrictamente con la estructura de metadatos y preguntas.
- **Unicidad:** No se permiten preguntas duplicadas en el mismo bundle.
- **Integridad:** La respuesta correcta (`answer`) debe apuntar a un índice válido en el array de `options`.
- **Calidad:** El contexto debe tener una longitud mínima y la explicación debe ser coherente.

## Regeneración Automática
Si se detectan fallos, el validador emite un reporte detallado que el agente puede usar para re-lanzar el generador con instrucciones correctivas.

## Integración con Cortex
- `projects/worldexams/validation-logs` - Registro histórico de errores y éxitos.
- `context/worldexams/last-validation` - Estado de la última validación realizada.

**Endpoints:**
- `POST http://localhost:8003/memory/add`
- `POST http://localhost:8003/memory/search`

## Uso del Script de Validación

```bash
python3 skills/worldexams-validator/scripts/validator.py --input curated_bundle.json
```
