from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Iterable


MODEL_NAME = "intfloat/multilingual-e5-small"
EMBEDDING_DIM = 384
BATCH_SIZE = 32


@dataclass(frozen=True)
class SemanticHit:
    chunk_id: int
    distance: float


class SemanticIndexer:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self._embedder = None
        self._sqlite_vec = None

    def init(self) -> None:
        self._load_sqlite_vec()
        self.conn.execute(
            f"CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(embedding float[{EMBEDDING_DIM}])"
        )

    def replace_file_embeddings(self, chunk_ids: list[int], chunks: list[object]) -> None:
        if len(chunk_ids) != len(chunks):
            raise RuntimeError(f"chunks/ids mismatch: {len(chunks)} != {len(chunk_ids)}")
        if not chunk_ids:
            return
        self.conn.executemany("DELETE FROM chunks_vec WHERE rowid = ?", [(chunk_id,) for chunk_id in chunk_ids])
        texts = [f"passage: {chunk.content}" for chunk in chunks]
        for id_batch, vector_batch in zip(batched(chunk_ids, BATCH_SIZE), self._embed(texts, BATCH_SIZE)):
            self.conn.executemany(
                "INSERT INTO chunks_vec(rowid, embedding) VALUES (?, ?)",
                [(chunk_id, self._serialize(vector)) for chunk_id, vector in zip(id_batch, vector_batch)],
            )

    def search(self, query: str, limit: int = 25) -> list[SemanticHit]:
        vector = self._serialize(next(self._model().embed([f"query: {query}"])).tolist())
        rows = self.conn.execute(
            """
            SELECT rowid, distance
            FROM chunks_vec
            WHERE embedding MATCH ? AND k = ?
            ORDER BY distance
            """,
            (vector, limit),
        ).fetchall()
        return [SemanticHit(chunk_id=int(row["rowid"]), distance=float(row["distance"])) for row in rows]

    def _load_sqlite_vec(self):
        if self._sqlite_vec is not None:
            return self._sqlite_vec
        try:
            import sqlite_vec
        except ImportError as exc:
            raise SystemExit(
                "ERROR: --semantic requiere dependencias opcionales: pip install sqlite-vec fastembed"
            ) from exc
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        self._sqlite_vec = sqlite_vec
        return sqlite_vec

    def _model(self):
        if self._embedder is not None:
            return self._embedder
        try:
            from fastembed import TextEmbedding
        except ImportError as exc:
            raise SystemExit(
                "ERROR: --semantic requiere dependencias opcionales: pip install sqlite-vec fastembed"
            ) from exc
        self._embedder = TextEmbedding(model_name=MODEL_NAME)
        return self._embedder

    def _embed(self, texts: list[str], size: int) -> Iterable[list[list[float]]]:
        model = self._model()
        for batch in batched(texts, size):
            yield [vector.tolist() for vector in model.embed(batch)]

    def _serialize(self, vector: list[float]) -> bytes | str:
        sqlite_vec = self._load_sqlite_vec()
        if hasattr(sqlite_vec, "serialize_float32"):
            return sqlite_vec.serialize_float32(vector)
        return json.dumps(vector)


def batched(items: list, size: int) -> Iterable[list]:
    for idx in range(0, len(items), size):
        yield items[idx : idx + size]
