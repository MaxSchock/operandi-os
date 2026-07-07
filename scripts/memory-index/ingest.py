#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_CONFIG = SCRIPT_DIR / "corpus.yaml"
if not DEFAULT_CONFIG.exists():  # repo recién clonado: cae al ejemplo genérico
    DEFAULT_CONFIG = SCRIPT_DIR / "corpus.example.yaml"
DEFAULT_DB = REPO_ROOT / "context" / ".memory-index" / "memory.db"
BATCH_SIZE = 32
TARGET_MIN_TOKENS = 400
TARGET_MAX_TOKENS = 700
OVERLAP_SENTENCES = 2
OVERLAP_TOKENS = 80
RRF_K = 60

SECRET_PATTERNS = [
    re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|service[_-]?role[_-]?key)\b\s*[:=]\s*['\"]?[^'\"\s`]+"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\b(?:ghp|github_pat|xox[baprs])-?[A-Za-z0-9_-]{20,}\b"),
]

FTS_STOPWORDS = {
    "a",
    "al",
    "de",
    "del",
    "el",
    "en",
    "la",
    "las",
    "lo",
    "los",
    "para",
    "por",
    "que",
    "qué",
    "se",
    "sobre",
    "un",
    "una",
    "y",
}

# Sinónimos opcionales para ampliar el recall por keyword. VACÍO por defecto:
# este repo es genérico y se distribuye a la comunidad, así que no lleva términos
# de ningún negocio concreto. El operador puede añadir los suyos, p.ej.:
#   {"cpl": ["leadgen", "ret", "captacion"], "mrr": ["ingresos", "facturacion"]}
FTS_EXPANSIONS: dict[str, list[str]] = {}


@dataclass(frozen=True)
class SourceFile:
    path: Path
    source_type: str


@dataclass(frozen=True)
class Chunk:
    source_path: str
    source_type: str
    chunk_index: int
    content: str
    file_hash: str
    metadata: dict[str, object]


def init_db(conn: sqlite3.Connection) -> None:
    schema_sql = (SCRIPT_DIR / "schema.sql").read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()


def expand_sources(config_path: Path) -> list[SourceFile]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    base_dir = config_path.parent
    files: list[SourceFile] = []
    seen: set[Path] = set()
    for source in config.get("sources", []):
        source_type = source["source_type"]
        for pattern in source.get("paths", []):
            expanded = os.path.expanduser(os.path.expandvars(pattern))
            pattern_path = Path(expanded)
            if not pattern_path.is_absolute():
                pattern_path = (base_dir / pattern_path).resolve()
            matches = sorted(pattern_path.parent.glob(pattern_path.name))
            for match in matches:
                if match.is_file() and match.suffix.lower() == ".md":
                    resolved = match.resolve()
                    if resolved not in seen:
                        seen.add(resolved)
                        files.append(SourceFile(path=resolved, source_type=source_type))
    return files


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def scrub_secrets(text: str) -> str:
    scrubbed = text
    for pattern in SECRET_PATTERNS:
        scrubbed = pattern.sub("[REDACTED_SECRET]", scrubbed)
    return scrubbed


def token_count(text: str) -> int:
    return len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE))


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜÑ¿¡0-9])", text.strip())
    return [part.strip() for part in parts if part.strip()]


def sentence_windows(text: str, min_tokens: int, max_tokens: int) -> list[str]:
    sentences = split_sentences(text)
    if not sentences:
        return []
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0
    for sentence in sentences:
        sentence_tokens = token_count(sentence)
        if current and current_tokens + sentence_tokens > max_tokens:
            chunks.append(" ".join(current).strip())
            overlap = current[-OVERLAP_SENTENCES:]
            current = overlap[:]
            current_tokens = token_count(" ".join(current))
        current.append(sentence)
        current_tokens += sentence_tokens
        if current_tokens >= min_tokens:
            chunks.append(" ".join(current).strip())
            overlap = current[-OVERLAP_SENTENCES:]
            current = overlap[:]
            current_tokens = token_count(" ".join(current))
    tail = " ".join(current).strip()
    if tail and (not chunks or tail != chunks[-1]):
        chunks.append(tail)
    return chunks


def token_windows(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    tokens = re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)
    if not tokens:
        return []
    chunks: list[str] = []
    step = max(1, max_tokens - overlap_tokens)
    for start in range(0, len(tokens), step):
        window = tokens[start : start + max_tokens]
        if window:
            chunks.append(" ".join(window))
        if start + max_tokens >= len(tokens):
            break
    return chunks


