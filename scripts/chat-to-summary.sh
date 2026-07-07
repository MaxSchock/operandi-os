#!/bin/bash
# Hook Stop wrapper: feed the current project's most recent Claude Code session
# to chat-to-summary.py. Registered in ~/.claude/settings.json by
# install-hivemind.sh (Hivemind team mode).
# Async-safe: never blocks session close. The raw transcript stays local; only
# an LLM summary is indexed into the shared KB (see chat-to-summary.py).

set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECTS_DIR="$HOME/.claude/projects"

# Per-user Hivemind config (DSN, user id, API keys). Single source of truth.
ENV_FILE="$HOME/.claude/hivemind.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
fi

# Scope the lookup to THIS project's transcript directory (Claude Code maps the
# cwd to a dir name by replacing non-alphanumerics with '-'). Prevents pairing
# another project's session with this cwd's client_id.
proj_slug="$(pwd | sed 's#[^a-zA-Z0-9]#-#g')"
proj_dir="$PROJECTS_DIR/$proj_slug"
[ -d "$proj_dir" ] || { echo "[chat-to-summary] No transcript dir for this project ($proj_dir); skipping." >&2; exit 0; }

# Newest JSONL, portable (no GNU find -printf; works on macOS too).
latest="$(ls -t "$proj_dir"/*.jsonl 2>/dev/null | head -1)"
[ -z "$latest" ] && { echo "[chat-to-summary] No JSONL in $proj_dir." >&2; exit 0; }

# Only act on sessions touched in the last 10 minutes.
recent="$(find "$latest" -mmin -10 2>/dev/null)"
[ -z "$recent" ] && { echo "[chat-to-summary] Last session older than 10min; skipping." >&2; exit 0; }

# stderr flows through so the user sees "Indexed summary" / outbox notices.
python3 "$SCRIPT_DIR/chat-to-summary.py" "$latest" >/dev/null \
    || echo "[chat-to-summary] summary step failed for $latest (non-fatal)." >&2

exit 0
