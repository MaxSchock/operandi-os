# Data Classification Policy — Project Hivemind

Three tiers govern where data may live. The pre-commit hook and the EOD pipeline enforce the boundary mechanically; this document is the human-readable rule.

## Tier 1 — Universal (shared, all team members)
Process knowledge with **no client PII**.
- Templates, frameworks, checklists, decision trees.
- Anonymized learnings and case patterns ("how we structure a RAG ingest").
- Tooling notes, prompt patterns, n8n patterns (no credentials).

**Lives in:** Forgejo repo `hivemind-shared`. Readable by everyone.

## Tier 2 — Per-client (shared only with the assigned team)
Work artifacts that contain client business data.
- Briefs, workflow backups (JSON), deliverable drafts, project docs.
- **LLM-generated summaries** of sessions (decisions, artifacts, next steps), pseudonymized where practical.

**Lives in:** Forgejo repo `client-<X>` (repo-level access via Forgejo team) **and** indexed in `hivemind.documents` with `client_id=<X>` (RLS-scoped). Readable only by members assigned to client X.

## Tier 3 — FORBIDDEN on the shared server (local only / secrets manager)
Never pushed to Forgejo or indexed in pgvector.
- Credentials of any kind: `.env`, API keys, tokens, passwords, SSH private keys, n8n keys.
- Employee personal data (salaries, IDs, home addresses).
- **Raw chat transcripts** (full conversations). Only LLM summaries cross into Tier 2.
- Special-category data (Art. 9) unless a specific lawful basis + DPIA exists.

**Lives in:** the employee's local machine and/or a secrets manager. Backups stay local/encrypted.

## Enforcement
- **Pre-commit hook** (`.githooks/pre-commit`): a blocklist that rejects commits containing `.env` files, secret-like patterns, credential paths or personal operator context. Activated automatically by the installer (`core.hooksPath`).
- **EOD pipeline** (`scripts/chat-to-summary.py`): emits a structured summary into Tier 2; the raw transcript is handled locally by `chat-to-md.py` and never leaves the machine.
- **Forgejo teams** + **pgvector RLS by `client_id`**: a member of client A cannot read client B.

## When in doubt
Treat it as the **higher** tier. If you cannot tell whether a name is PII, pseudonymize it. The cost of over-restricting is friction; the cost of under-restricting is a reportable breach.
