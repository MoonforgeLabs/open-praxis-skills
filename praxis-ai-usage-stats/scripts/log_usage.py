#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

LOG_PATHS = {
    "skill": "~/.codex/skill-usage.log",
    "agent": "~/.codex/agent-usage.log",
    "tool": "~/.codex/tool-usage.log",
}


def clean_field(value: str) -> str:
    return " ".join(value.replace("\t", " ").split())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append one Codex usage event to a local usage log.")
    parser.add_argument("--kind", required=True, choices=sorted(LOG_PATHS), help="Usage kind to record")
    parser.add_argument("--name", required=True, help="Skill, agent, or tool name")
    parser.add_argument("--context", default="", help="Short non-sensitive context")
    parser.add_argument("--log-path", default="", help="Override destination log path")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    destination = Path(args.log_path or LOG_PATHS[args.kind]).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    line = f"{timestamp}\t{clean_field(args.name)}\t{clean_field(args.context)}\n"
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(line)
    print(f"logged {args.kind}: {args.name} -> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
