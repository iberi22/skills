---
name: hermes-gateway-troubleshooting
description: "Debug Hermes Gateway connectivity and platform integration issues — Telegram, Discord, WhatsApp. Covers Python env corruption, systemd service config, plugin adapter changes, and credential/auth failures."
version: 1.0.0
author: Hermes Agent
platforms: [linux]
---

# Hermes Gateway Troubleshooting

## When to Use

This skill covers diagnosing and fixing issues with the **Hermes Gateway** — the systemd service that connects Hermes Agent to messaging platforms (Telegram, Discord, WhatsApp, etc.).

**Triggers:**
- "Telegram no responde" / "bot is not responding"
- Gateway starts but blocks messages
- Gateway won't start / crashes immediately
- Platform integration stopped working after upgrade
- "ModuleNotFoundError" or "RuntimeError" in gateway logs
- Users are blocked as "unauthorized"

**DO NOT use for:** CLI-only issues, Hermes TUI rendering. Model/provider failures ("The model provider failed after retries") ARE covered here — see Layer 2.5.

## Diagnostic Approach — Layer by Layer

Always work from outermost to innermost layer:

1. **Is the process running?** → `systemctl --user status hermes-gateway.service`
2. **Are there error logs?** → `tail -100 ~/.hermes/logs/gateway.log`
3. **Is the service config correct?** → `systemctl --user cat hermes-gateway.service`
4. **Is the Python environment intact?** → Check uv tool site-packages
5. **Is the plugin/adapter code correct?** → Check adapter's handling of config values

---

## Layer 1 — Process Health

```bash
# Check if gateway is running
systemctl --user status hermes-gateway.service

# Check gateway PID and uptime
ps aux | grep "gateway run" | grep -v grep

# Restart if needed
systemctl --user restart hermes-gateway.service
```

## Layer 2 — Log Analysis

```bash
# Full recent log
tail -100 ~/.hermes/logs/gateway.log

# Only errors
grep -i "error\|traceback\|exception\|blocked\|unauthorized" ~/.hermes/logs/gateway.log

# Only Telegram activity
grep "\[Telegram\]" ~/.hermes/logs/gateway.log

# Follow in real time
tail -f ~/.hermes/logs/gateway.log
```

**Key log signatures:**

| Log line | Meaning | Likely Fix |
|----------|---------|------------|
| `Blocked unauthorized user X` | Allowlist check failed | Check `allow_from` format in config.yaml |
| `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'` | Python ABI mismatch | Check uv tool has correct site-packages |
| `Failed to initialize OpenAI client` | Python deps broken | Reinstall missing packages |
| `Connected to Telegram (polling mode)` | OK | — |
| `set_my_commands OK` | OK | — |
| `ImportError: cannot import name '<X>' from '<module>'` | Version skew — daemon running pre-update code against post-update files | See Layer 1.5 |

## Layer 2.4 — Version Skew: gateway process predating a code update

**Symptom:** every inbound message fails with `ImportError: cannot import name
'X' from 'Y'`, naming a symbol that plainly exists in the file on disk. Multiple
unrelated symbols fail at once, from modules that import fine interactively.

**Cause:** `hermes update` (or a git checkout of a new tag) replaces the source
tree while the long-running gateway keeps the OLD modules already imported in
memory. The process holds a mix of old code and new files: old call sites
import symbols the new layout moved or renamed. Nothing on disk is broken.

**Diagnose — compare process start time against the update, not against the file:**

```bash
# When did the running gateway start?
ps -o pid,lstart,etime -p "$(pgrep -f 'hermes_cli.main gateway run' | head -1)"

# When was the source last replaced?
stat -c '%y' ~/.hermes/hermes-agent/hermes_cli/providers.py
git -C ~/.hermes/hermes-agent log -1 --format='%ci %s'
```

If the process started BEFORE the update, version skew is the diagnosis.

**Confirm the disk side is actually healthy** — this is the step that separates
skew from a real breakage:

```bash
~/.hermes/hermes-agent/venv/bin/python -c "from hermes_cli.providers import LLAMACPP_ALIASES; print('imports OK')"
~/.hermes/hermes-agent/venv/bin/python -c "from tools.mcp_tool_common import mcp_server_enabled; print('imports OK')"
```

