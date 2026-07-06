# hivemind-kb MCP server

RLS-scoped retrieval over the shared KB (`hivemind.documents` + `hivemind.eod_summaries`).
Lets Claude Code answer "¿qué sabemos del cliente X?" with only the clients the employee may see.

## Tools
- `search_kb(query, limit=8)` — semantic (pgvector cosine) or ILIKE fallback. RLS-filtered.
- `read_doc(doc_id)` — full document, only within access scope.

## How access control works
The server connects as `hivemind_app` (no superuser, no BYPASSRLS) and runs
`set_config('hivemind.user_id', $HIVEMIND_USER_ID, false)` per connection. Postgres
RLS policies (see `deploy/sql/001_hivemind_schema.sql`) restrict every row to clients
present in `hivemind.client_access` for that user. The server cannot widen its own scope.

**Known limit (accepted for MVP):** all employees share the `hivemind_app` DB role,
and `HIVEMIND_USER_ID` is self-declared in each user's local config. Anyone holding
the shared DSN could impersonate a colleague's user id. This is an internal-trust
tool; per-user credentials are the upgrade path if that assumption ever changes.

## Config (env, from `~/.claude/hivemind.env`, sourced by `run.sh`)
| var | meaning |
|---|---|
| `HIVEMIND_DB_DSN` | DSN for role `hivemind_app` (reach `base_postgres`; via SSH tunnel or hosted endpoint) |
| `HIVEMIND_USER_ID` | the employee identity used for RLS + audit |
| `OPENAI_API_KEY` | optional; enables embeddings (text-embedding-3-large, 3072 dim) |

## Install
```
pip install -r mcp-servers/hivemind-kb/requirements.txt
```

## Networking
`base_postgres` is internal to the Swarm on ki-prod-01. For remote employees pick one:
1. **SSH tunnel** (MVP): `ssh -L 5432:base_postgres:5432 ki-prod-01`; point the DSN at localhost.
2. **Hosted SSE** (rollout): host this server on ki-prod-01 behind Traefik (per the existing
   MCP-gateway-SSE pattern) and give each employee a scoped endpoint token. Keeps Postgres internal.

## Verify isolation (must pass before rollout)
Set `HIVEMIND_USER_ID` to a user assigned only to client A; confirm `search_kb`
returns nothing from client B (use synthetic data).