def enforce_max_tokens(parts: list[str]) -> list[str]:
    chunks: list[str] = []
    for part in parts:
        if token_count(part) <= TARGET_MAX_TOKENS:
            chunks.append(part)
            continue
        chunks.extend(token_windows(part, TARGET_MAX_TOKENS, OVERLAP_TOKENS))
    return chunks


def markdown_sections(text: str) -> list[tuple[str | None, str]]:
    matches = list(re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, flags=re.MULTILINE))
    if not matches:
        return [(None, text.strip())] if text.strip() else []
    sections: list[tuple[str | None, str]] = []
    if matches[0].start() > 0:
        prefix = text[: matches[0].start()].strip()
        if prefix:
            sections.append((None, prefix))
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        title = match.group(2).strip()
        body = text[start:end].strip()
        if body:
            sections.append((title, body))
    return sections


def extract_date(path: Path, text: str) -> str | None:
    candidates = [
        re.search(r"(20\d{2})[-_](\d{2})[-_](\d{2})", path.name),
        re.search(r"\b(20\d{2})[-/](\d{2})[-/](\d{2})\b", text[:1000]),
    ]
    for match in candidates:
        if match:
            return "-".join(match.groups())
    return None


def chunk_markdown(source: SourceFile, file_hash: str) -> list[Chunk]:
    raw = source.path.read_text(encoding="utf-8", errors="ignore")
    text = scrub_secrets(raw)
    date = extract_date(source.path, text)
    chunks: list[Chunk] = []
    for section_title, section_text in markdown_sections(text):
        section_tokens = token_count(section_text)
        if section_tokens <= TARGET_MAX_TOKENS:
            parts = [section_text]
        else:
            parts = sentence_windows(section_text, TARGET_MIN_TOKENS, TARGET_MAX_TOKENS)
        parts = enforce_max_tokens(parts)
        for part in parts:
            content = part.strip()
            if not content:
                continue
            metadata: dict[str, object] = {
                "section_title": section_title,
                "tokens_estimate": token_count(content),
            }
            if date:
                metadata["date"] = date
            chunks.append(
                Chunk(
                    source_path=str(source.path),
                    source_type=source.source_type,
                    chunk_index=len(chunks),
                    content=content,
                    file_hash=file_hash,
                    metadata=metadata,
                )
            )
    return chunks


def unchanged_file(conn: sqlite3.Connection, source_path: str, file_hash: str) -> bool:
    row = conn.execute(
        "SELECT file_hash FROM chunks WHERE source_path = ? LIMIT 1",
        (source_path,),
    ).fetchone()
    return bool(row and row["file_hash"] == file_hash)


