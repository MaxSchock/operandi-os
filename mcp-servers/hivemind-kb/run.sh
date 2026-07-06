#!/bin/bash
# Launcher for the hivemind-kb MCP server. Sources the per-user Hivemind env
# (~/.claude/hivemind.env, written by scripts/install-hivemind.sh) so that
# .mcp.json never has to carry the DSN or any key. Single source of truth.

ENV_FILE="$HOME/.claude/hivemind.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/server.py"