If those succeed, the fix is a restart, not a code change or reinstall:

```bash
systemctl --user restart hermes-gateway.service
```

**Verify by scoping errors to the new process, never by counting the whole log.**
`grep -c ImportError gateway.log` is cumulative and will show the historical
failures forever:

```bash
awk '/<restart timestamp>/,0' ~/.hermes/logs/gateway.log | grep -c ImportError   # must be 0
grep -E "telegram connected" ~/.hermes/logs/gateway.log | tail -1
```

Healthy reconnect looks like:
```
[Telegram] Telegram polling confirmed healthy: getUpdates progressing (generation 1)
gateway.run: ✓ telegram connected
```

**PITFALL — an update procedure that does not restart the gateway leaves the
system silently broken.** Any task that replaces Hermes source (update, tag
checkout, dependency sync) MUST end with the gateway restart plus the
post-restart connectivity check. Report the update as incomplete until
`✓ telegram connected` appears with a process start time newer than the update.
`hermes doctor` does NOT catch this — it inspects on-disk config, not the
running process's loaded modules.

## Layer 2.5 — Model/Provider Failure Diagnosis

When a session shows `⚠️ The model provider failed after retries. I kept raw provider details out of chat; check gateway logs for diagnostics.` — the raw details ARE in the logs, the chat message just hides them by design:

```bash
# errors.log (NOT gateway.log) carries per-attempt provider details
grep -i "api call failed" ~/.hermes/logs/errors.log | tail -20
grep -i "API call failed" ~/.hermes/logs/errors.log | grep "$(date +%F)" | tail -20   # solo hoy
```

Each failed attempt logs `error_type=...` + `summary=...` for the exact provider/model. Taxonomy:

| error_type | summary signal | Meaning | Action |
|---|---|---|---|
| `APIStatusError` | `HTTP 402 ... Insufficient Balance` | **Provider account balance exhausted (user-actionable)** | Top up the provider account / swap API key |
| `InternalServerError` | `HTTP 500: {"type":"Router.Unavailable","modelID":...}` | Provider router can't serve that model right now (transient) | Retry / wait / temporarily switch model in config.yaml |
| `InternalServerError` | `HTTP 500: Internal server error` | Provider-side outage | Retry with backoff (Hermes already retries 3x) |
| `APIConnectionError` | `Connection error.` | Provider unreachable (network/outage) | Retry; `curl -sI <base_url>`; if ALL providers fail it's network |

Workflow:
1. Get the timestamp of the failed turn from `agent.log`: `grep "model provider failed" ~/.hermes/logs/agent.log* | tail -5`
2. Grep `errors.log` around that timestamp for `API call failed` → read `error_type` + `summary`
3. Classify: **user-actionable** (402 balance, 401 bad key — the user must act) vs **transient** (500/connection — retry works, no user action)
4. Check whether the SAME error persists now (`tail errors.log`) — a one-off 500 vs a persistent `Router.Unavailable` are different answers
5. Also watch `agent.credential_pool: no available entries (all exhausted or empty)` — credential pool empty compounds the failure

Real case 2026-08-02/03: chat error caused first by `HTTP 402 Insufficient Balance` (opencode.ai account empty — user needed to top up), then the next day by `HTTP 500 Router.Unavailable modelID=deepseek-v4-flash` (provider-side, transient). Two different causes on consecutive days, both visible ONLY in errors.log.

## Layer 2.6 — Hermes Execution Health Audit (logs + entorno, verificado 2026-08-05)

Cuando el usuario pide "revisa los logs y todo alrededor para mejorar la ejecución de Hermes", la
auditoría NO es solo del gateway — es de todo el proceso. Pasos que producen hallazgos accionables:

