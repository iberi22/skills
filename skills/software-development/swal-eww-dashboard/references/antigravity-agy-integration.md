# Antigravity (AGY) CLI Integration — SWAL Dashboard

Session: 2026-05-22 — Integrating Google AI Pro CLI (`agy`) as a 4th agent badge in the SWAL EWW dashboard.

## Installation on NixOS

AGY is distributed as a generic Linux binary, not a Nix package. It fails with missing `.so` libraries on NixOS.

**Wrapper with `steam-run`:**
```bash
# Download binary (official or trusted source)
curl -L -o ~/.local/bin/agy.bin <url>
chmod +x ~/.local/bin/agy.bin

# Create wrapper
cat > ~/.local/bin/agy << 'EOF'
#!/usr/bin/env bash
exec steam-run "$HOME/.local/bin/agy.bin" "$@"
EOF
chmod +x ~/.local/bin/agy
```

Requires `nixpkgs#steam-run` installed (usually present on gaming-enabled NixOS setups).

## Authentication (OAuth)

AGY has **no `login` or `auth` subcommand**. It uses silent OAuth triggered automatically on first use.

**Auth flow:**
1. Run any command that needs API access (e.g., `agy --print "hello"`)
2. If not authenticated, AGY prints a Google OAuth URL
3. User opens the URL in a browser, completes Google sign-in (must have Google AI Pro subscription)
4. Google redirects with an authorization code
5. The CLI waits for the callback (default timeout: 30s)

**Token storage:**
- File: `~/.gemini/antigravity-cli/antigravity-oauth-token`
- Format: JSON with `access_token`, `refresh_token`, `expiry`
- Also mirrored in: `~/.gemini/oauth_creds.json`

**Verify auth:**
```bash
# Should return a chat response, not "Authentication required"
agy --print "hello world"

# Check token file exists and is non-empty
[[ -s ~/.gemini/antigravity-cli/antigravity-oauth-token ]] && echo "Authenticated"
```

**Token refresh:** AGY handles refresh automatically via the stored `refresh_token`. If auth fails after working before, check the token file hasn't been corrupted or deleted.

## CLI Arguments

```
agy --help
  --print, -p         Run a single prompt non-interactively and print response
  --prompt-interactive, -i   Run initial prompt then enter interactive session
  --continue, -c      Continue most recent conversation
  --conversation      Resume a previous conversation by ID
  --add-dir           Add directory to workspace (repeatable)
  --dangerously-skip-permissions   Auto-approve all tool permissions
  --sandbox           Run in sandbox with terminal restrictions

Subcommands:
  install             Configure PATH and shell settings
  plugin/plugins      Manage plugins (install, uninstall, list, enable, disable)
  update              Update CLI
  changelog           Show release notes
  help                Show help for subcommands
```

**No `login`, `auth`, `logout`, or `status` subcommands exist.**

## Dashboard Integration

AGY was added as badge "AGY" between "COD" and "GEM" in the dashboard.

**Process detection:** `pgrep -f "agy.bin"` (the real binary name, since the wrapper is a shell script).

**Status script example:**
```bash
# ai_status_json.sh
agy)     pgrep -f "agy.bin" >/dev/null 2>&1 && echo "Active" || echo "Standby" ;;
```

**Model label:** "AGY Pro" (represents Google AI Pro subscription tier).

## Logs

AGY logs are written to:
- `~/.gemini/antigravity-cli/log/cli-<timestamp>.log`
- Symlink: `~/.gemini/antigravity-cli/cli.log` → latest log file

Common log lines when not authenticated:
```
error getting token source: You are not logged into Antigravity.
Failed to load token from keyring, falling back to file
printmode.go: silent auth failed, triggering OAuth
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `agy: command not found` | Wrapper not in PATH | Ensure `~/.local/bin` is in PATH; run `agy install` to append to shell profiles |
| `Authentication required` | Token missing or expired | Complete OAuth flow again by running `agy --print "test"` |
| Binary crashes with `.so` errors | NixOS missing libraries | Use `steam-run` wrapper |
| `consumerOAuth: starting OAuth flow` then timeout | Browser didn't complete callback | Ensure browser can reach `https://antigravity.google/oauth-callback` |
