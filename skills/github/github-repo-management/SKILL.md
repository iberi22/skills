---
name: github-repo-management
description: "Clone/create/fork repos; manage remotes, releases."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Repositories, Git, Releases, Secrets, Configuration]
    related_skills: [github-auth, github-pr-workflow, github-issues]
---

# GitHub Repository Management

Create, clone, fork, configure, and manage GitHub repositories. Each section shows `gh` first, then the `git` + `curl` fallback.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)

## First Rule: Use `gh` Before `curl` or Filesystem Search

When you need to access a GitHub repo — especially one the user mentioned by name — **try `gh` first**:

```bash
gh repo view owner/repo-name
```

`gh` handles authentication automatically (token from `gh auth login`), works with **public AND private repos**, and returns immediately. By contrast:
- `curl` + GitHub API **fails on private repos** with a 404 unless you inject a token manually
- Searching the local filesystem only finds repos you've already cloned
- Session search is for context, not for finding repos

**Decision order:**

1. `gh repo view owner/repo` → fastest, handles auth, works on private repos
2. `gh repo list` → list your own repos
3. `gh search repos "keywords"` → search across GitHub
4. Only then search local disk or session history (for repos that were cloned or worked on before)

**To check available commands at any time:**

```bash
gh --help          # all commands
gh <command> --help # specific command, e.g. gh repo --help
```

**Common `gh` commands for repo discovery:**

```bash
gh repo view owner/repo                           # basic info (description + README)
gh repo view owner/repo --json name,description,url,visibility,defaultBranchRef,languages,repositoryTopics  # structured info
gh repo list <your-user> --limit 50                   # list all repos for a user
gh repo list <your-user> --json name,description,visibility,updatedAt  # structured list
gh search repos "keyword" --owner <your-user>          # search within user
```

### Setup

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f .env ] && grep -q "^GITHUB_TOKEN=" .env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" .env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi

# Get your GitHub username (needed for several operations)
if [ "$AUTH" = "gh" ]; then
  GH_USER=$(gh api user --jq '.login')
else
  GH_USER=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | python3 -c "import sys,json; print(json.load(sys.stdin)['login'])")
fi
```

If you're inside a repo already:

```bash
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## 1. Cloning Repositories

Cloning is pure `git` — works identically either way:

```bash
# Clone via HTTPS (works with credential helper or token-embedded URL)
git clone https://github.com/owner/repo-name.git

# Clone into a specific directory
git clone https://github.com/owner/repo-name.git ./my-local-dir

# Shallow clone (faster for large repos)
git clone --depth 1 https://github.com/owner/repo-name.git

# Clone a specific branch
git clone --branch develop https://github.com/owner/repo-name.git

# Clone via SSH (if SSH is configured)
git clone git@github.com:owner/repo-name.git
```

**With gh (shorthand):**

```bash
gh repo clone owner/repo-name
gh repo clone owner/repo-name -- --depth 1
```

### Post-Hoc Git Setup (source files + existing remote, no .git)

When you have source files that were manually copied (no `.git/` directory) but the repo already exists on GitHub:

```bash
cd /path/to/project

# 1. Initialize git and point to the right remote
git init
git remote add origin https://github.com/owner/repo.git

# 2. Fetch remote state
git fetch origin

# 3. Reset to origin/main to stage the diff between local files and remote
git reset origin/main

# 4. Restore any tracked files that were missing from the copy
#    (like .gitignore, .github/ workflows, .gitcore/)
git checkout origin/main -- .gitignore .github/ 2>/dev/null || true

# 5. Now add and commit your changes on top
git add -A
git commit -m "sync: local state"

# 6. Push
git push origin main
```

**Pitfall:** The `git checkout origin/main -- file` approach restores files from the remote. If local had intentional changes to those files, the remote version wins. Review with `git diff --cached` before committing.

### Auth: embedding `gh` token in remote URLs

When `git push` on an HTTPS remote fails with "could not read Username" (no credential helper configured), embed the `gh` auth token directly:

```bash
# One-liner: embed gh token in remote URL
git remote set-url origin https://username:$(gh auth token)@github.com/owner/repo.git

# Or configure gh as git credential helper (persistent)
gh auth setup-git
```

