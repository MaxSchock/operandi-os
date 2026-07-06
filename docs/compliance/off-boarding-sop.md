# Off-boarding SOP — Project Hivemind

When a team member leaves (or loses a client assignment), revoke access fast and provably. Target SLA: **access revoked within 24h; shared credentials rotated within 72h.**

Responsible: ______________ (admin). Log every off-boarding in `hivemind.audit_log` + this file's history.

## Immediate (within 24h)
1. **Forgejo:** remove the user from all teams; deactivate the account. (Removes read access to `client-*` repos.)
2. **SSH:** delete their `kisult_hivemind_<user>` public key from Forgejo (and from `ki-prod-01` `authorized_keys` if it was ever added there).
3. **pgvector:** remove their rows from `hivemind.client_access` (drops RLS visibility immediately). There is no per-person DB role: everyone connects as the shared `hivemind_app` (accepted MVP limitation, see `mcp-servers/hivemind-kb/README.md`), which is why step 5 below is mandatory on departure.
4. **MCP:** if a hosted `hivemind-kb` SSE endpoint is used, revoke their endpoint token.

## Within 72h
5. **Rotate shared secrets** the person could have seen: **the `hivemind_app` DB password** (ALTER ROLE on ki-prod-01 + update every remaining team member's `~/.claude/hivemind.env`), the shared `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` handed out in `hivemind.env`, relevant n8n API keys, MinIO keys, any shared service credentials. (Per CLAUDE.md secret-rotation flow: Max edits secrets on the server, restart service, verify clean startup.)
6. **Audit:** review `git log` of repos they had access to and `hivemind.audit_log` for the last 90 days for anomalies.

## Local copies (best-effort, documented)
7. Send written instruction to delete local clones and any local Tier 3 data; record acknowledgement. (Git gives no remote wipe — assume they retain what they cloned; rotation in step 5 limits the blast radius.)

## Per-client unassignment (not a full departure)
- Only steps 1 (specific team) and 3 (specific `client_access` rows). No credential rotation unless they held client secrets.

## Verification (must pass)
- [ ] User can no longer `git clone`/`pull` any `client-*` repo.
- [ ] `search_kb` under their identity returns zero rows.
- [ ] Rotated secrets confirmed live; old ones rejected.
