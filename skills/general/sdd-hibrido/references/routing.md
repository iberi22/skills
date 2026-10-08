# Routing Organico — Decision Tree (gentle-ai v2.3.0 adaptado)
<!-- vendored from gentle-ai docs/trigger-rules.md commit v2.3.0 MIT — ver ATTRIBUTION.md -->

## Tabla routing

| Ruta | Condicion | Accion | SDD artifacts |
|------|-----------|--------|---------------|
| Direct inline | 1-3 files para entender, o 1 file mecanico sin research/design | Haz inline file+terminal | 0 |
| Delegated direct | 4+ files para entender, o 2+ non-trivial para escribir, o research amplio | delegate_task 1 writer, Xavier busca skills | 0 |
| Optional SDD | Ambiguedad alta, spec duradero reduce incertidumbre | Proponer SDD, si SI crear onepage.md | 1 file |

## Ejemplos

- Fix typo en README -> direct inline
- Refactor auth middleware (3 files) + tests -> delegated direct
- Feature "realtime sync garaje con offline" con 3 stakeholders y contratos desconocidos -> optional SDD -> onepage -> luego N issues file-islands

## Que no hacer

- No contar riesgo para forzar SDD — riesgo solo refuerza verify
- No crear .gitcore/sdd/ sin pasar por esta tabla
- Si simple revela ambiguedad, ofrece SDD en siguiente boundary, nunca silently
