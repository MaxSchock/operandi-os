PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS chunks (
  id INTEGER PRIMARY KEY,
  source_path TEXT NOT NULL,
  source_type TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  file_hash TEXT NOT NULL,
  metadata TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(source_path, chunk_index)
);

CREATE INDEX IF NOT EXISTS chunks_source_path_idx
  ON chunks (source_path);

CREATE INDEX IF NOT EXISTS chunks_file_hash_idx
  ON chunks (source_path, file_hash);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
  content,
  source_path UNINDEXED,
  content='chunks',
  content_rowid='id',
  tokenize='unicode61 remove_diacritics 2'
);

CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
  INSERT INTO chunks_fts(rowid, content, source_path)
  VALUES (new.id, new.content, new.source_path);
END;

CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
  INSERT INTO chunks_fts(chunks_fts, rowid, content, source_path)
  VALUES ('delete', old.id, old.content, old.source_path);
END;

CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
  INSERT INTO chunks_fts(chunks_fts, rowid, content, source_path)
  VALUES ('delete', old.id, old.content, old.source_path);
  INSERT INTO chunks_fts(rowid, content, source_path)
  VALUES (new.id, new.content, new.source_path);
END;
