#!/bin/bash
# PostToolUse hook (Edit|Write): flag skill changes for sync on next wrap-up.
# Referenced by .claude/settings.json. Previously missing -> the hook errored on
# every Edit/Write. This is an intentionally minimal, no-op-safe implementation.
#
# Behaviour: if an edited path lives under .claude/skills/, drop a marker file so
# /wrap-up can pick it up. Never blocks, never fails the tool call.

set +e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MARKER="$REPO_ROOT/.claude/.skills-dirty"

# Claude passes hook context as JSON on stdin; we only need the file path(s).
payload="$(cat 2>/dev/null)"

if printf '%s' "$payload" | grep -q '.claude/skills/'; then
    touch "$MARKER" 2>/dev/null
fi

exit 0
