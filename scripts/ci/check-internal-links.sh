#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
from urllib.parse import unquote
import re
import sys

files = [Path("README.md")] + sorted(Path("docs").glob("*.md"))
link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
errors = []

for path in files:
    in_code_block = False
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        for match in link_pattern.finditer(line):
            target = match.group(1).strip()
            if not target or target.startswith("#"):
                continue
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue

            target = target.split("#", 1)[0].split("?", 1)[0].strip()
            if not target:
                continue

            resolved = (path.parent / unquote(target)).resolve()
            try:
                resolved.relative_to(Path.cwd().resolve())
            except ValueError:
                errors.append(f"{path}:{line_no}: link escapes repo: {match.group(1)}")
                continue

            if not resolved.exists():
                errors.append(f"{path}:{line_no}: missing target: {match.group(1)}")

if errors:
    print("Internal markdown link check failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    sys.exit(1)

print(f"OK: internal markdown links are alive in {len(files)} files")
PY