def replace_file_chunks(conn: sqlite3.Connection, chunks: list[Chunk]) -> list[int]:
    if not chunks:
        return []
    source_path = chunks[0].source_path
    old_rows = conn.execute("SELECT id FROM chunks WHERE source_path = ?", (source_path,)).fetchall()
    if old_rows and table_exists(conn, "chunks_vec"):
        conn.executemany("DELETE FROM chunks_vec WHERE rowid = ?", [(row["id"],) for row in old_rows])
    conn.execute("DELETE FROM chunks WHERE source_path = ?", (source_path,))
    ids: list[int] = []
    for chunk in chunks:
        cursor = conn.execute(
            """
            INSERT INTO chunks
              (source_path, source_type, chunk_index, content, file_hash, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                chunk.source_path,
                chunk.source_type,
                chunk.chunk_index,
                chunk.content,
                chunk.file_hash,
                json.dumps(chunk.metadata, ensure_ascii=False),
            ),
        )
        ids.append(int(cursor.lastrowid))
    return ids


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table', 'virtual table') AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def batched(items: list[Chunk], size: int) -> Iterable[list[Chunk]]:
    for idx in range(0, len(items), size):
        yield items[idx : idx + size]


def fts_query(raw_query: str) -> str:
    terms: list[str] = []
    for raw_term in re.findall(r"[\w]+", raw_query, flags=re.UNICODE):
        term = raw_term.lower()
        if len(term) <= 1 or term in FTS_STOPWORDS:
            continue
        terms.append(term)
        terms.extend(FTS_EXPANSIONS.get(term, []))
    if not terms:
        return "\"\""
    deduped_terms = list(dict.fromkeys(terms))
    return " OR ".join(f'"{term}"' for term in deduped_terms)


def fts_search(conn: sqlite3.Connection, query: str, limit: int = 5) -> list[dict[str, object]]:
    match_query = fts_query(query)
    rows = conn.execute(
        """
        SELECT
          c.id,
          c.source_path,
          c.source_type,
          c.chunk_index,
          c.metadata,
          snippet(chunks_fts, 0, '[', ']', ' ... ', 24) AS preview,
          bm25(chunks_fts) AS score
        FROM chunks_fts
        JOIN chunks AS c ON c.id = chunks_fts.rowid
        WHERE chunks_fts MATCH ?
        ORDER BY score
        LIMIT ?
        """,
        (match_query, limit),
    ).fetchall()
    return [
        {
            "id": row["id"],
            "source_path": row["source_path"],
            "source_type": row["source_type"],
            "chunk_index": row["chunk_index"],
            "metadata": json.loads(row["metadata"] or "{}"),
            "preview": " ".join((row["preview"] or "").split()),
            "score": float(row["score"]),
        }
        for row in rows
    ]


def reciprocal_rank_fusion(*ranked_lists: list[int], k: int = RRF_K) -> list[tuple[int, float]]:
    scores: dict[int, float] = {}
    for ranked in ranked_lists:
        for rank, chunk_id in enumerate(ranked, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def print_hits(hits: list[dict[str, object]]) -> None:
    for idx, hit in enumerate(hits, start=1):
        metadata = hit.get("metadata") if isinstance(hit.get("metadata"), dict) else {}
        date = metadata.get("date") or "sin_fecha"
        section = metadata.get("section_title") or "sin_seccion"
        print(
            f"{idx}. source_path={hit['source_path']} "
            f"score={hit['score']:.6f} date={date} section={section}\n"
            f"   {hit['preview']}"
        )


def open_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ingest(args: argparse.Namespace) -> int:
    started = time.perf_counter()
    sources = expand_sources(args.config)
    if not sources:
        raise SystemExit(f"ERROR: no se encontraron archivos en {args.config}")

    stats = {
        "files_seen": len(sources),
        "files_skipped": 0,
        "files_processed": 0,
        "chunks_inserted": 0,
    }

    semantic_indexer = None
    with open_db(args.db) as conn:
        init_db(conn)
        if args.semantic:
            from semantic import SemanticIndexer

            semantic_indexer = SemanticIndexer(conn)
            semantic_indexer.init()

        for source in sources:
            file_hash = sha1_file(source.path)
            if unchanged_file(conn, str(source.path), file_hash):
                stats["files_skipped"] += 1
                continue

            chunks = chunk_markdown(source, file_hash)
            chunk_ids = replace_file_chunks(conn, chunks)
            if semantic_indexer is not None:
                semantic_indexer.replace_file_embeddings(chunk_ids, chunks)
            conn.commit()

            stats["files_processed"] += 1
            stats["chunks_inserted"] += len(chunks)

        total_chunks = conn.execute("SELECT COUNT(*) AS count FROM chunks").fetchone()["count"]
        elapsed = time.perf_counter() - started
        mode = "semantic" if args.semantic else "base"
        print(
            "INGEST_OK "
            f"mode={mode} "
            f"db={args.db} "
            f"files_seen={stats['files_seen']} "
            f"files_processed={stats['files_processed']} "
            f"files_skipped={stats['files_skipped']} "
            f"chunks_inserted={stats['chunks_inserted']} "
            f"chunks_total={total_chunks} "
            f"elapsed_seconds={elapsed:.2f}"
        )

        if args.smoke_query:
            print(f"SMOKE_QUERY {args.smoke_query}")
            hits = fts_search(conn, args.smoke_query, limit=5)
            print_hits(hits)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Indexa memoria markdown local con SQLite + FTS5.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Ruta a corpus.yaml.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Ruta del memory.db local.")
    parser.add_argument("--semantic", action="store_true", help="Activa sqlite-vec + multilingual-e5-small opt-in.")
    parser.add_argument("--query", "--smoke-query", dest="smoke_query", help="Ejecuta búsqueda FTS5 top-5 tras el ingest incremental (también vale --smoke-query).")
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(ingest(parse_args(sys.argv[1:])))
