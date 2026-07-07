-- Project Hivemind — schema + RLS for the shared knowledge index.
-- Target: base_postgres on ki-prod-01, dedicated DB "hivemind" (isolated from
-- the suritec RAG in DB "rag": own blast radius, grants and restores). Idempotent.
-- Run as a superuser/owner:  psql "$DSN" -f deploy/sql/001_hivemind_schema.sql
--
-- Access model (confirmed): all-or-nothing per client. A user assigned to a
-- client sees ALL of that client's rows; nothing of other clients.
-- RLS keys off the session setting hivemind.user_id, set per-connection by the
-- MCP server (mcp-servers/hivemind-kb). Unset -> current_setting(...,true) is
-- NULL -> policies return zero rows (safe default).

CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS hivemind;

-- Who may see which client. all-or-nothing: presence of a row grants full access.
CREATE TABLE IF NOT EXISTS hivemind.client_access (
    user_id    text NOT NULL,
    client_id  text NOT NULL,
    level      text NOT NULL DEFAULT 'member',   -- reserved for future intra-client granularity
    granted_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, client_id)
);

-- Tier 2 artifacts + their embeddings (pointer to the authoritative file in Forgejo).
CREATE TABLE IF NOT EXISTS hivemind.documents (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    client_id   text NOT NULL,
    title       text,
    content     text,
    embedding   vector(3072),               -- OpenAI text-embedding-3-large
    author      text,
    source_repo text,                        -- e.g. client-<X>
    source_path text,                        -- path within that repo
    created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS documents_client_idx ON hivemind.documents (client_id);

-- EOD session summaries (LLM-generated; never raw transcripts).
CREATE TABLE IF NOT EXISTS hivemind.eod_summaries (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    client_id   text NOT NULL,
    author      text,
    session_id  text,
    summary     text,
    decisions   text,
    next_steps  text,
    embedding   vector(3072),
    created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS eod_client_idx ON hivemind.eod_summaries (client_id);

-- Accountability (Art. 5(2) / Art. 30). Not RLS-restricted; admin-only via GRANT.
CREATE TABLE IF NOT EXISTS hivemind.audit_log (
    id        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id   text,
    action    text,        -- search | read | insert | delete | access_grant | access_revoke
    client_id text,
    detail    text,
    at        timestamptz NOT NULL DEFAULT now()
);

-- NOTE on ANN index: vector(3072) exceeds the 2000-dim limit of ivfflat/hnsw.
-- At MVP scale exact cosine scan (<=>) is fine. To scale, migrate the column to
-- halfvec(3072) and add: CREATE INDEX ON hivemind.documents
--   USING hnsw ((embedding::halfvec(3072)) halfvec_cosine_ops);

-- ---- Row Level Security ----------------------------------------------------
ALTER TABLE hivemind.documents      ENABLE ROW LEVEL SECURITY;
ALTER TABLE hivemind.documents      FORCE  ROW LEVEL SECURITY;
ALTER TABLE hivemind.eod_summaries  ENABLE ROW LEVEL SECURITY;
ALTER TABLE hivemind.eod_summaries  FORCE  ROW LEVEL SECURITY;

DROP POLICY IF EXISTS documents_rls ON hivemind.documents;
CREATE POLICY documents_rls ON hivemind.documents
    USING (client_id IN (
        SELECT client_id FROM hivemind.client_access
        WHERE user_id = current_setting('hivemind.user_id', true)
    ));

DROP POLICY IF EXISTS eod_rls ON hivemind.eod_summaries;
CREATE POLICY eod_rls ON hivemind.eod_summaries
    USING (client_id IN (
        SELECT client_id FROM hivemind.client_access
        WHERE user_id = current_setting('hivemind.user_id', true)
    ));

-- ---- Service role ----------------------------------------------------------
-- The MCP server connects as hivemind_app (NOT superuser, NOT BYPASSRLS), so RLS applies.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'hivemind_app') THEN
        CREATE ROLE hivemind_app LOGIN;   -- set password out-of-band: ALTER ROLE hivemind_app PASSWORD '...';
    END IF;
END$$;

GRANT USAGE ON SCHEMA hivemind TO hivemind_app;
GRANT SELECT, INSERT ON hivemind.documents, hivemind.eod_summaries TO hivemind_app;
-- audit_log is write-only for the app role (admin-only reads, see comment above):
-- everyone can append audit events, nobody but the admin can read other users' activity.
REVOKE ALL ON hivemind.audit_log FROM hivemind_app;
GRANT INSERT ON hivemind.audit_log TO hivemind_app;
GRANT SELECT ON hivemind.client_access TO hivemind_app;
-- Admin maintains client_access / deletions (erasure) via a separate privileged role.

-- Sanity: confirm a user with no client_access sees nothing.
--   SET hivemind.user_id = 'nobody'; SELECT count(*) FROM hivemind.documents;  -- expect 0
