#!/usr/bin/env python3
"""
Citation Manager — gestor de fuentes, evidencia y claims con IDs estables.

Maneja:
- sources.json: registro de fuentes con source_id basado en hash
- evidence.json: evidencias literales con localizador
- claims.json: afirmaciones atómicas con estado de soporte
- run_manifest.json: manifiesto del run (query, modo, asunciones)

Los source_id son sha256(raw_url) truncado a 12 caracteres → estables a través
de renumeraciones, ediciones y continuaciones.

Los números de display [1], [2], ... se asignan en tiempo de render con
assign-display-numbers, basado en orden de primera aparición.
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _stable_source_id(raw_url: str) -> str:
    """Genera un source_id estable basado en hash de la URL normalizada."""
    normalized = raw_url.strip().lower().rstrip("/")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def _load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cmd_init_run(args):
    """Inicializa los artefactos del run."""
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "query": args.query,
        "mode": args.mode,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "language": "es",
        "assumptions": [],
        "phase_log": [],
    }
    _save_json(out_dir / "run_manifest.json", manifest)
    _save_json(out_dir / "sources.json", {"sources": []})
    _save_json(out_dir / "evidence.json", {"evidence": []})
    _save_json(out_dir / "claims.json", {"claims": []})

    print(f"✓ Run inicializado en {out_dir}")
    print(f"  Query: {args.query}")
    print(f"  Modo: {args.mode}")
    return 0


def cmd_register_source(args):
    """Registra una nueva fuente. Devuelve el source_id estable."""
    data = json.loads(args.json)
    raw_url = data.get("raw_url", "").strip()
    if not raw_url:
        print("❌ ERROR: 'raw_url' es obligatorio", file=sys.stderr)
        return 1

    source_id = _stable_source_id(raw_url)
    sources_path = Path(args.dir) / "sources.json"
    sources_data = _load_json(sources_path, {"sources": []})

    # Si ya existe, no duplicar
    existing = next(
        (s for s in sources_data["sources"] if s["source_id"] == source_id), None
    )
    if existing:
        print(source_id)
        return 0

    source_entry = {
        "source_id": source_id,
        "raw_url": raw_url,
        "title": data.get("title", ""),
        "source_type": data.get("source_type", "web"),
        "year": data.get("year", ""),
        "author": data.get("author", ""),
        "publication": data.get("publication", ""),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "credibility_score": data.get("credibility_score"),
        "display_number": None,  # se asigna después con assign-display-numbers
    }
    sources_data["sources"].append(source_entry)
    _save_json(sources_path, sources_data)
    print(source_id)
    return 0


def cmd_add_evidence(args):
    """Añade una pieza de evidencia."""
    data = json.loads(args.json)
    source_id = data.get("source_id", "").strip()
    quote = data.get("quote", "").strip()

    if not source_id or not quote:
        print("❌ ERROR: 'source_id' y 'quote' son obligatorios", file=sys.stderr)
        return 1

    evidence_path = Path(args.dir) / "evidence.json"
    evidence_data = _load_json(evidence_path, {"evidence": []})

    evidence_id = hashlib.sha256(
        f"{source_id}::{quote}".encode("utf-8")
    ).hexdigest()[:12]

    entry = {
        "evidence_id": evidence_id,
        "source_id": source_id,
        "quote": quote,
        "evidence_type": data.get("evidence_type", "direct_quote"),
        "locator": data.get("locator", ""),
        "added_at": datetime.now(timezone.utc).isoformat(),
    }
    evidence_data["evidence"].append(entry)
    _save_json(evidence_path, evidence_data)
    print(evidence_id)
    return 0


def cmd_add_claim(args):
    """Añade una afirmación atómica con sus evidencias de soporte."""
    data = json.loads(args.json)
    claim_text = data.get("claim", "").strip()
    if not claim_text:
        print("❌ ERROR: 'claim' es obligatorio", file=sys.stderr)
        return 1

    claims_path = Path(args.dir) / "claims.json"
    claims_data = _load_json(claims_path, {"claims": []})

    claim_id = hashlib.sha256(claim_text.encode("utf-8")).hexdigest()[:12]
    entry = {
        "claim_id": claim_id,
        "claim": claim_text,
        "supporting_evidence_ids": data.get("supporting_evidence_ids", []),
        "support_status": data.get("support_status", "unverified"),
        "section": data.get("section", ""),
        "added_at": datetime.now(timezone.utc).isoformat(),
    }
    claims_data["claims"].append(entry)
    _save_json(claims_path, claims_data)
    print(claim_id)
    return 0


def cmd_assign_display_numbers(args):
    """Asigna [1], [2], [3]... a las fuentes según orden de primera aparición."""
    sources_path = Path(args.dir) / "sources.json"
    sources_data = _load_json(sources_path, {"sources": []})

    # Asignación simple por orden de registro
    for i, src in enumerate(sources_data["sources"], start=1):
        src["display_number"] = i

    _save_json(sources_path, sources_data)
    print(f"✓ Asignados números de display a {len(sources_data['sources'])} fuentes")
    return 0


def cmd_get_bibliography(args):
    """Genera la bibliografía formateada lista para pegar en el informe."""
    sources_path = Path(args.dir) / "sources.json"
    sources_data = _load_json(sources_path, {"sources": []})

    sources = sorted(
        sources_data["sources"], key=lambda s: s.get("display_number") or 9999
    )

    lines = []
    for src in sources:
        n = src.get("display_number", "?")
        author = src.get("author") or src.get("publication") or "Autor desconocido"
        year = src.get("year", "s. f.")
        title = src.get("title", "Sin título")
        publication = src.get("publication", "")
        url = src.get("raw_url", "")
        retrieved = src.get("retrieved_at", "")[:10]

        parts = [f"[{n}]", author, f"({year}).", f'"{title}".']
        if publication:
            parts.append(f"{publication}.")
        if url:
            parts.append(url)
        if retrieved:
            parts.append(f"(Recuperado: {retrieved})")

        lines.append(" ".join(parts))

    print("\n".join(lines))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Citation Manager")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init-run")
    p_init.add_argument("--out-dir", required=True)
    p_init.add_argument("--query", required=True)
    p_init.add_argument("--mode", required=True, choices=["quick", "standard", "deep", "ultradeep"])
    p_init.set_defaults(func=cmd_init_run)

    p_src = sub.add_parser("register-source")
    p_src.add_argument("--json", required=True)
    p_src.add_argument("--dir", required=True)
    p_src.set_defaults(func=cmd_register_source)

    p_ev = sub.add_parser("add-evidence")
    p_ev.add_argument("--json", required=True)
    p_ev.add_argument("--dir", required=True)
    p_ev.set_defaults(func=cmd_add_evidence)

    p_cl = sub.add_parser("add-claim")
    p_cl.add_argument("--json", required=True)
    p_cl.add_argument("--dir", required=True)
    p_cl.set_defaults(func=cmd_add_claim)

    p_num = sub.add_parser("assign-display-numbers")
    p_num.add_argument("--dir", required=True)
    p_num.set_defaults(func=cmd_assign_display_numbers)

    p_bib = sub.add_parser("get-bibliography")
    p_bib.add_argument("--dir", required=True)
    p_bib.set_defaults(func=cmd_get_bibliography)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
