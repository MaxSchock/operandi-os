#!/usr/bin/env python3
"""Project Hivemind EOD pipeline.

Turn the most recent Claude Code session into a SHORT, PII-aware summary and index
it into the shared knowledge base (hivemind.eod_summaries on ki-prod-01).

Design constraints (DSGVO):
  - The raw transcript NEVER leaves the local machine. Only an LLM-generated
    summary (decisions / artifacts / next steps) is stored in the shared DB.
  - Degrades gracefully: if SDKs, API keys or the DB are unavailable, it writes
    the summary to a local outbox (~/.claude/hivemind-outbox/) and exits 0, so it
    never blocks session close. A later flush can push outbox items, but MUST
    skip records flagged "needs_redaction" (heuristic summaries may contain names).

Usage: chat-to-summary.py <jsonl_path>
Env:
  HIVEMIND_USER_ID    employee id (author + RLS identity). Required to index.
  HIVEMIND_CLIENT_ID  client this session belongs to. If unset, inferred from cwd.
  HIVEMIND_DB_DSN     postgres DSN for hivemind_app. If unset -> outbox only.
  ANTHROPIC_API_KEY   if set, used to generate the structured summary via Claude.
  OPENAI_API_KEY      if set, used for the embedding (text-embedding-3-large).
"""
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

OUTBOX = Path.home() / ".claude" / "hivemind-outbox"
SUMMARY_MODEL = "claude-opus-4-8"
EMBED_MODEL = "text-embedding-3-large"
EMBED_DIM = 3072

# Light pseudonymization before anything is sent out. Not a substitute for the
# Tier policy; a backstop for emails/phones that slip into a summary.
PII_PATTERNS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[email]"),
    (re.compile(r"\+?\d[\d ()/-]{7,}\d"), "[phone]"),
]


def log(msg):
    print(f"[chat-to-summary] {msg}", file=sys.stderr)


def pseudonymize(text):
    for pat, repl in PII_PATTERNS:
        text = pat.sub(repl, text)
    return text