```bash
# 1. Tamaño y rotación de logs — agent.log rota a ~5MB; errors.log a ~2MB
ls -la ~/.hermes/logs/
# 2. Tipos de error en agent.log (top tool failures del turno actual)
grep "WARNING" ~/.hermes/logs/agent.log | grep -oE "Tool [a-z_]+ returned error|Tool [a-z_]+: |agent\.[a-z_]+:" | sort | uniq -c | sort -rn | head -8
# 3. Caídas del gateway — gateway-exit-diag.log registra el traceback del exit code
tail -20 ~/.hermes/logs/gateway-exit-diag.log
journalctl --user -u hermes-gateway.service --since "3 days ago" | grep -cE "Started|Stopped"   # reinicios
# 4. Recursos: RAM del gateway y pico histórico (pico 28GB en esta máquina = posible OOM previo)
systemctl --user status hermes-gateway.service | grep -E "Active|Memory|Tasks"
# 5. state.db creciendo (sesiones/mensajes almacenados — 2.6GB/245K msgs en esta máquina)
ls -lh ~/.hermes/state.db
```

**Hallazgo recurrente — background curator ruidoso (34+ errores/turno):** el self-improvement
review corre después de cada turno e intenta parchear skills vía `skill_manage`, pero se le NEGA
sistemáticamente, llenando errors.log:
```
Refusing background curator patch for skill 'X': the skill records show it is not agent-created
(created_by=None). Manually authored skills are off-limits... / current SKILL.md content has not
been loaded in this review turn...
```
- **Causa**: skills escritas a mano (created_by=None en `.usage.json`) o el review no carga el
  SKILL.md antes de parchear → el guard las rechaza. No es un fallo del skill, es el review
  intentando auto-mejorar contenido que no le corresponde.
- **Impacto**: llamadas de API fallidas por turno + logs inundados. Si `errors.log` está lleno de
  este patrón, es la fuente de ruido #1.
- **Fix propuesto**: configurar `auxiliary.background_review` a un modelo barato explícito o
  desactivar el auto-parchado de skills manuales (dejar solo captura de memoria).
- **PITFALL de patch a skills manuales**: el mismo guard bloquea `skill_manage patch/edit` sobre
  skills con `created_by=None` (ej. skills creadas antes de que el registro `.usage.json`
  existiera, o cuyo create inicial falló y dejó el registro huérfano). No es un error de la
  operación — es el guard anti-curation. Workaround: si el skill está protegido pero el
  aprendizaje es importante, documentarlo en un skill editable (los que tienen
  `author: Hermes Agent` en frontmatter) o crear uno nuevo.

**gateway exit code 75 (verificado varias veces 2026-08-01..03):** `SystemExit(75)` en
`gateway/run.py:22936` — el gateway se cae con este código cuando el runner aborta. Diagnóstico
en `gateway-exit-diag.log` (traceback completo con PID + timestamp). Los reinicios frecuentes
(7 en 3 días) con pico de RAM de 28GB apuntan a OOM por delegaciones masivas o compresión de
contexto — vigilar memoria antes de asumir problema de código.

**state.db 2.6GB (245K mensajes, 3.4K sesiones):** cada `session_search` indexa todo el DB;
backups lentos. Mantenimiento: podar sesiones >60 días (exportar a Xavier antes) + `VACUUM`.

## Layer 1.5 — Version Skew After an In-Place Update

The highest-yield check when a gateway breaks right after `hermes update`: the
running process holds the OLD code in memory while the files on disk are NEW.
Every inbound message then dies on an import that no longer resolves.

Signature in `~/.hermes/logs/gateway.log`:

```
ImportError: cannot import name 'LLAMACPP_ALIASES' from 'hermes_cli.providers'
ImportError: cannot import name 'mcp_server_enabled' from 'tools.mcp_tool_common'
```

Read as a module-move in the new release, not as a broken install.

**Triage — compare the process start time against the file mtime:**

```bash
ps -o pid,lstart,etime -p $(pgrep -f "hermes_cli.main gateway run" | head -1)
stat -c '%y' ~/.hermes/hermes-agent/hermes_cli/providers.py
```

Process started hours BEFORE the update ⇒ skew. Confirm the symbol is fine with
current code before touching anything:

```bash
~/.hermes/hermes-agent/venv/bin/python -c \
  "from hermes_cli.providers import LLAMACPP_ALIASES; print('imports OK')"
```

If that succeeds, the fix is a restart and nothing else:

```bash
systemctl --user restart hermes-gateway.service
```

Then verify the NEW process, and prove the skew is gone:

