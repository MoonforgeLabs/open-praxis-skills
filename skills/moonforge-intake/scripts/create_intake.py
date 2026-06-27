#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_INBOX = Path("/Users/alex/Documents/myWork/openCode/moonforge/radar-intake/inbox/openhuman")
VALID_VISIBILITY = {"public-core", "public-extension", "private-config", "private-knowledge", "sensitive-secret"}
VALID_ACTIONS = {"keep", "template", "redact", "extract-interface", "move-private", "discard"}


def slugify(value: str, fallback: str = "intake") -> str:
    value = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", value).strip("-").lower()
    return value[:80] or fallback


def parse_tags(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a Moonforge intake item from OpenHuman capture.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--type", default="idea", choices=["link", "idea", "task", "document", "project", "reminder", "observation"])
    parser.add_argument("--content", default="")
    parser.add_argument("--url", default="")
    parser.add_argument("--source", default="openhuman")
    parser.add_argument("--tags", default="")
    parser.add_argument("--radar-board", default="Knowledge Intake Radar")
    parser.add_argument("--visibility", default="private-knowledge", choices=sorted(VALID_VISIBILITY))
    parser.add_argument("--open-source-action", default="move-private", choices=sorted(VALID_ACTIONS))
    parser.add_argument("--destination", default="moonforge-inbox")
    parser.add_argument("--next-action", default="triage")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_INBOX)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    captured_at = datetime.now(timezone.utc).isoformat()
    item = {
        "schemaVersion": 1,
        "kind": "moonforge.intake.openhuman",
        "source": args.source,
        "captured_at": captured_at,
        "type": args.type,
        "title": args.title,
        "content": args.content,
        "url": args.url or None,
        "tags": parse_tags(args.tags),
        "radar_board": args.radar_board,
        "visibility": args.visibility,
        "open_source_action": args.open_source_action,
        "destination": args.destination,
        "next_action": args.next_action,
        "status": "new",
    }
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = out_dir / f"{stamp}-{slugify(args.title)}.json"
    path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(path), "item": item}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
