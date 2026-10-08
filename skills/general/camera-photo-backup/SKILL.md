---
name: camera-photo-backup
description: "Respaldo seguro de fotos/videos desde tarjeta SD de camara: montaje, copia verificada con checksums y liberacion de la tarjeta. Nunca borra sin verificar."
version: 1.1.0-reconstructed
author: Hermes Agent (RECONSTRUCTED 2026-09-07 tras incidente skills 2026-09-06 — validar)
tags: [backup, photos, sd-card, rsync, checksum]
related_skills: []
---

# Camera Photo Backup

> ⚠️ RECONSTRUCTED 2026-09-07 — cuerpo original irrecuperable tras el
> incidente de skills. Procedimiento generico y seguro (no habia fuentes
> locales). Belal: validar destinos y retencion.

## Procedimiento

1. Identificar dispositivo (`lsblk`) y montar la SD **solo lectura** si
   el flujo lo permite.
2. Destino: carpeta con fecha `<dest>/YYYY-MM-DD-<evento>/`.
3. Copiar con `rsync -a --checksum` (no mover).
4. Verificar: conteo de archivos origen vs destino + tamano total;
   muestra aleatoria abrible.
5. Solo con verificacion OK: liberar la tarjeta (formatear en camara,
   no en PC, si se va a reutilizar).

## Prohibido

- Borrar/mover antes de verificar copia + muestra.
- Operar sobre el unico ejemplar (regla 3-2-1 para material critico).