def extract_turns(jsonl_path):
    """Minimal transcript extraction (local only)."""
    turns, tools = [], set()
    with open(jsonl_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = ev.get("type")
            msg = ev.get("message", {}) or {}
            content = msg.get("content", "")
            if t == "user" and isinstance(content, str) and content.strip():
                turns.append(("user", content))
            elif t == "user" and isinstance(content, list):
                txt = " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
                if txt.strip():
                    turns.append(("user", txt))
            elif t == "assistant" and isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        tools.add(b.get("name", "?"))
                txt = " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
                if txt.strip():
                    turns.append(("assistant", txt))
    return turns, sorted(tools)


def infer_client_id():
    cid = os.environ.get("HIVEMIND_CLIENT_ID")
    if cid:
        return cid
    # .../clients/<empresa>/clients/<client>/... -> <client>
    parts = Path.cwd().parts
    if "clients" in parts:
        idxs = [i for i, p in enumerate(parts) if p == "clients"]
        last = idxs[-1]
        if last + 1 < len(parts) and parts[last + 1] != "_templates":
            return parts[last + 1]
    return None


def heuristic_summary(turns, tools):
    first_user = next((t for r, t in turns if r == "user"), "")
    last_asst = next((t for r, t in reversed(turns) if r == "assistant"), "")
    return {
        "summary": pseudonymize((first_user[:400] + " … " + last_asst[:400]).strip()),
        "decisions": "",
        "next_steps": "",
        "tools": tools,
        "_llm": False,  # heuristic: may still contain person names -> do not index to shared KB
    }


def llm_summary(turns, tools):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return heuristic_summary(turns, tools)
    try:
        import anthropic
    except ImportError:
        log("anthropic SDK not installed; using heuristic summary.")
        return heuristic_summary(turns, tools)
    transcript = "\n".join(f"{r.upper()}: {t}" for r, t in turns)[:120000]
    prompt = (
        "Summarize this work session for a team knowledge base. Output STRICT JSON with keys "
        '"summary" (3-5 sentences, what was done), "decisions" (bullet list as text), '
        '"next_steps" (bullet list as text). Do NOT include credentials, personal emails or '
        "phone numbers. Keep client/business facts but omit personal contact data.\n\n" + transcript
    )
    try:
        client = anthropic.Anthropic(api_key=key)
        resp = client.messages.create(
            model=SUMMARY_MODEL, max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        data = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
        return {
            "summary": pseudonymize(data.get("summary", "")),
            "decisions": pseudonymize(data.get("decisions", "")),
            "next_steps": pseudonymize(data.get("next_steps", "")),
            "tools": tools,
            "_llm": True,  # LLM-summarized with PII-omission instruction -> safe to index
        }
    except Exception as e:
        log(f"LLM summary failed ({e}); using heuristic.")
        return heuristic_summary(turns, tools)


def embed(text):
    key = os.environ.get("OPENAI_API_KEY")
    if not key or not text.strip():
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        v = client.embeddings.create(model=EMBED_MODEL, input=text[:30000], dimensions=EMBED_DIM)
        return v.data[0].embedding
    except Exception as e:
        log(f"Embedding failed ({e}); storing without vector.")
        return None


def write_outbox(record):
    OUTBOX.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    p = OUTBOX / f"{ts}-{record.get('session_id','sess')[:8]}.json"
    p.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"Stored summary in outbox: {p}")


def index_db(record, embedding):
    dsn = os.environ.get("HIVEMIND_DB_DSN")
    user_id = os.environ.get("HIVEMIND_USER_ID")
    if not dsn or not user_id:
        return False
    try:
        import psycopg
    except ImportError:
        log("psycopg not installed; outbox only.")
        return False
    try:
        with psycopg.connect(dsn) as conn, conn.cursor() as cur:
            # SET does not accept bind parameters over the extended protocol; set_config does.
            cur.execute("SELECT set_config('hivemind.user_id', %s, false)", (user_id,))
            # pgvector text input format; avoids needing a client-side vector adapter.
            emb_val = "[" + ",".join(repr(float(x)) for x in embedding) + "]" if embedding else None
            cur.execute(
                "INSERT INTO hivemind.eod_summaries "
                "(client_id, author, session_id, summary, decisions, next_steps, embedding) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s::vector)",
                (record["client_id"], user_id, record["session_id"], record["summary"],
                 record["decisions"], record["next_steps"], emb_val),
            )
            cur.execute(
                "INSERT INTO hivemind.audit_log (user_id, action, client_id, detail) "
                "VALUES (%s,'insert',%s,'eod_summary')",
                (user_id, record["client_id"]),
            )
            conn.commit()
        log("Indexed summary into hivemind.eod_summaries.")
        return True
    except Exception as e:
        log(f"DB index failed ({e}); falling back to outbox.")
        return False


def main():
    if len(sys.argv) < 2:
        log("Usage: chat-to-summary.py <jsonl_path>")
        return 0  # never block the Stop hook
    jsonl = Path(sys.argv[1])
    if not jsonl.exists():
        log(f"{jsonl} not found.")
        return 0

    client_id = infer_client_id()
    if not client_id:
        log("No client_id (not inside a clients/<empresa>/clients/<X>/ tree and HIVEMIND_CLIENT_ID unset); skipping shared index.")
        return 0

    turns, tools = extract_turns(jsonl)
    if not turns:
        log("No turns; skipping.")
        return 0

    s = llm_summary(turns, tools)
    record = {
        "client_id": client_id,
        "session_id": jsonl.stem,
        "summary": s["summary"],
        "decisions": s["decisions"],
        "next_steps": s["next_steps"],
        "tools": s["tools"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # DSGVO safeguard: a heuristic (non-LLM) summary can still contain person names,
    # which the regex backstop does not catch. Never index such a summary into the
    # shared KB; park it in the outbox flagged for redaction instead.
    if not s.get("_llm"):
        record["needs_redaction"] = True
        log("No LLM available -> summary may contain names; NOT indexing to shared KB, parked in outbox.")
        write_outbox(record)
        return 0

    embedding = embed("\n".join([s["summary"], s["decisions"], s["next_steps"]]))
    if not index_db(record, embedding):
        write_outbox(record)
    return 0


if __name__ == "__main__":
    sys.exit(main())
