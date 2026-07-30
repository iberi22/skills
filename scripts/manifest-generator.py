#!/usr/bin/env python3
"""
Manifest Generator for iberi22/skills

Scans skills/<category>/<skill-name>/SKILL.md, parses frontmatter YAML,
and generates _registry/manifest.yaml with structured metadata.
"""

import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_OWNER = "iberi22"
REPO_NAME = "skills"
BRANCH = "main"
SKILLS_DIR = Path("skills")
REGISTRY_DIR = Path("_registry")
MANIFEST_PATH = REGISTRY_DIR / "manifest.yaml"

# Regex to extract YAML frontmatter from markdown
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def extract_description(content: str, frontmatter: dict) -> str:
    """Extract a short description from frontmatter or markdown body."""
    # 1. Use explicit description field if present
    if frontmatter.get("description"):
        return str(frontmatter["description"]).strip()

    # 2. Use first goal as description if it's a short string
    goals = frontmatter.get("goals", [])
    if goals and isinstance(goals[0], str) and len(goals[0]) < 300:
        return goals[0].strip()

    # 3. Extract first paragraph from markdown body (after frontmatter)
    body = FRONTMATTER_RE.sub("", content, count=1).strip()
    # Remove markdown headers and clean up
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    for line in lines:
        # Skip markdown headers
        if line.startswith("#"):
            continue
        # Skip horizontal rules
        if line.startswith("---"):
            continue
        # Clean markdown formatting
        clean = re.sub(r"[*_`\[\]\(\)]", "", line)
        if len(clean) > 20:
            return clean.strip()

    # 4. Fallback to name
    return frontmatter.get("name", "")


def parse_skill_file(skill_path: Path) -> dict:
    """Parse a single SKILL.md file and return manifest entry."""
    content = skill_path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(content)
    if not match:
        raise ValueError(f"No frontmatter found in {skill_path}")

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {skill_path}: {e}") from e
    if not isinstance(frontmatter, dict):
        raise TypeError(f"Frontmatter must be a mapping in {skill_path}")

    # Determine relative path components
    rel = skill_path.relative_to(SKILLS_DIR)
    category = rel.parts[0]
    skill_name = rel.parts[1] if len(rel.parts) > 1 else frontmatter.get("id", "")

    # GitHub raw URL
    raw_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/skills/{category}/{skill_name}/SKILL.md"

    entry = {
        "id": frontmatter.get("id") or skill_name,
        "name": frontmatter.get("name") or skill_name,
        "description": extract_description(content, frontmatter),
        "category": frontmatter.get("category") or category,
        "tags": frontmatter.get("tags", []),
        "path": f"skills/{category}/{skill_name}",
        "raw_url": raw_url,
    }

    # Optional fields
    if "version" in frontmatter:
        entry["version"] = str(frontmatter["version"])
    if "authors" in frontmatter:
        entry["authors"] = frontmatter["authors"]
    if "license" in frontmatter:
        entry["license"] = frontmatter["license"]
    if "original_source" in frontmatter:
        entry["original_source"] = frontmatter["original_source"]

    return entry


def find_duplicate_id_errors(entries: list[dict]) -> list[str]:
    """Return one error for every skill ID used by multiple paths."""
    paths_by_id: dict[str, list[str]] = {}
    for entry in entries:
        skill_id = str(entry["id"])
        paths_by_id.setdefault(skill_id, []).append(entry["path"])

    return [
        f"Duplicate skill id '{skill_id}' in {', '.join(paths)}"
        for skill_id, paths in sorted(paths_by_id.items())
        if len(paths) > 1
    ]


def generate_manifest():
    """Scan skills/ and generate manifest.yaml."""
    entries = []
    errors = []

    for category_dir in sorted(SKILLS_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        for skill_dir in sorted(category_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                errors.append(f"Missing SKILL.md in {skill_dir}")
                continue
            try:
                entry = parse_skill_file(skill_file)
                entries.append(entry)
            except (OSError, TypeError, ValueError) as e:
                errors.append(f"Error parsing {skill_file}: {e}")

    errors.extend(find_duplicate_id_errors(entries))
    if errors:
        print("Errors:")
        for err in errors:
            print(f"  - {err}")
        raise SystemExit(1)

    manifest = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": f"https://github.com/{REPO_OWNER}/{REPO_NAME}",
        "total_skills": len(entries),
        "categories": sorted({e["category"] for e in entries}),
        "skills": entries,
    }

    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        yaml.dump(
            manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True
        )

    print(f"Generated manifest with {len(entries)} skills at {MANIFEST_PATH}")


if __name__ == "__main__":
    generate_manifest()
