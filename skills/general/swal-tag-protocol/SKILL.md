---
name: swal-tag-protocol
description: "Protocolo de tags de release SWAL: formato vX.Y.Z, condiciones para taguear (CI verde + QA + CHANGELOG + ADR), single-source de manifests y verificacion."
version: 1.1.0-reconstructed
author: Hermes Agent (RECONSTRUCTED 2026-09-07 tras incidente skills 2026-09-06 — validar)
tags: [swal, git, tags, release, semver, versioning]
related_skills: [swal-preflight]
---

# SWAL Tag Protocol

> ⚠️ RECONSTRUCTED 2026-09-07 — cuerpo original irrecuperable tras el
> incidente de skills. Reconstruido desde `swal-preflight` (Sistema de
> versiones) + `docs/SWAL/VERSIONING.md`. Belal: validar.

## Reglas (de `swal-preflight`, Sistema de versiones)

- SemVer 2.0.0 estricto; `0.y.z` hasta gate 1.0.0.
- `feat:` → minor, `fix:` → patch, `feat!:` → major (si >=1.0) / minor
  (si 0.y.z). Sugerir bump con `swal-preflight bump --dry-run`.
- Tag `vX.Y.Z` SOLO con: CI verde + QA + CHANGELOG + ADR firmada.
- Single source: todos los manifests coinciden (`swal-preflight check`).

## Ceremonia

1. `swal-preflight check --cwd <app>` en verde (versions, changelog, git).
2. Confirmar `git status` limpio y `commitsSinceTag` revisado.
3. Crear tag anotado (`git tag -a vX.Y.Z -m "..."`) y pushear tag.
4. Verificar tag remoto + CI del tag en verde.

## Prohibido

- Taguear con CI rojo, CHANGELOG sin `[Unreleased]` resuelto, o dirty.
- Re-taguear un numero publicado (nuevo fix = nuevo patch).
