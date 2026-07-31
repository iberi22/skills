---
id: qwen
name: qwen
category: tools
tags:
  - qwen
goals:
  - "> Qwen CLI integration for Alibaba's Qwen AI models."
authors:
  - Brahyan Belalcazar
---

# Qwen CLI Skill

> Qwen CLI integration for Alibaba's Qwen AI models.

## 📦 Instalación

```bash
# Instalar Qwen CLI
pip install qwen-cli

# O via npm
npm install -g @qwen/qwen-cli

# Verificar
qwen --version
```

## ⚙️ Configuración

```bash
# Login con Alibaba Cloud
qwen login --api-key YOUR_API_KEY

# Configurar endpoint
qwen config set endpoint https://api.qwen.ai/v1

# Verificar
qwen config list
```

## 🚀 Uso

### Desde OpenClaw

```python
from skills.qwen.qwen_client import QwenCLI

qwen = QwenCLI()

# Basic
result = qwen.run("Write a Python function")
print(result)

# Con archivo
result = qwen.analyze_code("src/module.py")

# Chat
chat = qwen.chat_session("debug")
response = chat.send("Help me fix this bug")
```

## 📁 Estructura

```
skills/qwen/
├── SKILL.md            # Este archivo
├── qwen_client.py      # Cliente Python
└── scripts/
    └── qwen.ps1        # PowerShell wrapper
```

## 🔧 API Reference

### QwenCLI

```python
from qwen_client import QwenCLI

# Basic
cli = QwenCLI()
result = cli.run("Your prompt")

# Opciones
result = cli.run(
    prompt="Explain this code",
    model="qwen-turbo",
    temperature=0.7,
    max_tokens=4000
)

# Archivos
result = cli.analyze_file("src/module.py")
result = cli.generate_code("Create a REST API", framework="fastapi")
```

## 🎯 Casos de Uso

| Task | Comando |
|------|---------|
| Code generation | `qwen run "Create a login API"` |
| Translation | `qwen run "Translate this to Spanish"` |
| Documentation | `qwen run "Generate docs for this code"` |
| Debug | `qwen run "Find the bug"` |

## 🔗 Integración

```python
def handle_coding_task(task: str):
    """Delegar tarea de código a Qwen."""
    qwen = QwenCLI()
    return qwen.run(task)
```

---

**Versión:** 1.0.0
**Última actualización:** 2026-02-05