**Pitfalls:**
- The token-embedded URL is stored in `.git/config` — avoid committing repos with embedded tokens if the repo is shared or public.
- `gh auth token` returns the current token. If the token is revoked or expires, the URL breaks. Prefer `gh auth setup-git` for persistent setups.

## 2. Creating Repositories

**With gh:**

```bash
# Create a public repo and clone it
gh repo create my-new-project --public --clone

# Private, with description and license
gh repo create my-new-project --private --description "A useful tool" --license MIT --clone

# Under an organization
gh repo create my-org/my-new-project --public --clone

# From existing local directory
cd /path/to/existing/project
gh repo create my-project --source . --public --push
```

**With git + curl:**

```bash
# Create the remote repo via API
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{
    "name": "my-new-project",
    "description": "A useful tool",
    "private": false,
    "auto_init": true,
    "license_template": "mit"
  }'

# Clone it
git clone https://github.com/$GH_USER/my-new-project.git
cd my-new-project

# -- OR -- push an existing local directory to the new repo
cd /path/to/existing/project
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/$GH_USER/my-new-project.git
git push -u origin main
```

To create under an organization:

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/orgs/my-org/repos \
  -d '{"name": "my-new-project", "private": false}'
```

### From a Template

**With gh:**

```bash
gh repo create my-new-app --template owner/template-repo --public --clone
```

**With curl:**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/template-repo/generate \
  -d '{"owner": "'"$GH_USER"'", "name": "my-new-app", "private": false}'
```

## 3. Forking Repositories

**With gh:**

```bash
gh repo fork owner/repo-name --clone
```

**With git + curl:**

```bash
# Create the fork via API
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo-name/forks

# Wait a moment for GitHub to create it, then clone
sleep 3
git clone https://github.com/$GH_USER/repo-name.git
cd repo-name

# Add the original repo as "upstream" remote
git remote add upstream https://github.com/owner/repo-name.git
```

### Keeping a Fork in Sync

```bash
# Pure git — works everywhere
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

**With gh (shortcut):**

```bash
gh repo sync $GH_USER/repo-name
```

## 4. Repository Information

**With gh (structured JSON — best for programmatic use):**

```bash
# View repo details with select fields
gh repo view owner/repo-name --json name,description,url,visibility,defaultBranchRef,languages,repositoryTopics

# Common JSON fields for repo views:
# name, description, url, visibility (PUBLIC/PRIVATE),
# defaultBranchRef { name }, languages [ { node { name }, size } ],
# repositoryTopics, createdAt, updatedAt, pushedAt,
# isArchived, isFork, isEmpty, diskUsage, stargazerCount,
# licenseInfo { name }, primaryLanguage { name },
# viewerCanAdminister, viewerPermission

# List repos with structured output
gh repo list <your-user> --json name,description,url,visibility,updatedAt --limit 50

# Script-friendly: pipe to jq or python3
gh repo view owner/repo-name --json name,visibility,defaultBranchRef | jq .
```

**With curl:**

```bash
# View repo details
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO \
  | python3 -c "
