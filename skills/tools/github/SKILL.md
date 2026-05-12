---
id: github
name: github
category: tools
tags:
  - github
goals:
  - "This skill documents how to use `gh` CLI for GitHub operations in SWAL projects."
authors:
  - Brahyan Belalcazar
---

# GitHub CLI Skill — SWAL

## Overview

This skill documents how to use `gh` CLI for GitHub operations in SWAL projects.

## Authentication

### Token-Based Auth (RECOMMENDED for automated scripts)

**⚠️ IMPORTANT:** When running `gh` in exec sessions (OpenClaw context), tokens don't persist between sessions. The token must be provided explicitly or stored in a persistent manner.

```powershell
# Method 1: Set GH_TOKEN environment variable (session-scoped)
$env:GH_TOKEN = "gho_your_token_here"
gh auth login -h github.com --with-token

# Method 2: Use --with-token directly (PowerShell)
$token | gh auth login -h github.com --with-token

# Method 3: Use insecure storage (saves to plain text - NOT recommended for production)
gh auth login -h github.com --insecure-storage
```

### Why tokens don't persist

- `gh` on Windows stores tokens in **Windows Credential Manager** under your user profile
- exec sessions in OpenClaw may run as **SYSTEM** or different user context
- Solution: Always provide token explicitly OR use `--insecure-storage`

### Getting a Token

1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Required scopes: `repo`, `read:org`, `workflow`
4. Copy token (starts with `ghp_` or `gho_`)

## Common Commands

### Repository Operations

```bash
# Clone a repo
git clone https://github.com/iberi22/repo-name.git

# Fork and clone in one command
gh repo fork owner/repo --clone

# Create repo from current directory
gh repo create owner/repo-name --public --source=. --push

# List repos for org/user
gh repo list iberi22 --limit 10

# View repo details
gh repo view owner/repo

# View PRs
gh pr list
gh pr view 123
```

### Authentication Check

```bash
# Check auth status
gh auth status

# Check who you're logged in as
gh api user
```

### Workflows

```bash
# Trigger workflow manually
gh workflow run workflow-name --ref branch

# View workflow runs
gh run list

# Watch a run
gh run watch
```

## SWAL Convention

| Item | Value |
|------|-------|
| **Repo Principal** | `iberi22/*` (NOT southwest-ai-labs) |
| **Carpeta Proyectos** | `E:\scripts-python` |
| **GitHub Token** | Stored in `GH_TOKEN` env var |

## Troubleshooting

### "Token is invalid" error

This happens when:
1. Token expired or was revoked → Generate new token
2. Running in different user context → Use `$env:GH_TOKEN` explicitly
3. Credential Manager issue → Use `--insecure-storage` flag

### "Repository not found" after push

The remote repo doesn't exist on GitHub yet:
```bash
gh repo create owner/repo-name --public --source=. --push
```

### Fork failed - not an organization

`gh repo fork` with `--org` only works for orgs, not user accounts:
```bash
# For user account (iberi22 is a user, not org)
gh repo fork owner/repo --clone

# Not: gh repo fork owner/repo --org iberi22
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GH_TOKEN` | GitHub Personal Access Token |
| `GITHUB_TOKEN` | Alias for GH_TOKEN |
