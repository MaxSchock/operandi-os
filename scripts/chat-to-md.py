#!/usr/bin/env python3
"""Convert a Claude Code session JSONL into a markdown file for the Obsidian vault.

Usage: chat-to-md.py <jsonl_path> <output_dir>

Output filename: YYYY-MM-DD-<session-id-8>-<project-tag>.md

Redacts common secret prefixes before writing.
"""
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone


SECRET_PATTERNS = [
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"), "sk-ant-***REDACTED***"),
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "sk-***REDACTED***"),
    (re.compile(r"ghp_[A-Za-z0-9]{30,}"), "ghp_***REDACTED***"),
    (re.compile(r"gho_[A-Za-z0-9]{30,}"), "gho_***REDACTED***"),
    (re.compile(r"AIza[A-Za-z0-9_-]{30,}"), "AIza***REDACTED***"),
    (re.compile(r"xox[bpars]-[A-Za-z0-9-]{20,}"), "xox***REDACTED***"),
    (re.compile(r"eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"), "eyJ***JWT-REDACTED***"),
    (re.compile(r"(?i)(api[_-]?key|token|secret|password|passphrase)\s*[=:]\s*['\"]?[A-Za-z0-9_/+=.-]{16,}['\"]?"), r"\1=***REDACTED***"),
    (re.compile(r"access_token=[A-Za-z0-9_.-]+"), "access_token=***REDACTED***"),
    (re.compile(r"refresh_token=[A-Za-z0-9_.-]+"), "refresh_token=***REDACTED***"),
]


def redact(text):
    if not isinstance(text, str):
        return text
    for pattern, replacement in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def project_tag_from_path(jsonl_path):
    parent = Path(jsonl_path).parent.name
    cleaned = parent.lstrip("-").replace("--", "/").replace("-", "/")
    parts = cleaned.split("/")
    parts = [p for p in parts if p and p not in ("home", "max", "mnt", "c", "Users", "PC")]
    if parts:
        return "-".join(parts)
    return "home"


def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks = []
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                chunks.append(block.get("text", ""))
            elif btype == "tool_use":
                name = block.get("name", "?")
                input_repr = json.dumps(block.get("input", {}), ensure_ascii=False)
                if len(input_repr) > 300:
                    input_repr = input_repr[:300] + "...(truncated)"
                chunks.append(f"[tool_use {name}({input_repr})]")
            elif btype == "tool_result":
                tool_id = block.get("tool_use_id", "?")[:8]
                result_content = block.get("content", "")
                result_text = extract_text(result_content) if not isinstance(result_content, str) else result_content
                if len(result_text) > 500:
                    result_text = result_text[:500] + "...(truncated)"
                chunks.append(f"[tool_result for {tool_id}: {result_text}]")
        return "\n".join(chunks)
    return ""


def convert(jsonl_path, output_dir):
    jsonl_path = Path(jsonl_path)
    if not jsonl_path.exists():
        print(f"ERROR: {jsonl_path} does not exist", file=sys.stderr)
        return None

    project_tag = project_tag_from_path(jsonl_path)
    session_id = jsonl_path.stem
    session_short = session_id[:8]

    turns = []
    first_ts = None
    last_ts = None
    tools_used = set()

    with open(jsonl_path, "r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            event_type = event.get("type")
            ts = event.get("timestamp")
            if ts:
                if first_ts is None:
                    first_ts = ts
                last_ts = ts

            if event_type == "user":
                msg = event.get("message", {})
                text = extract_text(msg.get("content", ""))
                if text.strip():
                    turns.append(("user", text, ts))
            elif event_type == "assistant":
                msg = event.get("message", {})
                content = msg.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_use":
                            tools_used.add(block.get("name", "?"))
                text = extract_text(content)
                if text.strip():
                    turns.append(("assistant", text, ts))

    if not turns:
        print(f"WARN: {jsonl_path} produced no turns; skipping", file=sys.stderr)
        return None

    if first_ts:
        try:
            dt = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
        except Exception:
            date_str = datetime.fromtimestamp(jsonl_path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
    else:
        date_str = datetime.fromtimestamp(jsonl_path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")

    out_name = f"{date_str}-{session_short}-{project_tag}.md"
    out_path = Path(output_dir) / out_name
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("---")
    lines.append("type: chat-history")
    lines.append(f"date: {date_str}")
    lines.append(f"project: {project_tag}")
    lines.append(f"session_id: {session_id}")
    lines.append(f"first_ts: {first_ts or 'unknown'}")
    lines.append(f"last_ts: {last_ts or 'unknown'}")
    lines.append(f"turns: {len(turns)}")
    lines.append(f"tools_used: [{', '.join(sorted(tools_used))}]")
    lines.append("tags: [chat-history, source/claude-code]")
    lines.append("---")
    lines.append("")
    lines.append(f"# {date_str} · {project_tag} · {session_short}")
    lines.append("")

    for idx, (role, text, ts) in enumerate(turns, 1):
        ts_short = ts[:19] if ts else "?"
        lines.append(f"## Turn {idx} · {role} · {ts_short}")
        lines.append("")
        lines.append(redact(text))
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def main():
    if len(sys.argv) < 3:
        print("Usage: chat-to-md.py <jsonl_path> <output_dir>", file=sys.stderr)
        sys.exit(1)
    result = convert(sys.argv[1], sys.argv[2])
    if result:
        print(str(result))


if __name__ == "__main__":
    main()
