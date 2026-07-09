---
id: gemini
name: gemini
category: tools
tags:
  - gemini
goals:
  - "> Gemini CLI integration for local AI-powered development tasks."
authors:
  - Brahyan Belalcazar
---

# Gemini CLI Skill

> Gemini CLI integration for local AI-powered development tasks.

## 📦 Instalación

```bash
# Instalar Gemini CLI
npm install -g @google/gemini-cli

# Verificar
gemini --version
```

## ⚙️ Configuración

```bash
# Login con Google
gemini login

# Configurar modelo
gemini config set model gemini-2.0-flash

# Verificar
gemini config list
```

## 🚀 Uso

### Desde OpenClaw

```python
from skills.gemini.gemini_client import GeminiCLI

gemini = GeminiCLI()

# Ejecutar prompt
result = gemini.run("Explain this code")
print(result)

# Modo interactivo
gemini.interactive()

# Con archivo
result = gemini.run_file("path/to/file.py")

# Chat session
session = gemini.create_session("my-session")
response = session.send("Help me with this bug")
```

## 📁 Estructura

```
skills/gemini/
├── SKILL.md              # Este archivo
├── gemini_client.py      # Cliente Python
└── scripts/
    └── gemini.ps1        # PowerShell wrapper
```

## 🔧 API Reference

### GeminiCLI

```python
from gemini_client import GeminiCLI

# Basic
cli = GeminiCLI()
result = cli.run("Your prompt here")

# Con opciones
result = cli.run(
    prompt="Analyze this code",
    model="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=2000,
    system_prompt="You are a code reviewer"
)

# Archivos
result = cli.analyze_file("src/module.ts")
result = cli.analyze_directory("src/")

# Chat
session = cli.chat_session("debug-session")
response = session.send("What's wrong with this code?")
```

## 🎯 Casos de Uso

| Task | Comando |
|------|---------|
| Explicar código | `gemini run "Explain this Python code"` |
| Code review | `gemini run "Review this PR"` |
| Generar tests | `gemini run "Write unit tests for this module"` |
| Refactorizar | `gemini run "Refactor this function"` |
| Debug | `gemini run "Find the bug in this code"` |

## 🔗 Integración con OpenClaw

```python
from skills.gemini.gemini_client import GeminiCLI

def handle_analysis_task(task: str, context: dict = None):
    """Delegar análisis a Gemini."""
    gemini = GeminiCLI()
    
    prompt = f"Task: {task}"
    if context:
        prompt += f"\nContext: {context}"
    
    return gemini.run(prompt)
```

## 🐛 Troubleshooting

### Error de autenticación

```bash
# Re-autenticar
gemini logout
gemini login
```

### No responde

```bash
# Verificar estado
gemini doctor

# Reiniciar
gemini kill
gemini start
```

---

**Versión:** 1.0.0
**Última actualización:** 2026-02-05
