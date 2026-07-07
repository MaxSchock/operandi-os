# Records of Processing Activities (Art. 30 GDPR)
# Verzeichnis von Verarbeitungstätigkeiten — Project Hivemind

Controller: **KIsult** (Verantwortlicher). Maintained by: ______________. Last updated: ______________.

Fill the blanks with counsel before go-live. One processing activity per section.

---

## Activity 1 — Team knowledge base (shared client work)
- **Purpose (Zweck):** store and retrieve client project artifacts and summaries so assigned team members can collaborate.
- **Categories of data subjects:** client contacts (B2B), KIsult employees.
- **Categories of personal data:** business contact details, project content, author identity. (No special-category data.)
- **Recipients:** assigned KIsult team members only (per-client access control).
- **Sub-processors:**
  - Hetzner Online GmbH (hosting `ki-prod-01`, Falkenstein/DE) — AVV ref: ______
  - Contabo GmbH (hosting `VpsFigura`, DE) — a periodic rsync mirrors the operator's
    gitignored client data (incl. client names) WSL↔VpsFigura for the Strategist.
    This is a **second storage location of client PII** beyond ki-prod-01. AVV ref: ______
  - Anthropic (LLM via Claude Code) — DPA status: ______ (see README)
- **Third-country transfer:** storage none (EEA/DE). LLM prompts: depends on Anthropic posture — document here: ______
- **Retention (Löschfrist):** Tier 2 artifacts/summaries: ____ (proposed: project end + 12 months). Audit logs: ____ (proposed: 12 months).
- **Technical/organisational measures (TOMs):** TLS in transit; disk encryption at rest; SSH-key-only auth; Forgejo team ACL; pgvector RLS by `client_id`; pre-commit secret/PII gate; per-machine local-only Tier 3.

## Activity 2 — Session summaries (EOD pipeline)
- **Purpose:** capture decisions/artifacts/next-steps per work session for team continuity.
- **Data:** LLM-generated summary text, author, client_id, timestamp. **No raw transcripts.**
- **Recipients / sub-processors / transfer / TOMs:** as Activity 1.
- **Retention:** ____ (proposed: align with Activity 1).
- **Note:** raw transcripts remain local (Tier 3) and are out of scope of this shared processing.

## Activity 3 — Access & audit logging
- **Purpose:** demonstrate accountability (Art. 5(2)); detect/limit unauthorized access.
- **Data:** user_id, action, client_id, timestamp (Forgejo git history + `hivemind.audit_log`).
- **Retention:** ____ (proposed: 12 months).
- **Recipients:** KIsult admins only.

---

## Data subject rights — handling
- **Access (Art. 15) / Portability (Art. 20):** export from `hivemind.documents` (SQL by `client_id`/subject) + relevant Forgejo files.
- **Erasure (Art. 17):** delete rows by `client_id`/subject in pgvector; for git, delete or history-rewrite the per-client repo. Log the deletion in `audit_log`.
- **Rectification (Art. 16):** update the row/file; commit recorded in history.
- **Responsible person / SLA:** ______________ / ____ days.

## DPIA (Art. 35)
Assess whether a DPIA is required (likely yes if scale/monitoring grows). Trigger review when: team > 8, special-category clients onboarded, or systematic access monitoring added. DPIA file: ______________.
