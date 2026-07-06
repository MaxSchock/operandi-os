# Project Hivemind — Compliance (DSGVO/GDPR)

Internal compliance artifacts for the KIsult team layer. These are **working references**, not legal advice. KIsult is the **data controller** (Verantwortlicher); Anthropic and Hetzner are **processors/sub-processors** (Auftragsverarbeiter).

> **Decision (Max, 2026-07-06): DSGVO items are best-effort, not gates.** Hivemind is an
> internal tool; we respect data protection where it does not obstruct the work. The
> technical hygiene below is built in and stays (it costs nothing day-to-day). The
> contractual items (AVV/DPA) are recommended follow-ups, not deployment blockers.

## Built-in hygiene (implemented, always on)
| Measure | Where |
|---|---|
| Per-client isolation (Forgejo repo per client + pgvector RLS by `client_id`) | `deploy/sql/001_hivemind_schema.sql` |
| EOD pipeline emits LLM summaries, never raw transcripts | `scripts/chat-to-summary.py` |
| No-LLM fallback parks summaries locally (`needs_redaction`), never indexes them | `scripts/chat-to-summary.py` |
| Pre-commit blocklist against secrets/credentials/personal context | `../../.githooks/pre-commit` (activated by the installer) |
| Data residency Germany (EEA), TLS via Traefik, SSH-key-only | ki-prod-01 infra |

## Recommended follow-ups (non-blocking)
- **Anthropic:** each employee uses their **personal Claude subscription** at launch
  (Max's decision 2026-07-06; Claude for Team was evaluated and deferred as not viable
  at the start). Consumer plans have training disabled but include no DPA. Moving the
  team to **Claude for Team** later would add a DPA automatically and is the natural
  upgrade once the team size/budget justifies it.
- **Hetzner AVV:** 2-minute click-through at `accounts.hetzner.com/account/dpa`.
- **Art. 30 register** (`article-30-register.md`): keep roughly current as the system evolves.

## Notes
- Right to erasure (Art. 17) is hard in git history. Mitigation: client PII lives in per-client repos (deletable by deleting/rewriting that repo) and in pgvector rows (deletable by `client_id`), **never** in append-only shared markdown.
- See `data-classification-policy.md` for what may and may not leave a local machine.