import sys, json
r = json.load(sys.stdin)
print(f\"Name: {r['full_name']}\")
print(f\"Description: {r['description']}\")
print(f\"Stars: {r['stargazers_count']}  Forks: {r['forks_count']}\")
print(f\"Default branch: {r['default_branch']}\")
print(f\"Language: {r['language']}\")"

# List your repos
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/user/repos?per_page=20&sort=updated" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin):
    vis = 'private' if r['private'] else 'public'
    print(f\"  {r['full_name']:40}  {vis:8}  {r.get('language', ''):10}  ★{r['stargazers_count']}\")"

# Search repos
curl -s \
  "https://api.github.com/search/repositories?q=machine+learning+language:python&sort=stars&per_page=10" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin)['items']:
    print(f\"  {r['full_name']:40}  ★{r['stargazers_count']:6}  {r['description'][:60] if r['description'] else ''}\")"
```

## 5. Repository Settings

**With gh:**

```bash
gh repo edit --description "Updated description" --visibility public
gh repo edit --enable-wiki=false --enable-issues=true
gh repo edit --default-branch main
gh repo edit --add-topic "machine-learning,python"
gh repo edit --enable-auto-merge
```

**With curl:**

```bash
curl -s -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO \
  -d '{
    "description": "Updated description",
    "has_wiki": false,
    "has_issues": true,
    "allow_auto_merge": true
  }'

# Update topics
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.mercy-preview+json" \
  https://api.github.com/repos/$OWNER/$REPO/topics \
  -d '{"names": ["machine-learning", "python", "automation"]}'
```

## 6. Branch Protection

```bash
# View current protection
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection

# Set up branch protection
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection \
  -d '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["ci/test", "ci/lint"]
    },
    "enforce_admins": false,
    "required_pull_request_reviews": {
      "required_approving_review_count": 1
    },
    "restrictions": null
  }'
```

## 7. Secrets Management (GitHub Actions)

**With gh:**

```bash
gh secret set API_KEY --body "your-secret-value"
gh secret set SSH_KEY < ~/.ssh/id_rsa
gh secret list
gh secret delete API_KEY
```

**With curl:**

Secrets require encryption with the repo's public key — more involved via API:

```bash
# Get the repo's public key for encrypting secrets
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets/public-key

# Encrypt and set (requires Python with PyNaCl)
python3 -c "
from base64 import b64encode
from nacl import encoding, public
import json, sys

# Get the public key
key_id = '<key_id_from_above>'
public_key = '<base64_key_from_above>'

# Encrypt
sealed = public.SealedBox(
    public.PublicKey(public_key.encode('utf-8'), encoding.Base64Encoder)
).encrypt('your-secret-value'.encode('utf-8'))
print(json.dumps({
    'encrypted_value': b64encode(sealed).decode('utf-8'),
    'key_id': key_id
}))"

# Then PUT the encrypted secret
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets/API_KEY \
  -d '<output from python script above>'

# List secrets (names only, values hidden)
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/secrets \
  | python3 -c "
import sys, json
for s in json.load(sys.stdin)['secrets']:
    print(f\"  {s['name']:30}  updated: {s['updated_at']}\")"
```

Note: For secrets, `gh secret set` is dramatically simpler. If setting secrets is needed and `gh` isn't available, recommend installing it for just that operation.

## 8. Releases

**With gh:**

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release create v2.0.0-rc1 --draft --prerelease --generate-notes
gh release create v1.0.0 ./dist/binary --title "v1.0.0" --notes "Release notes"
gh release create v1.0.0 --title "v1.0.0" --notes "## Release Notes" --verify-tag
gh release list
gh release download v1.0.0 --dir ./downloads
gh release view v1.0.0 --json body,createdAt,name,tagName
gh release edit v1.0.0 --title "Updated Title" --notes "Updated body"
```

### Tag Management

#### Moving a release tag to current HEAD

When a tag was created at an old commit and needs to point to `HEAD` (common during stabilization sprints where the tag predates the final commits):

```bash
# 1. Delete old local tag
git tag -d v1.0.0

# 2. Create new tag at HEAD
git tag v1.0.0 HEAD -m "v1.0.0: description"

# 3. Force push tag to remote (overwrites the old one)
git push origin v1.0.0 --force

# 4. Verify the tag on remote points to the right commit
git ls-remote --tags origin v1.0.0

# 5a. If release doesn't exist yet — create it
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes" --verify-tag

# 5b. If release already exists — edit it
gh release edit v1.0.0 --title "v1.0.0" --notes "Updated release notes"
```

**Pitfalls:**
- Force-pushing a tag (`git push --force`) is destructive — anyone who pulled the old tag gets a mismatch. Safe on personal/private repos where you control the consumers; avoid on public repos with external contributors.
- `gh release create --verify-tag` ensures the tag exists on the remote before creating the release. Without it, the release is created even with a missing tag.
- If `gh release create` returns "Release.tag_name already exists", the release was already created under that tag name. Use `gh release edit` instead.
- `--verify-tag` only checks the tag exists, not that it matches local HEAD. Verify with `git ls-remote --tags` separately.

**With curl:**

```bash
# Create a release
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/releases \
  -d '{
    "tag_name": "v1.0.0",
    "name": "v1.0.0",
    "body": "## Changelog\n- Feature A\n- Bug fix B",
    "draft": false,
    "prerelease": false,
    "generate_release_notes": true
  }'

# List releases
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/releases \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin):
    tag = r.get('tag_name', 'no tag')
    print(f\"  {tag:15}  {r['name']:30}  {'draft' if r['draft'] else 'published'}\")"

# Upload a release asset (binary file)
RELEASE_ID=<id_from_create_response>
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  "https://uploads.github.com/repos/$OWNER/$REPO/releases/$RELEASE_ID/assets?name=binary-amd64" \
  --data-binary @./dist/binary-amd64
```

## 9. GitHub Actions Workflows

**With gh:**

```bash
gh workflow list
gh run list --limit 10
gh run view <RUN_ID>
gh run view <RUN_ID> --log-failed
gh run rerun <RUN_ID>
gh run rerun <RUN_ID> --failed
gh workflow run ci.yml --ref main
gh workflow run deploy.yml -f environment=staging
```

**With curl:**

```bash
# List workflows
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows \
  | python3 -c "
import sys, json
for w in json.load(sys.stdin)['workflows']:
    print(f\"  {w['id']:10}  {w['name']:30}  {w['state']}\")"

# List recent runs
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?per_page=10" \
  | python3 -c "
import sys, json
for r in json.load(sys.stdin)['workflow_runs']:
    print(f\"  Run {r['id']}  {r['name']:30}  {r['conclusion'] or r['status']}\")"

# Download failed run logs
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs

# Re-run a failed workflow
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun

# Re-run only failed jobs
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/rerun-failed-jobs

# Trigger a workflow manually (workflow_dispatch)
WORKFLOW_ID=<workflow_id_or_filename>
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows/$WORKFLOW_ID/dispatches \
  -d '{"ref": "main", "inputs": {"environment": "staging"}}'
```

## 10. Gists

**With gh:**

```bash
gh gist create script.py --public --desc "Useful script"
gh gist list
```

**With curl:**

```bash
# Create a gist
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/gists \
  -d '{
    "description": "Useful script",
    "public": true,
    "files": {
      "script.py": {"content": "print(\"hello\")"}
    }
  }'

# List your gists
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/gists \
  | python3 -c "
import sys, json
for g in json.load(sys.stdin):
    files = ', '.join(g['files'].keys())
    print(f\"  {g['id']}  {g['description'] or '(no desc)':40}  {files}\")"
```

## 11. Splitting a NixOS Flake into Public/Private Repos

When a NixOS flake contains personal information (user name, hostname, email, SSH keys, dotfiles, wallpapers) that shouldn't be public, split it into a generic public repo + a private personal repo.

### Principles

- **Public repo**: modules, templates, examples — reusable by anyone
- **Private repo**: machine-specific config, dotfiles, secrets, agent workspace (`agent-workspace/`)
- Private repo imports public repo as a flake input via `path:` (local) or `github:` (remote)

### Step-by-Step

**1. Identify personal data to strip from the public repo:**

```
User-specific:     user name, email, hostname, timezone, keyboard layout
Security:          SSH keys, API tokens, .env, auth files
Dotfiles:          hypr/, waybar/, eww/, rofi/, dunst/, wallpapers/
Machine-specific:  hardware-configuration.nix, hostname-specific configs
Agent workspace:   agent-workspace/ (memories, skills, sessions, cron, config)
```

**2. Make all options overridable with `lib.mkDefault`:**

```nix
# In public modules, use mkDefault so private config can override with mkForce
{ config, lib, pkgs, ... }:
with lib;
{
  options.services.gaming = {
    enable = mkEnableOption "gaming optimizations";
    gpuVendor = mkOption {
      type = types.str;
      default = "amd";  # default for most users
      description = "GPU vendor (amd or nvidia)";
    };
  };
}
```

**3. Create a generic public `configuration.nix`:**

```nix
{
  imports = [ ./modules ];

  # All values are mkDefault — users override in their private config
  networking.hostName = lib.mkDefault "nixos";
  time.timeZone = lib.mkDefault "UTC";
  i18n.defaultLocale = lib.mkDefault "en_US.UTF-8";
  services.xserver.layout = lib.mkDefault "us";
  users.users.defaultUser = lib.mkDefault {
    isNormalUser = true;
    shell = pkgs.bash;
  };
}
```

**4. Create the private repo structure:**

```
my-private-config/
├── flake.nix                    # Imports public repo
├── hosts/<host>/                  # Machine-specific config
│   ├── configuration.nix        # mkForce overrides
│   ├── home.nix                 # User dotfiles, aliases, scripts
│   └── hardware-configuration.nix
├── hypr/ eww/ Wallpapers/       # Personal dotfiles
├── scripts/                     # Personal scripts (install.sh)
└── agent-workspace/                     # Agent workspace (memories, config, sessions)
```

**5. Private `flake.nix` imports public repo:**

```nix
{
  description = "Private Configuration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    my-desktop-config = {
      # Use local path during development, github: when published
      url = "path:/path/to/my-desktop-config";
      # url = "github:username/my-desktop-config";
    };
    home-manager.url = "github:nix-community/home-manager";
  };

  outputs = { self, nixpkgs, my-desktop-config, home-manager, ... }: {
    nixosConfigurations.<host> = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        my-desktop-config.nixosModules.common
        my-desktop-config.nixosModules.gaming
        ./hosts/<host>/configuration.nix   # mkForce overrides
        home-manager.nixosModules.home-manager {
          home-manager.users.<user> = import ./hosts/<host>/home.nix;
        }
      ];
    };
  };
}
```

### Pitfalls

- **Flake inputs path resolution**: When using `path:`, the path must be an absolute path that exists. The private repo must clone alongside the public repo, or use `github:` input after publishing.
- **`lib.mkForce` all overrides**: The private config must use `mkForce` on every option the public module set with `mkDefault`, or the default wins.
- **`agent-workspace/` workspace size**: The sessions/ directory can grow large (GBs). Add `sessions/` to `.gitignore` in the private repo, or use sparse checkout.
- **SSH keys**: Never commit private SSH keys to any repo. Store them out-of-band (password manager, USB drive, installation script).
- **Token exposure via git**: The `gh auth setup-git` command configures git to use `gh` as credential helper, which may embed tokens in `~/.git-credentials`. Verify this file is excluded.
- **Public repo still builds**: Test that the public repo alone still evaluates (`nix flake check`) after stripping personal data. Add a minimal template user if needed.

## Pitfall: Private Repos Return 404 via Unauthenticated API

When you access a private repo with `curl` (no auth token) or via the browser URL without authentication, GitHub returns **404 Not Found** — not 403 or 401. This can make you think the repo doesn't exist when it's simply private.

**Correct approach:** Always try `gh repo view owner/repo` first. If `gh` is authenticated, it works on both public and private repos.

```bash
# ❌ Wrong — fails on private repos with misleading 404
curl -s https://api.github.com/repos/owner/private-repo

# ✅ Right — works on both public and private repos
gh repo view owner/private-repo
```

## Additional Resources

- `references/gh-json-fields-reference.md` — Complete field reference for `gh repo view --json`, `gh release view --json`, and `gh run view --json`.
- `references/github-api-cheatsheet.md` — API-level curl commands for advanced operations.

## Quick Reference Table

| Action | gh | git + curl |
|--------|-----|-----------|
| Clone | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create repo | `gh repo create name --public` | `curl POST /user/repos` |
| Fork | `gh repo fork o/r --clone` | `curl POST /repos/o/r/forks` + `git clone` |
| Repo info | `gh repo view o/r` | `curl GET /repos/o/r` |
| Edit settings | `gh repo edit --...` | `curl PATCH /repos/o/r` |
| Create release | `gh release create v1.0` | `curl POST /repos/o/r/releases` |
| List workflows | `gh workflow list` | `curl GET /repos/o/r/actions/workflows` |
| Rerun CI | `gh run rerun ID` | `curl POST /repos/o/r/actions/runs/ID/rerun` |
| Set secret | `gh secret set KEY` | `curl PUT /repos/o/r/actions/secrets/KEY` (+ encryption) |

## Linked Resources

- `templates/rust-ci.yml` — Standard Rust CI workflow (test + clippy + fmt + optional MSRV/cross targeting). Copy to `.github/workflows/ci.yml`.
- `references/rust-release-workflow.md` — Rust version bump, tag management, release notes structure, and CARGO_TARGET_DIR patterns.
- `references/github-api-cheatsheet.md` — Session-specific API reference.
