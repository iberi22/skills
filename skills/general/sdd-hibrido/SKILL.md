---
name: sdd-hibrido
description: 'Use when routing a task before creating SDD artifacts.'
version: 0.1.0
author: BELA
tags: [sdd, routing, gitcore, minimal]
---

# SDD Hibrido Minimalista — Routing Organico

Antes de crear cualquier `.gitcore/sdd/` debes aplicar routing. Si no, no crees SDD.

## Regla unica (gentle-ai trigger-rules adaptado)

| Ruta | Cuando usarla | Que pasa |
|------|---------------|----------|
| **Direct inline** | 1-3 files ya entendidos, o 1 file mecanico sin research ni design pendiente | Haces inline con file+terminal, sin delegar, sin SDD |
| **Delegated direct** | 4+ files para entender, o 2+ files non-trivial para escribir, o necesitas research amplio | Delegas 1 explorer/writer via delegate_task (fresh context), Xavier busca skills relevantes via xavier-skill-indexer, sin crear .gitcore/sdd/ |
| **Optional SDD** | Ambiguedad alta, o un spec duradero reduciria incertidumbre material | Propones SDD opcional al usuario. Solo si dice SI creas `.gitcore/sdd/specs/###-feat/onepage.md` (1 pagina que combina spec P1 + plan HOW minimo + tasks [P]). Si dice NO, reduces scope a direct/delegated. |

File counts = contexto necesario para la accion actual, no riesgo ni umbral SDD. Riesgo solo refuerza verify, no fuerza SDD.

Si trabajo aparentemente simple revela ambiguedad alta, ofrece SDD en el siguiente safe boundary. Nunca enrolles SDD silencioso.

## Ubicacion aislada

- Todo SDD externo vive en `.gitcore/sdd/specs/###-feat/onepage.md` (nunca en docs/plans/ ni AGENTS.md)
- `rm -rf .gitcore/sdd` limpia sin tocar .gitcore/features.json ni issues
- Una pagina onepage mapea a N issues file-islands existentes (1 onepage -> N .gitcore/issues/*.md)

## Referencias

- `references/routing.md` — tabla completa y ejemplos
- Vendored: gentle-ai docs/trigger-rules.md commit v2.3.0 MIT (atribucion en references/ATTRIBUTION.md)
