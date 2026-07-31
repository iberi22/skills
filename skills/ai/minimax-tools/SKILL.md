---
id: minimax-tools
name: minimax-tools
category: ai
tags:
  - minimax
  - mcp
  - groq
  - whisper
  - web-search
  - image-understanding
goals:
  - "Configurar MiniMax M2.7 con MCP tools (web_search, understand_image) y Groq Whisper para audio."
  - "Ideal para agentes que necesitan búsqueda web, análisis de imágenes y transcripción de audio."
context: |
  Requiere MiniMax API Key (Coding Plan) y uvx instalado.
  Groq Whisper actúa como fallback para transcripción de audio.
authors:
  - Brahyan Belalcazar
---

# MiniMax Tools — MCP + Audio Transcription

## Visión General

Este skill configura dos capacidades críticas para agentes SWAL:

1. **MiniMax MCP Server** — `web_search` + `understand_image` para MiniMax M2.7
2. **Groq Whisper** — Transcripción de audio (no disponible en MiniMax nativamente)

## Parte 1: MiniMax MCP Server

### Requisitos
- MiniMax API Key (del Coding Plan o cuenta regular)
- `uvx` instalado

### Instalar uvx

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

### Configurar MCP en ZeroClaw/OpenClaw

ZeroClaw ya tiene MiniMax bundled con:
- ✅ `MiniMax-VL-01` — image understanding (incluido en `minimax/MiniMax-M2.7`)
- ✅ `web_search` — via MiniMax Coding Plan API

**Problema conocido:** La implementación de `web_search` en ZeroClaw oficial para MiniMax no está bien configurada. La solución es agregar el MCP server manualmente.

### Agregar MCP Server manualmente

```bash
# En el contenedor/servidor donde corre ZeroClaw
zeroclaw mcp add MiniMax \
  --command uvx \
  --args minimax-coding-plan-mcp -y \
  --env MINIMAX_API_KEY=tu_api_key \
  --env MINIMAX_API_HOST=https://api.minimax.io
```

### Verificar configuración

```bash
zeroclaw mcp list
# Debe mostrar: minimax-websearch, minimax-understand-image
```

### Alternativa: Configurar en ~/.openclaw/config.yaml

```yaml
mcp:
  servers:
    minimax:
      command: uvx
      args: ["minimax-coding-plan-mcp", "-y"]
      env:
        MINIMAX_API_KEY: "${MINIMAX_API_KEY}"
        MINIMAX_API_HOST: "https://api.minimax.io"
```

## Parte 2: Groq Whisper (Audio Transcription)

MiniMax M2.7 no tiene capacidades de audio → usar Groq Whisper como fallback.

### Configurar GROQ_API_KEY

```bash
export GROQ_API_KEY=gsak_...
```

### Script de transcripción (para mensajes de voz)

```bash
#!/bin/bash
# Transcribir audio OGG usando Groq Whisper API
# Uso: ./transcribe.sh audio.ogg

AUDIO_FILE="$1"
TEMP_FILE=$(mktemp /tmp/audio.XXXXXX.ogg)

cp "$AUDIO_FILE" "$TEMP_FILE"

curl -s -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -F "file=@$TEMP_FILE" \
  -F "model=whisper-large-v3" \
  -F "language=es"

rm -f "$TEMP_FILE"
```

### Integración en ZeroClaw

En el config.toml del agente:

```toml
[audio]
transcription_provider = "groq"
transcription_model = "whisper-large-v3"
groq_api_key = "${GROQ_API_KEY}"
```

## Parte 3: Setup Completo para Agente

### Paso 1: Variables de entorno requeridas

```bash
# Requeridas
export MINIMAX_API_KEY="tu_minimax_key"
export GROQ_API_KEY="tu_groq_key"

# Opcionales
export DEFAULT_MODEL="minimax/MiniMax-M2.7"
export DEFAULT_PROVIDER="minimax"
```

### Paso 2: Verificar herramientas disponibles

```bash
# Verificar web_search
zeroclaw tools list | grep web_search

# Verificar image understanding
zeroclaw tools list | grep understand_image

# Verificar audio transcription
echo "GROQ_API_KEY configured: $(test -n "$GROQ_API_KEY" && echo YES || echo NO)"
```

### Paso 3: Test rápido

```bash
# Test web search
zeroclaw invoke web_search --query "test"

# Test image understanding (requiere URL de imagen)
zeroclaw invoke understand_image --prompt "describe this image" --image_url "https://..."

# Test audio (requiere archivo de audio)
./transcribe.sh audio.ogg
```

## Configuración para swal-zeroclaw (Docker)

En el contenedor `swal-zeroclaw`, agregar al `docker-compose.swal.yml`:

```yaml
environment:
  - MINIMAX_API_KEY=${MINIMAX_API_KEY}
  - GROQ_API_KEY=${GROQ_API_KEY}
  - DEFAULT_MODEL=minimax/MiniMax-M2.7
```

Y en el entrypoint:

```bash
# Instalar uvx si no existe
if ! command -v uvx &>/dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Agregar MCP server
zeroclaw mcp add MiniMax \
  --command uvx \
  --args minimax-coding-plan-mcp -y \
  --env MINIMAX_API_KEY=${MINIMAX_API_KEY} \
  --env MINIMAX_API_HOST=https://api.minimax.io
```

## Solución de Problemas

### "web_search not found" en MiniMax M2.7
**Causa:** La herramienta no está registrada correctamente.
**Solución:**
1. Verificar que `MINIMAX_API_KEY` tiene plan Coding Plan activo
2. Agregar MCP server manualmente (sección arriba)
3. Reiniciar el daemon: `zeroclaw daemon restart`

### "understand_image not working"
**Causa:** MiniMax-VL-01 requiere que la imagen sea pasada como URL o base64.
**Solución:**
- Para URLs: funciona directo
- Para archivos locales: convertir a base64 primero

### "GROQ_API_KEY not found"
**Causa:** La variable no está configurada en el entorno del agente.
**Solución:**
```bash
export GROQ_API_KEY=gsak_...  # Agregar a secrets.env
source ~/.openclaw/secrets.env  # Recargar en sesión
```

## Resumen de APIs

| Herramienta | Provider | API Key Requerida | Notas |
|------------|----------|-------------------|-------|
| web_search | MiniMax MCP | MINIMAX_API_KEY | Solo Coding Plan |
| understand_image | MiniMax-VL-01 | MINIMAX_API_KEY | Bundled con M2.7 |
| Audio transcription | Groq Whisper | GROQ_API_KEY | Fallback para audio |

## Generación de Contenido con Web Search

Para la generación de exámenes (WorldExams), `web_search` es fundamental para:
1. Buscar ejemplos reales de preguntas ICFES Colombia (grados 6, 9, 11).
2. Investigar temas curriculares actuales del Ministerio de Educación.
3. Encontrar textos de lectura crítica y artículos científicos para base de preguntas.

### Prompt Sugerido para Generación
"Usa la herramienta `web_search` para buscar el estándar actual del ICFES para [MATERIA] de grado [GRADO]. Luego genera 5 preguntas siguiendo ese formato JSON."

## Activación

Este skill se activa automáticamente cuando:
1. El agente usa modelo `minimax/MiniMax-M2.7`
2. Necesita buscar información en la web
3. Necesita analizar imágenes
4. Recibe mensajes de audio/voz

## Notas para SWAL Agents

- El agente principal (esta sesión) ya tiene Groq Whisper configurado
- Para otros agentes, asegurar que `secrets.env` tenga `GROQ_API_KEY`
- El MCP server de MiniMax debe estar corriendo en el mismo host que el agente
