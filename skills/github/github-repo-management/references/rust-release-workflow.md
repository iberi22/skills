# Rust Release Engineering Patterns

Session-specific patterns from the v1.0.0 releases of Xavier, PgHeart, and photon-core (May 2026).

## Version bump pattern

```bash
# 1. Bump version in Cargo.toml
# Using patch tool on the version string
patch old_string='version = "1.0.0-rc.1"' new_string='version = "1.0.0"' path=Cargo.toml

# 2. Verify cargo check passes (catches stale Cargo.lock issues)
CARGO_TARGET_DIR=/tmp/cargo-target-x cargo check -q

# 3. Run tests to validate nothing broke
CARGO_TARGET_DIR=/tmp/cargo-target-x cargo test --lib -q

# 4. Commit
git add -A
git commit -m "v1.0.0: bump version from X to Y"

# 5. Tag
git tag v1.0.0 HEAD -m "v1.0.0: Description"
```

## Tag management

If a v1.0.0 tag already exists at an old commit:

```bash
# Move tag to current HEAD
git tag -d v1.0.0
git tag v1.0.0 HEAD -m "v1.0.0: Description"
git push origin v1.0.0 --force
```

Then handle the GitHub Release:
- If release doesn't exist: `gh release create v1.0.0 --verify-tag ...`
- If release exists: `gh release edit v1.0.0 --notes "..."`

## Release notes structure

Follow this structure for consistent releases:

```markdown
## Project v1.0.0 — Tagline

### ✨ Features
- Main feature points in present tense

### 🛠 Fixes
- Bug fixes, regressions, patches

### 🔒 Security (if applicable)
- Security-related changes

### 🛠 Infrastructure (if applicable)
- CI/CD, docs, tooling

### 📦 License
```

## CARGO_TARGET_DIR workaround

In environments where `/build/` is not writable (permission denied errors):

```bash
# Set a writable per-project target dir
CARGO_TARGET_DIR=/tmp/cargo-target-{shortname} cargo test -q

# Or set an alias in shell config
alias cx='CARGO_TARGET_DIR=/tmp/cargo-target-x cargo'
alias cpg='CARGO_TARGET_DIR=/tmp/cargo-target-pg cargo'
alias cpc='CARGO_TARGET_DIR=/tmp/cargo-target-pc cargo'
```

## Cargo.lock handling

- **Libraries**: Cargo.lock should be in .gitignore (photon-core follows this)
- **Binaries**: Cargo.lock should be committed for reproducible builds (Xavier should check this)
- After version bump, `cargo check` or `cargo generate-lockfile` updates Cargo.lock automatically

## gh auth token for git push

When `git push` fails on HTTPS repos:

```bash
# One-shot: embed token in remote URL
git remote set-url origin https://username:$(gh auth token)@github.com/owner/repo.git

# This is not persistent across token refreshes — prefer:
gh auth setup-git
```
