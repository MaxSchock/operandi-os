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
# Since 08-10-2026 the registry is prose (core / own / library lists), not a table:
# every backticked kebab-case name in the section counts as registered.
registered = {n for n in re.findall(r"`([a-z0-9][a-z0-9-]*)`", registry) if "-" in n}
# Archived skills (.claude/skills/_archived/<name>) may be named in the section as archived.
archived = {q.parent.name for q in Path(".claude/skills/_archived").rglob("SKILL.md")} if Path(".claude/skills/_archived").exists() else set()
registered -= archived

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
unlisted = sorted(disk - registered)

# Only ghosts fail. Installed skills are deliberately not listed by name since 08-10-2026
# (they show up in every session's skill list); the library list in CLAUDE.md is informative.
if missing_on_disk:
    print("Skills registry drift detected:", file=sys.stderr)
    print("Listed in CLAUDE.md but missing on disk:", file=sys.stderr)
    for name in missing_on_disk:
        print(f"- {name}", file=sys.stderr)
    sys.exit(1)

print(f"OK: no ghosts in CLAUDE.md registry ({len(disk)} skills on disk, {len(unlisted)} not named in CLAUDE.md)")
PY

