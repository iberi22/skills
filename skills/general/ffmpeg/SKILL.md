---
name: ffmpeg
description: Edición de video real con FFmpeg local (cortar, unir, vertical 9:16, captions, loudness, exports por plataforma). Úsalo siempre que haya footage real (mp4/mov/mkv); HyperFrames es solo para composiciones/slideshows.
---

# FFmpeg (footage real, local, verificado)

Origen: port de https://github.com/kajisho5/ffmpeg-skill (MIT). 42 scripts en
`scripts/`, solo Python stdlib + ffmpeg/ffprobe. Nada sale a la nube.

## Workflow obligatorio (esto es lo que evitó otro baby-shower)

1. `probe.py` a cada input: duración, fps, resolución, codecs, audio, VFR.
   Planificar desde números reales, nunca suponer.
2. Preferir lossless (stream copy) cuando no haya filtros de por medio.
3. `--dry-run --json` antes de encodes largos; `--fast` para preview.
4. Orden de cadena: color → cut → join → silence → fit → captions →
   audio → loudness → export. Fit/crop ANTES de captions.
5. `check.py OUTPUT --platform X` + `probe.py` al resultado. Reportar
   números exactos (duración, resolución, fps, audio).
6. `look.py` (contact sheet PNG) + vision_analyze cuando la imagen cambió.
   Sin revisión visual no hay entrega.
7. Jamás sobrescribir originales. Todo es determinista y re-ejecutable.

## Timeline para DaVinci Resolve

Resolve importa Final Cut Pro 7 XML (.xml). Para entregar timeline editable:
generar el XML con script stdlib (sequence 1080x1920 en format
samplecharacteristics, clips referenciados por path absoluto + in/out reales
del probe). Resolve relinkea y el usuario sigue editando ahí.

## Scripts clave

probe, cut, join, fit, caption, loudness, audio, export, check, verify,
look, silence, scenes, sync, report, render (project.json declarativo),
batch (watch folder con cache por hash).
