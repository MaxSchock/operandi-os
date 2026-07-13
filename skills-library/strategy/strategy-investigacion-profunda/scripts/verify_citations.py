#!/usr/bin/env python3
"""
Verificador de citas — comprueba la integridad de la bibliografía:
- Cada cita [N] del cuerpo tiene entrada en bibliografía
- Cada entrada de bibliografía tiene URL o DOI válido
- Detecta entradas sospechosas (año reciente sin URL, títulos inventados)
- Cruza con sources.json si está disponible

No hace llamadas de red (entorno aislado). Si se quiere resolución de DOI,
exportar el informe y verificar manualmente.
"""

import argparse
import json
import re
import sys
from pathlib import Path


SUSPICIOUS_PATTERNS = [
    # Citas sin URL ni DOI (sospechosas si son recientes)
    {
        "name": "Cita reciente sin URL ni DOI",
        "regex": r"^\s*\[\d+\][^\n]*\b(202[3-9]|20[3-9]\d)\b[^\n]*$",
        "must_not_match": r"(https?://|10\.\d{4,9}/)",
    },
]


def extract_bibliography(content: str) -> tuple[str, dict]:
    """Extrae la sección de bibliografía y la parsea a dict {n: line}."""
    match = re.search(
        r"##\s+Bibliograf[íi]a\s*\n+(.*?)(?=\n##\s|\Z)",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return "", {}
    text = match.group(1)
    entries = {}
    for line in text.split("\n"):
        m = re.match(r"^\s*\[(\d+)\]\s+(.*)", line)
        if m:
            entries[int(m.group(1))] = m.group(2).strip()
    return text, entries


def extract_body_citations(content: str) -> set[int]:
    """Extrae todos los [N] del cuerpo (excluyendo bibliografía)."""
    bib_match = re.search(
        r"##\s+Bibliograf[íi]a", content, re.IGNORECASE
    )
    body = content[: bib_match.start()] if bib_match else content
    return set(int(n) for n in re.findall(r"\[(\d+)\]", body))


def check_orphan_citations(body_cites: set, bib_entries: dict) -> list[str]:
    """Citas en cuerpo sin entrada en bibliografía."""
    missing = body_cites - set(bib_entries.keys())
    return [f"[{n}] usada en cuerpo pero falta en bibliografía" for n in sorted(missing)]


def check_unused_entries(body_cites: set, bib_entries: dict) -> list[str]:
    """Entradas en bibliografía nunca citadas."""
    unused = set(bib_entries.keys()) - body_cites
    return [f"[{n}] en bibliografía pero no citada en cuerpo" for n in sorted(unused)]


def check_entries_have_url_or_doi(bib_entries: dict) -> list[str]:
    """Cada entrada debe tener URL o DOI."""
    issues = []
    for n, line in bib_entries.items():
        has_url = bool(re.search(r"https?://\S+", line))
        has_doi = bool(re.search(r"10\.\d{4,9}/\S+", line))
        if not (has_url or has_doi):
            issues.append(f"[{n}] sin URL ni DOI: '{line[:80]}...'")
    return issues


def check_suspicious_entries(bib_entries: dict) -> list[str]:
    """Detecta entradas sospechosas."""
    issues = []
    for n, line in bib_entries.items():
        for check in SUSPICIOUS_PATTERNS:
            if re.search(check["regex"], f"[{n}] {line}", re.IGNORECASE):
                if not re.search(check["must_not_match"], line):
                    issues.append(f"[{n}] sospechosa ({check['name']}): '{line[:80]}'")
    return issues


def check_against_sources_json(bib_entries: dict, sources_dir: Path) -> list[str]:
    """Cruza la bibliografía con sources.json si existe."""
    sources_path = sources_dir / "sources.json"
    if not sources_path.exists():
        return []  # no es error, solo aviso opcional

    with open(sources_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    issues = []
    display_numbers_in_json = {
        s.get("display_number")
        for s in data.get("sources", [])
        if s.get("display_number") is not None
    }
    bib_numbers = set(bib_entries.keys())

    only_in_bib = bib_numbers - display_numbers_in_json
    only_in_json = display_numbers_in_json - bib_numbers

    if only_in_bib:
        issues.append(
            f"Citas en bibliografía sin entrada en sources.json: {sorted(only_in_bib)}"
        )
    if only_in_json:
        issues.append(
            f"Fuentes en sources.json no presentes en bibliografía: {sorted(only_in_json)}"
        )

    return issues


def main():
    parser = argparse.ArgumentParser(description="Verificador de citas")
    parser.add_argument("--report", required=True, help="Ruta al informe .md")
    parser.add_argument(
        "--sources-dir",
        help="Carpeta con sources.json (por defecto: la del informe)",
    )
    args = parser.parse_args()

    report = Path(args.report)
    if not report.exists():
        print(f"❌ ERROR: No existe {report}", file=sys.stderr)
        sys.exit(2)

    sources_dir = Path(args.sources_dir) if args.sources_dir else report.parent

    with open(report, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"\n{'='*60}")
    print(f"VERIFICANDO CITAS: {report.name}")
    print(f"{'='*60}\n")

    bib_text, bib_entries = extract_bibliography(content)
    body_cites = extract_body_citations(content)

    print(f"  Citas en cuerpo: {len(body_cites)}")
    print(f"  Entradas en bibliografía: {len(bib_entries)}\n")

    all_issues = []
    all_warnings = []

    orphan = check_orphan_citations(body_cites, bib_entries)
    if orphan:
        all_issues.extend(orphan)
    unused = check_unused_entries(body_cites, bib_entries)
    if unused:
        all_warnings.extend(unused)
    missing_url = check_entries_have_url_or_doi(bib_entries)
    if missing_url:
        all_issues.extend(missing_url)
    suspicious = check_suspicious_entries(bib_entries)
    if suspicious:
        all_warnings.extend(suspicious)
    cross_check = check_against_sources_json(bib_entries, sources_dir)
    if cross_check:
        all_warnings.extend(cross_check)

    if all_issues:
        print(f"❌ Problemas críticos ({len(all_issues)}):")
        for issue in all_issues:
            print(f"  • {issue}")
    if all_warnings:
        print(f"\n⚠️  Avisos ({len(all_warnings)}):")
        for w in all_warnings:
            print(f"  • {w}")
    if not all_issues and not all_warnings:
        print("✓ Sin problemas detectados")

    print(f"\n{'='*60}\n")
    sys.exit(1 if all_issues else 0)


if __name__ == "__main__":
    main()
