---
name: gemini-capable
description: Use when calling Google AI Studio (Gemini) directly - auth, endpoint, thinking, vision, code execution. For which model to use, see llm-routing.
version: "2.0"
updated: "2026-04-23"
author: swal
license: MIT
metadata:
  provider: Google AI Studio
  version: 2.0
---

# Gemini API - Modelos Más Capaces

> **⚡ Investigación completa de Gemini API 2026**

---

## 🤖 Modelos

La elección de modelo vive en `llm-routing`. Los ids vigentes salen de la API en vivo (`GET https://generativelanguage.googleapis.com/v1beta/models`), no de una tabla estática.

---

## 🧠 Thinking Mode (Chain of Thought)

**Solo disponible en Gemini 2.5 Pro y 2.5 Flash**

### ¿Qué es?
Thinking divide la generación en:
1. **Reasoning interno** - El modelo "piensa" antes de responder
2. **Output final** - Respuesta refinada

### Costo adicional
- Thinking output tokens = $3.50/1M (2.5 Flash)
- Budget tokens: 1024 - 32768

### Ejemplo API:
```javascript
POST /v1beta/openai/chat/completions

{
  "model": "gemini-2.5-flash",
  "messages": [{"role": "user", "content": "Solve: Why is sky blue?"}],
  "thinking": {
    "type": "enabled",
    "budget_tokens": 2048
  }
}
```

### ¿Cuándo usar?
| Task | Thinking | Budget |
|------|----------|--------|
| Quick Q&A | ❌ | - |
| Math/Code | ✅ | 4096+ |
| Complex reasoning | ✅ | 8192+ |
| Architecture design | ✅ | 16384+ |

---

## 👁️ Vision (Image Understanding)

**Todos los modelos Gemini son multimodales**

```javascript
{
  "model": "gemini-2.5-flash",
  "messages": [{
    "role": "user",
    "content": [
      { "type": "text", "text": "What do you see?" },
      { "type": "image_url", "image_url": { "url": "https://..." } }
    ]
  }]
}
```

### Formatos soportados:
- JPEG, PNG, WebP, GIF, BMP
- PDF (hasta 300 páginas)
- Video (extraits de frames)

---

## 💻 Code Execution

**Gemini puede ejecutar código!**

```javascript
{
  "model": "gemini-2.5-flash",
  "messages": [{"role": "user", "content": "Write and run Python: print('Hello')"}],
  "tools": [{
    "type": "function",
    "function": {
      "name": "bash",
      "description": "Execute code",
      "parameters": { "type": "object", "properties": {} }
    }
  }]
}
```

---

## 🔧 API Reference

### Endpoint
```
https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
```

### Authentication
```bash
?key=YOUR_API_KEY
```

### Available Models via API
```
models/gemini-2.5-pro
models/gemini-2.5-flash
models/gemini-2.5-flash-lite
models/gemini-2.0-flash
models/gemini-2.0-flash-lite
models/gemini-1.5-pro
models/gemini-1.5-flash
```

---

## 📊 Free Tier (1,500 req/día por key)

| Límite | Valor |
|--------|-------|
| Requests/day | 1,500 |
| RPM | 15 |
| TPM | 1,000,000 |

**Con 4 keys = 6,000 req/día**

---

## 💰 Costos Reales con $10

| Modelo | Input $10 | Output $10 |
|--------|-----------|-------------|
| 2.5 Pro | 10M tokens | 1M tokens |
| 2.5 Flash | 33M tokens | 11M tokens |
| 2.5 Flash-Lite | 100M tokens | 25M tokens |
| 2.0 Flash | 33M tokens | 11M tokens |

---

## 🎯 Recomendaciones SWAL

Ver `llm-routing` (tabla canónica de modelos y proveedores).

---

## 🔄 Fallback Chain (SWAL)

```
2.5 Flash (Key #1)
    ↓ rate limit
2.5 Flash (Key #2)
    ↓ rate limit
2.5 Flash (Key #3)
    ↓ rate limit
2.5 Flash (Key #4)
    ↓ all exhausted
2.0 Flash-Lite (cheapest)
    ↓ all exhausted
Groq Llama (free)
```

---

## 📁 API Keys SWAL

| Key | API Key | Uso |
|-----|---------|-----|
| #1 | AIzaSyBXo... | Primary |
| #2 | AIzaSyCxp... | Secondary |
| #3 | AIzaSyDtx... | Tertiary |
| #4 | AIzaSyDj9... | Quaternary |

---

**Version:** 2.0
**Updated:** 2026-04-20
**Source:** ai.google.dev, OpenRouter, Shareuhack