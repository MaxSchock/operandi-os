#!/usr/bin/env python3
"""Project Hivemind knowledge-base MCP server (stdio FastMCP).

Exposes the shared KB to a local Claude Code instance, RLS-scoped to the employee.
Every query runs as hivemind_app with set_config('hivemind.user_id', <HIVEMIND_USER_ID>),
so Postgres RLS returns only clients the employee is assigned to. The server cannot
widen its own access; the boundary is enforced in the database.

Env:
  HIVEMIND_DB_DSN    postgres DSN for role hivemind_app (required).
  HIVEMIND_USER_ID   employee identity for RLS (required).
  OPENAI_API_KEY     optional; enables semantic search (text-embedding-3-large).
                     Without it, search falls back to ILIKE keyword match.

Run: python3 server.py    (configured in .mcp.json as the `hivemind-kb` server)
"""
import os
import sys

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    sys.stderr.write("hivemind-kb: 'mcp' package not installed. pip install -r requirements.txt\n")
    raise

import psycopg

DSN = os.environ.get("HIVEMIND_DB_DSN", "")
USER_ID = os.environ.get("HIVEMIND_USER_ID", "")
EMBED_MODEL = "text-embedding-3-large"
EMBED_DIM = 3072

mcp = FastMCP("hivemind-kb")


def _connect():
    if not DSN or not USER_ID:
        raise RuntimeError("HIVEMIND_DB_DSN and HIVEMIND_USER_ID must be set.")
    conn = psycopg.connect(DSN)
    with conn.cursor() as cur:
        # SET does not accept bind parameters over the extended protocol; set_config does.
        cur.execute("SELECT set_config('hivemind.user_id', %s, false)", (USER_ID,))
    return conn


def _embed(text):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        v = OpenAI(api_key=key).embeddings.create(model=EMBED_MODEL, input=text[:8000], dimensions=EMBED_DIM)
        return v.data[0].embedding
    except Exception:
        return None


def _vec(emb):
    # pgvector text input format; avoids needing a client-side vector adapter.
    return "[" + ",".join(repr(float(x)) for x in emb) + "]"


@mcp.tool()
def search_kb(query: str, limit: int = 8) -> str:
    """Search the shared KB (documents + EOD summaries) for the current employee.
    Results are automatically limited to the clients you are assigned to."""
    emb = _embed(query)
    try:
        with _connect() as conn, conn.cursor() as cur:
            if emb is not None:
                vec = _vec(emb)
                cur.execute(
                    "SELECT client_id, title, left(content, 400), source_repo, source_path, "
                    "       (embedding <=> %s::vector) AS dist "
                    "FROM hivemind.documents WHERE embedding IS NOT NULL "
                    "ORDER BY dist ASC LIMIT %s", (vec, limit))
                rows = cur.fetchall()
                cur.execute(
                    "SELECT client_id, 'EOD '||coalesce(session_id,''), left(summary,400), "
                    "       'eod_summaries', session_id, (embedding <=> %s::vector) AS dist "
                    "FROM hivemind.eod_summaries WHERE embedding IS NOT NULL "
                    "ORDER BY dist ASC LIMIT %s", (vec, limit))
                rows += cur.fetchall()
                rows.sort(key=lambda r: r[5])
            else:
                like = f"%{query}%"
                cur.execute(
                    "SELECT client_id, title, left(content,400), source_repo, source_path, 0.0 "
                    "FROM hivemind.documents WHERE content ILIKE %s OR title ILIKE %s LIMIT %s",
                    (like, like, limit))
                rows = cur.fetchall()
            cur.execute("INSERT INTO hivemind.audit_log (user_id, action, detail) VALUES (%s,'search',%s)",
                        (USER_ID, query[:200]))
            conn.commit()
    except Exception as e:
        # Never leak DSN/host details to the client; full error goes to stderr for the admin.
        sys.stderr.write(f"hivemind-kb search error: {e}\n")
        return "Search failed (database unreachable or misconfigured). Ask your admin to check the hivemind-kb server."

    if not rows:
        return "No results (within your assigned clients)."
    out = []
    for r in rows[:limit]:
        client_id, title, snippet, repo, path, _ = r
        loc = f"{repo}/{path}" if repo and path else (repo or "")
        out.append(f"- [{client_id}] {title or '(untitled)'}  ·  {loc}\n  {snippet}")
    return "\n".join(out)


@mcp.tool()
def read_doc(doc_id: int) -> str:
    """Read the full content of a document by id (only if it belongs to a client you can access)."""
    try:
        with _connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT client_id, title, content, source_repo, source_path "
                        "FROM hivemind.documents WHERE id = %s", (doc_id,))
            row = cur.fetchone()
            cur.execute("INSERT INTO hivemind.audit_log (user_id, action, detail) VALUES (%s,'read',%s)",
                        (USER_ID, str(doc_id)))
            conn.commit()
    except Exception as e:
        sys.stderr.write(f"hivemind-kb read error: {e}\n")
        return "Read failed (database unreachable or misconfigured). Ask your admin to check the hivemind-kb server."
    if not row:
        return "Not found, or outside your access scope."
    client_id, title, content, repo, path = row
    return f"# {title or '(untitled)'} [{client_id}]\nSource: {repo}/{path}\n\n{content or ''}"


if __name__ == "__main__":
    mcp.run()
