---
id: codex
name: codex
category: tools
tags:
  - codex
goals:
  - "Use Codex CLI for code generation, review, and autonomous coding tasks. Use this skill when you need OpenAI Codex to perform tasks."
authors:
  - Brahyan Belalcazar
---

# Codex CLI Skill

> OpenAI Codex CLI - AI-powered code generation, editing, and autonomous coding.

## 🎯 When to Use This Skill

- Code generation from specifications
- Autonomous code editing and refactoring
- Code review and analysis
- Running Codex as a sub-agent for complex tasks
- Bug detection and fixing

## ⚡ Quick Start

### Basic Usage (Headless)

```bash
# Generate code from a prompt
codex "Create a Python function to calculate fibonacci"

# Non-interactive mode
codex exec "Your task here"

# Review code
codex review --file src/main.rs

# Specific model
codex -m o3 "Your prompt"
```

### Available Commands

| Command | Description |
|---------|-------------|
| `codex --help` | Show all options |
| `codex exec "task"` | Run task non-interactively |
| `codex review` | Code review mode |
| `codex -m o3 "task"` | Use o3 model |
| `codex -m o4 "task"` | Use o4 model |
| `codex --version` | Show version |

### Models

- `o3` (default for complex tasks)
- `o4-mini`
- `codex-sonnet-4`

## 🔧 Advanced Usage

### Sandbox Modes

```bash
# Read-only (safe)
codex -s read-only "Review this code"

# Workspace write
codex -s workspace-write "Fix the bug"

# Full access (dangerous)
codex -s danger-full-access "Your task"
```

### Approval Policies

```bash
# Ask on failure
codex -a on-failure "Your task"

# Ask on request
codex -a on-request "Your task"

# Full auto
codex --full-auto "Your task"
```

### Environment Variables

```bash
# Set API key
$env:OPENAI_API_KEY="sk-..."

# Enable web search
codex --search "Your prompt"
```

## 📋 Integration with OpenClaw

```python
import subprocess

def run_codex(prompt: str, model: str = "o3", 
              sandbox: str = "workspace-write") -> str:
    """Run Codex headlessly and return the result."""
    cmd = [
        "codex", "-p", prompt,
        "-m", model,
        "-s", sandbox,
        "--dangerously-bypass-approvals-and-sandbox"
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300
    )
    
    return result.stdout if result.returncode == 0 else result.stderr
```

## 🎨 Examples

### Code Generation

```bash
codex exec "Create a Rust struct for a trading order with fields: symbol, side, quantity, price"
```

### Bug Fix

```bash
codex exec "Fix the panic in src/trading.rs when balance is zero"
```

### Code Review

```bash
codex review --file backend/src/main.rs
```

### Refactoring

```bash
codex exec "Refactor this function to use async/await" --file src/old.rs
```

## ⚠️ Important Notes

- Codex requires authentication via `codex login` or `OPENAI_API_KEY`
- Use `exec` for headless operation (no TTY required)
- Sandbox mode controls what Codex can do
- Default model is `o3` for complex reasoning

## 🔗 Resources

- [Codex CLI Docs](https://developers.openai.com/codex/cli)
- [Agent Skills](https://developers.openai.com/codex/skills)

---

**Version:** 2.0.0  
**Last Updated:** 2026-02-17