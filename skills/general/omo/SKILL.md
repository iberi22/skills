---
name: omo
description: Omo CLI - AI agent for software development. Alternative CLI agent for code generation and multilingual tasks.
version: "1.0.0"
updated: "2026-04-23"
author: swal
license: MIT
---

# Omo CLI Skill

> Omo AI - Agente CLI para desarrollo de software.

## 📦 Instalación

```bash
# Instalar Omo CLI
npm install -g @omo/cli

# Verificar
omo --version
```

## ⚙️ Configuración

```bash
# Login
omo login --api-key YOUR_KEY

# Configurar preferencias
omo config set model omo-pro
omo config set sandbox true
```

## 🚀 Uso

```python
from skills.omo.omo_client import OmoCLI

omo = OmoCLI()

# Ejecutar tarea
result = omo.run("Implement a login system")

# Modo sandbox (seguro)
result = omo.run("Test this code", sandbox=True)

# Con archivo
result = omo.run_file("path/to/task.md")
```

## 📁 Estructura

```
skills/omo/
├── SKILL.md           # Este archivo
└── omo_client.py      # Cliente Python
```

## 🔗 Integración

```python
def handle_dev_task(task: str):
    omo = OmoCLI()
    return omo.run(task, sandbox=True)
```

---

**Versión:** 1.0.0
**Última actualización:** 2026-02-05