```bash
ps -o lstart= -p $(pgrep -f "hermes_cli.main gateway run" | head -1)   # fresh
grep -a "✓ telegram connected" ~/.hermes/logs/gateway.log | tail -1
# count errors only AFTER the new start time — a whole-file count stays non-zero forever
awk '/<new start timestamp>/,0' ~/.hermes/logs/gateway.log | grep -c ImportError   # expect 0
```

**PITFALL:** `grep -c ImportError gateway.log` is cumulative and never returns 0
after an update. Always scope the count to the region after the restart, or you
will report a resolved fault as a live one.

**PITFALL:** `gateway.log` may be detected as a binary file, making `grep` print
`coincidencia en fichero binario` and silently match nothing. Add `-a` (as
above) whenever you grep a log that has grown large or contains non-UTF8 bytes.

**Prevent it:** stop the gateway before updating, or restart it immediately
after, as one atomic task. An update that leaves a long-lived daemon running
against replaced source will break every platform adapter until that restart.

## Layer 3 — Systemd Service Config

```bash
# View the full service unit
systemctl --user cat hermes-gateway.service

# Check for these critical fields:
# - WorkingDirectory: must point to CURRENT python version's site-packages
# - Environment=PATH: must reference correct python version
# - ExecStart: correct python binary path
```

### Common Service File Issues

**WorkingDirectory pointing to old Python version:**
```
# WRONG (stale python3.13):
WorkingDirectory=/home/user/.local/share/uv/tools/hermes-agent/lib/python3.13/site-packages

# RIGHT (current python3.14):
WorkingDirectory=/home/user/.local/share/uv/tools/hermes-agent/lib/python3.14/site-packages
```

### Fix
```bash
# Edit the service file
nano ~/.config/systemd/user/hermes-gateway.service
# Then:
systemctl --user daemon-reload
systemctl --user restart hermes-gateway.service
```

## Layer 4 — Python Environment (uv Tool)

### Detect Dual-Version Site-Packages

When uv upgrades the hermetic Python inside a tool, old version-specific site-packages can linger and cause import shadowing (Python resolves modules from the stale directory first).

```bash
# Check which python versions exist in the uv tool
ls ~/.local/share/uv/tools/hermes-agent/lib/

# Check actual python version of the tool's binary
~/.local/share/uv/tools/hermes-agent/bin/python3 --version

# If you see python3.13/ AND python3.14/, the old one is stale
# Fix: ensure systemd WorkingDirectory points to the CURRENT version
# Fix: install missing packages into the current version's site-packages
```

**Root cause:** Python adds the current working directory to `sys.path` as `''` (empty string). If `WorkingDirectory` points to an old pythonX.Y/site-packages, Python finds packages there first — even when `sys.path` doesn't explicitly include that directory.

### Install Missing Packages

When the correct site-packages directory lacks packages that only exist in a stale version:

```bash
uv pip install --python ~/.local/share/uv/tools/hermes-agent/bin/python3 \
  pydantic pydantic-core \
  python-telegram-bot \
  anthropic openai \
  rich tenacity httpx[socks] edge-tts \
  certifi python-dotenv fire pyyaml \
  jinja2 psutil tabulate termcolor wcwidth
```

### Verify
```bash
~/.local/share/uv/tools/hermes-agent/bin/python3 -c "
import pydantic_core
import pydantic
import telegram
import openai
print('pydantic_core:', pydantic_core.__version__)
print('pydantic:', pydantic.__version__)
print('ALL OK')
"
```

## Layer 5 — Plugin/Adapter Config

### Telegram `allow_from` Format

Hermes 0.19.0+ uses a plugin-based Telegram adapter (`plugins/platforms/telegram/`). The `allow_from` key is read from `config.yaml`'s `telegram:` section and bridged into the plugin's `extra` dict via `gateway/config.py` (~line 1472-1473 → `extra.update(bridged)` at ~line 1524).

**Critical:** The adapter iterates over `allow_from` to build an allowed set. Four formats can arrive:

| YAML config | Python type | Iteration behavior |
|---|---|---|
| `allow_from: [2076598024]` | `list[int]` | ✅ One iteration per ID |
| `allow_from:\n  - '2076598024'` | `list[str]` | ✅ One iteration per ID |
| `allow_from: 2076598024` | `int` | ❌ `TypeError: 'int' object is not iterable` (traceback at `adapter.py:1019`) |
| `allow_from: '2076598024'` | `str` | ❌ Iterates character-by-character (`'2'`, `'0'`, ...) |
| `allow_from: '["2076598024"]'` | `str` | ❌ Produces literal set `{'["2076598024"]'}` — never matches |

