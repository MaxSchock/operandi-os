#!/usr/bin/env bash
set -euo pipefail

while IFS= read -r script; do
  bash -n "$script"
done < <(find scripts -maxdepth 1 -name "*.sh" -print | sort)

if [ -d scripts/ci ]; then
  while IFS= read -r script; do
    bash -n "$script"
  done < <(find scripts/ci -maxdepth 1 -name "*.sh" -print | sort)
fi

if [ -d scripts/memory-index ]; then
  export PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-/tmp/iamasters-os-pycache}"
  while IFS= read -r py_file; do
    python3 -m py_compile "$py_file"
  done < <(find scripts/memory-index -maxdepth 1 -name "*.py" -print | sort)
fi

python3 - <<'PY'
from pathlib import Path
import json
import sys

yaml_path = Path("scripts/memory-index/corpus.example.yaml")
lines = yaml_path.read_text(encoding="utf-8").splitlines()

in_sources = False
current_item = None
current_paths = None
errors = []

for line_no, raw in enumerate(lines, start=1):
    stripped = raw.strip()
    if not stripped or stripped.startswith("#"):
        continue
    if stripped == "sources:":
        in_sources = True
        continue
    if not in_sources:
        errors.append(f"{yaml_path}:{line_no}: unexpected content before sources")
        continue
    if stripped.startswith("- source_type:"):
        current_item = stripped.split(":", 1)[1].strip()
        current_paths = None
        if not current_item:
            errors.append(f"{yaml_path}:{line_no}: empty source_type")
        continue
    if stripped == "paths:":
        if current_item is None:
            errors.append(f"{yaml_path}:{line_no}: paths without source_type")
        current_paths = []
        continue
    if stripped.startswith("- "):
        if current_paths is None:
            errors.append(f"{yaml_path}:{line_no}: list item outside paths")
        elif not stripped[2:].strip():
            errors.append(f"{yaml_path}:{line_no}: empty path")
        continue
    errors.append(f"{yaml_path}:{line_no}: unsupported YAML shape: {stripped}")

if errors:
    print("YAML parse check failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    sys.exit(1)

for path in sorted(Path(".").rglob("*template*.json")):
    if "vendor" in path.parts:
        continue
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(1)

print("OK: shell, Python, YAML example and template JSON syntax are valid")
PY
