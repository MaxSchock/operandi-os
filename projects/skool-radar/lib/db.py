"""SQLite store for the Skool radar. One row per post, comment and lesson.

Dedupe key is always Skool's own id, so re-running a collection is idempotent
and only new material gets scored.
"""
import json
import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "radar.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id            TEXT PRIMARY KEY,
    community     TEXT NOT NULL,
    slug          TEXT,
    url           TEXT,
    kind          TEXT,              -- post | lesson
    title         TEXT,
    content       TEXT,
    author        TEXT,
    labels        TEXT,
    upvotes       INTEGER,
    n_comments    INTEGER,
    videos        TEXT,              -- json: [{provider, video_id, url, len_ms, title}]
    created_at    TEXT,
    updated_at    TEXT,
    course        TEXT,              -- lessons only: course title
    module        TEXT,              -- lessons only: module title
    fetched_at    TEXT,
    comments_at   TEXT,              -- when the thread was last pulled
    transcript    TEXT,              -- video transcript / visual notes, when pulled
    score         INTEGER,           -- relevance 0-100, set by the scoring pass
    score_reason  TEXT,
    scored_at     TEXT,
    reported_at   TEXT               -- set once it has appeared in a digest
);
CREATE TABLE IF NOT EXISTS comments (
    id         TEXT PRIMARY KEY,
    post_id    TEXT NOT NULL,
    parent_id  TEXT,
    depth      INTEGER,
    author     TEXT,
    content    TEXT,
    upvotes    INTEGER,
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS runs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    community  TEXT,
    started_at TEXT,
    ended_at   TEXT,
    new_posts  INTEGER,
    note       TEXT
);
CREATE INDEX IF NOT EXISTS idx_posts_community ON posts(community, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_unscored ON posts(score) WHERE score IS NULL;
CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id);
"""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(path=DB_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def known_post_ids(con, community):
    return {r[0] for r in con.execute("SELECT id FROM posts WHERE community = ?", (community,))}


def upsert_post(con, p):
    """Insert or refresh a post. Never clobbers transcript/score on refresh."""
    cols = ("id", "community", "slug", "url", "kind", "title", "content", "author", "labels",
            "upvotes", "n_comments", "videos", "created_at", "updated_at", "course", "module",
            "fetched_at")
    vals = [p.get(c) for c in cols[:-1]] + [now()]
    placeholders = ",".join("?" * len(cols))
    updates = ",".join(f"{c}=excluded.{c}" for c in cols if c != "id")
    con.execute(
        f"INSERT INTO posts ({','.join(cols)}) VALUES ({placeholders}) "
        f"ON CONFLICT(id) DO UPDATE SET {updates}",
        vals,
    )


def save_comments(con, post_id, rows):
    con.executemany(
        "INSERT INTO comments (id, post_id, parent_id, depth, author, content, upvotes, created_at) "
        "VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET "
        "content=excluded.content, upvotes=excluded.upvotes",
        rows,
    )
    con.execute("UPDATE posts SET comments_at = ? WHERE id = ?", (now(), post_id))


def start_run(con, community):
    cur = con.execute("INSERT INTO runs (community, started_at) VALUES (?,?)", (community, now()))
    con.commit()
    return cur.lastrowid


def end_run(con, run_id, new_posts, note=""):
    con.execute("UPDATE runs SET ended_at=?, new_posts=?, note=? WHERE id=?",
                (now(), new_posts, note, run_id))
    con.commit()


def jdump(x):
    return json.dumps(x, ensure_ascii=False)
