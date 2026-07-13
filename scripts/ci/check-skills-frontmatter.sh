#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import sys

root = Path(".claude/skills")
errors = []

for path in sorted(root.rglob("SKILL.md")):
    if any("_archived" in part for part in path.parts):
        continue

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        errors.append(f"{path}: missing YAML frontmatter")
        continue

    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        errors.append(f"{path}: frontmatter is not closed")
        continue

    frontmatter = lines[1:end]
    fields = {}
    for line in frontmatter:
        if not line or line[:1].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")

    for key in ("name", "description"):
        if not fields.get(key):
            errors.append(f"{path}: missing non-empty {key}")

if errors:
    print("Skills frontmatter check failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    sys.exit(1)

print("OK: skills have non-empty name and description frontmatter")
PY

