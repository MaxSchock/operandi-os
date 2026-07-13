#!/usr/bin/env python3
"""
Source Evaluator — puntúa la credibilidad de una fuente 0-100 según heurísticas:

- Dominio (académico, gobierno, prensa establecida, blog personal...)
- Presencia de DOI
- Recencia
- Tipo de fuente declarado (paper, preprint, news, blog, opinion)

NO hace verificación de red. Solo análisis heurístico de metadatos.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from urllib.parse import urlparse


HIGH_CREDIBILITY_TLDS = {".gov", ".edu", ".int"}
HIGH_CREDIBILITY_DOMAINS = {
    "nature.com", "science.org", "nejm.org", "thelancet.com", "cell.com",
    "pnas.org", "sciencedirect.com", "springer.com", "wiley.com", "tandfonline.com",
    "arxiv.org", "ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov",
    "who.int", "europa.eu", "oecd.org", "imf.org", "worldbank.org",
    "anthropic.com", "openai.com", "deepmind.com",
    "ft.com", "economist.com", "reuters.com", "ap.org", "bloomberg.com",
    "elpais.com", "elmundo.es", "bbc.com", "lemonde.fr",
}
MEDIUM_CREDIBILITY_DOMAINS = {
    "nytimes.com", "washingtonpost.com", "wsj.com", "theguardian.com",
    "wired.com", "technologyreview.com", "spectrum.ieee.org",
    "github.com", "stackoverflow.com",
    "medium.com",  # depende del autor
}
LOW_CREDIBILITY_INDICATORS = {
    "blogspot.com", "wordpress.com", "substack.com",  # blogs personales
    "reddit.com", "quora.com",  # foros
    "tiktok.com", "instagram.com", "twitter.com", "x.com",  # social
}


def score_url(url: str) -> tuple[int, list[str]]:
    """Devuelve (score 0-100, lista de razones)."""
    reasons = []
    score = 50  # baseline neutro

    parsed = urlparse(url)
    domain = parsed.netloc.lower().lstrip("www.")

    # TLD académico/gobierno
    for tld in HIGH_CREDIBILITY_TLDS:
        if domain.endswith(tld):
            score += 30
            reasons.append(f"TLD de alta credibilidad ({tld})")
            break

    # Dominios específicos
    if any(d in domain for d in HIGH_CREDIBILITY_DOMAINS):
        score += 25
        reasons.append("Dominio establecido de alta credibilidad")
    elif any(d in domain for d in MEDIUM_CREDIBILITY_DOMAINS):
        score += 10
        reasons.append("Dominio de credibilidad media")
    elif any(d in domain for d in LOW_CREDIBILITY_INDICATORS):
        score -= 20
        reasons.append("Indicador de baja credibilidad (blog personal/social)")

    # HTTPS
    if parsed.scheme == "https":
        score += 5
        reasons.append("HTTPS")

    return max(0, min(100, score)), reasons


def score_metadata(meta: dict) -> tuple[int, list[str]]:
    """Puntúa según metadatos adicionales."""
    score = 0
    reasons = []

    source_type = meta.get("source_type", "").lower()
    if source_type == "academic" or source_type == "peer_reviewed":
        score += 15
        reasons.append("Tipo: académico/peer-reviewed")
    elif source_type == "preprint":
        score += 5
        reasons.append("Tipo: preprint (no peer-reviewed)")
    elif source_type == "news":
        score += 3
    elif source_type == "blog" or source_type == "opinion":
        score -= 10
        reasons.append("Tipo: blog/opinión")

    if meta.get("doi"):
        score += 10
        reasons.append("Tiene DOI")

    year = meta.get("year", "")
    if year:
        try:
            y = int(year)
            current = datetime.now().year
            age = current - y
            if age <= 2:
                score += 5
                reasons.append(f"Reciente ({y})")
            elif age > 10:
                score -= 5
                reasons.append(f"Antiguo ({y})")
        except ValueError:
            pass

    return score, reasons


def evaluate(url: str = "", metadata_json: str = "") -> dict:
    meta = json.loads(metadata_json) if metadata_json else {}
    if not url:
        url = meta.get("raw_url", "")

    url_score, url_reasons = score_url(url) if url else (0, ["Sin URL"])
    meta_score, meta_reasons = score_metadata(meta)

    final = max(0, min(100, url_score + meta_score))
    return {
        "url": url,
        "score": final,
        "url_score": url_score,
        "metadata_score": meta_score,
        "reasons": url_reasons + meta_reasons,
        "tier": (
            "alta" if final >= 75
            else "media" if final >= 50
            else "baja" if final >= 30
            else "muy baja"
        ),
    }


def main():
    parser = argparse.ArgumentParser(description="Source Evaluator")
    parser.add_argument("--url", default="", help="URL de la fuente")
    parser.add_argument(
        "--metadata", default="", help="JSON con metadatos adicionales"
    )
    args = parser.parse_args()

    if not args.url and not args.metadata:
        print("❌ ERROR: Proporciona --url o --metadata", file=sys.stderr)
        sys.exit(1)

    result = evaluate(args.url, args.metadata)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
