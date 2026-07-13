#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path
import re
import sys

claude = Path("CLAUDE.md").read_text(encoding="utf-8")

start_marker = "## Skills registry"
end_marker = "### Plugins Anthropic"
try:
    registry = claude.split(start_marker, 1)[1].split(end_marker, 1)[0]
except IndexError:
    print("Could not locate Skills registry section in CLAUDE.md", file=sys.stderr)
    sys.exit(1)

# Assumption: the canonical registry lists repo skills as markdown table rows whose
# first cell is a backticked skill folder name. The section intentionally stops
# before plugin-only skills such as docx/xlsx/pdf/pptx.
registered = set()
for line in registry.splitlines():
    match = re.match(r"^\|\s*`([^`]+)`\s*\|", line)
    if match:
        registered.add(match.group(1))

# Core (siempre instaladas) + biblioteca (instalables con /skills).
# En el repo del operador puede haber skills de biblioteca instaladas
# (copias en .claude/skills/) — el set() dedup evita contarlas doble.
disk = set()
for root in (".claude/skills", "skills-library"):
    for path in Path(root).rglob("SKILL.md"):
        if any("_archived" in part for part in path.parts):
            continue
        disk.add(path.parent.name)

missing_on_disk = sorted(registered - disk)
missing_in_registry = sorted(disk - registered)

if missing_on_disk or missing_in_registry:
    print("Skills registry drift detected:", file=sys.stderr)
    if missing_on_disk:
        print("Listed in CLAUDE.md but missing on disk:", file=sys.stderr)
        for name in missing_on_disk:
            print(f"- {name}", file=sys.stderr)
    if missing_in_registry:
        print("Present on disk but missing in CLAUDE.md:", file=sys.stderr)
        for name in missing_in_registry:
            print(f"- {name}", file=sys.stderr)
    sys.exit(1)

print(f"OK: CLAUDE.md registry matches disk ({len(disk)} skills)")
PY