The last row is the **`hermes config set` pitfall**: `hermes config set telegram.allow_from '[id]'` stores the value as a **literal quoted string** `'["id"]'` in YAML, **NOT** as a native YAML list. Always edit `config.yaml` directly or use `sed`/Python to write the YAML list format properly.

**Preferred config format:**
```yaml
telegram:
  allow_from:
    - '2076598024'       # YAML list with one quoted string per user ID
```

Multiple users:
```yaml
telegram:
  allow_from:
    - '2076598024'
    - '1234567890'
```

**Adapter patch** (shown with line numbers from `adapter.py:1016-1020`):

The original code assumes `allow_from` is always a list:
```python
# Original (broken for int/str):
adapter_allow_from = self.config.extra.get("allow_from")
if adapter_allow_from is not None:
    allowed = {str(u).strip() for u in adapter_allow_from if str(u).strip()}
    return user_id in allowed or "*" in allowed
```

Defensive fix — wrap non-list values before iterating:
```python
adapter_allow_from = self.config.extra.get("allow_from")
if adapter_allow_from is not None:
    if isinstance(adapter_allow_from, str):
        adapter_allow_from = [adapter_allow_from]       # str → list
    elif not isinstance(adapter_allow_from, (list, tuple)):
        adapter_allow_from = [str(adapter_allow_from)]  # int/float → list
    allowed = {str(u).strip() for u in adapter_allow_from if str(u).strip()}
    return str(user_id) in allowed or "*" in allowed
```

**Key details:**
- Use `str(user_id)` for comparison — Telegram may pass `user_id` as int while the allowed set contains strings
- After patching `adapter.py`, **restart the gateway** via `systemctl --user restart hermes-gateway.service` — the code change is hot only after restart
- The config → plugin bridging happens in `gateway/config.py` during gateway startup; changes to `config.yaml` only take effect after restart
- If you still get errors after fixing config, check that `systemctl --user daemon-reload` ran if you edited the service file

### Config → Plugin Bridging

The gateway config loader (`gateway/config.py`) reads top-level platform blocks from `config.yaml` and bridges specific keys into the plugin's `extra` dict. Bridged keys include:

`allow_from`, `allowed_chats`, `group_allowed_chats`, `allowed_topics`, `require_mention`, `dm_policy`, `group_policy`, `gateway_restart_notification`, `typing_indicator`, `channel_prompts`, `free_response_channels`, `mention_patterns`

## Full Debugging Sequence

When Telegram (or any platform) stops responding:

```
1. systemctl --user status hermes-gateway.service
   → Is it running? If not, start it.

2. tail -50 ~/.hermes/logs/gateway.log | grep -E "ERROR|Traceback|Blocked|unauthorized"
   → What errors exist?

3. If `TypeError: 'int' object is not iterable` at `adapter.py:1019`:
   → `allow_from` in config.yaml is an unquoted integer parsed by YAML as `int`
   → Fix: change to proper YAML list format
   → **WARNING:** `hermes config set telegram.allow_from '[id]'` stores a JSON-stringified
     literal string `'["id"]'`, NOT a YAML list. Edit config.yaml directly.
   → If the adapter doesn't handle all formats (str/int/list), patch adapter.py
   → **Always restart gateway after adapter patch** (`systemctl --user restart hermes-gateway.service`)

4. If "Blocked unauthorized user YOUR_ID":
   → Check telegram.allow_from format in config.yaml (same fix as above)
   → Ensure the user_id in config matches the Telegram user ID exactly

5. If pydantic_core ModuleNotFoundError:
   → Check uv tool python version vs site-packages ABI
   → Install missing packages for current python version

6. If code loads from wrong site-packages:
   → Check systemd service WorkingDirectory
   → Update to point to current python version

7. Restart gateway and test.
```

## Verification

```bash
# Send a test message via Telegram and check logs
grep -E "inbound message|Processed message|Agent error" ~/.hermes/logs/gateway.log | tail -5
```
