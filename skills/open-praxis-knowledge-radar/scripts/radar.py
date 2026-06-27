#!/usr/bin/env python3
"""Append, list, update, and export Alex reading radar JSONL records."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VALID_STATUSES = {"inbox", "next", "active", "learning", "learned", "applied", "waiting", "done", "archived"}
VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}

# GitHub URL patterns to extract from article content
_GITHUB_REPO_PATTERN = re.compile(r'https?://github\.com/([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)')
_GITHUB_URL_FULL = re.compile(r'https?://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+(?:/[^\s<>"\')\]]*)?')


def fetch_url_content(url: str, max_chars: int = 8000) -> str | None:
    """Fetch URL content for extraction. Handles YouTube/Bilibili specially."""
    # YouTube: fetch transcript via yt-dlp
    if "youtube.com/watch" in url or "youtu.be/" in url:
        return _fetch_youtube_transcript(url, max_chars)

    # Bilibili: fetch via bili CLI
    if "bilibili.com/video" in url or "b23.tv/" in url:
        return _fetch_bilibili_info(url, max_chars)

    # Generic webpage
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,*/*",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:max_chars]
    except Exception:
        return None


def _fetch_youtube_transcript(url: str, max_chars: int) -> str | None:
    """Fetch YouTube video transcript via yt-dlp."""
    if not shutil.which("yt-dlp"):
        return None
    try:
        # Get video info + auto-generated subtitles
        proc = subprocess.run(
            ["yt-dlp", "--write-auto-sub", "--skip-download", "--print", "%(title)s\n%(description)s",
             "--sub-lang", "en,zh-Hans,zh", "--sub-format", "vtt", "-o", "/tmp/praxis-yt-sub"],
            capture_output=True, text=True, timeout=30,
        )
        title_desc = proc.stdout.strip()

        # Read downloaded subtitle file if any
        subtitle_text = ""
        for sub_file in ["/tmp/praxis-yt-sub.en.vtt", "/tmp/praxis-yt-sub.zh-Hans.vtt",
                         "/tmp/praxis-yt-sub.zh.vtt", "/tmp/praxis-yt-sub.zhs.vtt"]:
            if os.path.exists(sub_file):
                with open(sub_file, "r", encoding="utf-8") as f:
                    raw = f.read()
                # Strip VTT formatting
                lines = []
                for line in raw.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("WEBVTT") and not line.startswith("Kind:") \
                            and not line.startswith("Language:") and "-->" not in line \
                            and not re.match(r'^\d+$', line):
                        lines.append(line)
                subtitle_text = " ".join(lines)
                os.remove(sub_file)
                break

        result = title_desc
        if subtitle_text:
            result += "\n\n字幕:\n" + subtitle_text
        return result[:max_chars] if result else None
    except Exception:
        return None


def _fetch_bilibili_info(url: str, max_chars: int) -> str | None:
    """Fetch Bilibili video info via bili CLI."""
    if not shutil.which("bili"):
        return None
    try:
        # Extract BV id from URL
        bv_match = re.search(r'(BV[a-zA-Z0-9]+)', url)
        if not bv_match:
            return None
        bvid = bv_match.group(1)
        proc = subprocess.run(
            ["bili", "info", bvid, "-f", "json"],
            capture_output=True, text=True, timeout=15,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            data = json.loads(proc.stdout)
            title = data.get("title", "")
            desc = data.get("desc", "")
            return f"{title}\n{desc}"[:max_chars]
        return None
    except Exception:
        return None


def extract_github_refs(text: str) -> list[str]:
    """Extract unique GitHub repository URLs from text."""
    repos = set()
    for match in _GITHUB_REPO_PATTERN.finditer(text):
        repo = match.group(1)
        repos.add(f"https://github.com/{repo}")
    return sorted(repos)


def extract_title_from_content(url: str, content: str) -> str:
    """Try to extract a meaningful title from fetched content."""
    # Look for common title patterns
    patterns = [
        re.compile(r'(?:^|\s)([A-Z][^\n.]{10,80})(?:\n|\. )'),  # First sentence
    ]
    # Try og:title or <title> from original HTML (not stripped)
    title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
        if 5 < len(title) < 200:
            return title

    # Use URL path as fallback
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.rstrip("/")
    if path:
        segment = path.split("/")[-1]
        segment = segment.replace("-", " ").replace("_", " ").replace(".html", "").replace(".md", "")
        if len(segment) > 5:
            return segment.title()
    return parsed.netloc


def default_store() -> Path:
    configured = os.getenv("PRAXIS_KNOWLEDGE_RADAR_STORE") or os.getenv("PRAXIS_KNOWLEDGE_RADAR_STORE")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".praxis-skills" / "data" / "knowledge-radar" / "tasks.jsonl"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def read_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise SystemExit(f"Invalid JSON on line {line_number}: {error}") from error
    return records


def write_records(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def append_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def cmd_add(args: argparse.Namespace) -> None:
    if args.status not in VALID_STATUSES:
        raise SystemExit(f"Invalid status: {args.status}")
    if args.priority not in VALID_PRIORITIES:
        raise SystemExit(f"Invalid priority: {args.priority}")

    timestamp = now_iso()
    refs = split_csv(args.references)

    # Auto-fetch content and extract GitHub links if URL provided
    content_summary = ""
    github_refs = []
    auto_title = args.title

    # 使用外部提供的摘要（如果有）
    if hasattr(args, 'summary') and args.summary:
        content_summary = args.summary

    if refs and not args.no_fetch:
        url = refs[0]
        if url.startswith("http"):
            # 如果没有外部摘要，自动抓取
            if not content_summary:
                print(f"  📥 抓取内容: {url[:80]}...", file=sys.stderr)
                content = fetch_url_content(url)
                if content:
                    content_summary = content[:500]
                    github_refs = extract_github_refs(content)
                    if args.title == url or args.title == "auto":
                        auto_title = extract_title_from_content(url, content) or url
                    if github_refs:
                        print(f"  🔗 发现 {len(github_refs)} 个 GitHub 工程: {', '.join(github_refs[:5])}", file=sys.stderr)
            else:
                # 有外部摘要时，仍然提取 GitHub refs
                content = fetch_url_content(url)
                if content:
                    github_refs = extract_github_refs(content)

    # Merge original URL + GitHub refs into references
    all_refs = refs + github_refs
    # Deduplicate while preserving order
    seen = set()
    unique_refs = []
    for r in all_refs:
        if r not in seen:
            seen.add(r)
            unique_refs.append(r)

    # Auto-guess area from content
    area = args.area
    if area == "auto" or not area:
        combined = f"{' '.join(unique_refs)} {content_summary} {args.notes or ''}".lower()
        area = _guess_area(combined)

    record = {
        "id": args.id or str(uuid.uuid4())[:8],
        "title": auto_title,
        "status": args.status,
        "priority": args.priority,
        "area": area,
        "source": args.source,
        "tags": split_csv(args.tags),
        "references": unique_refs,
        "github_repos": github_refs,
        "content_summary": content_summary,
        "notes": args.notes or "",
        "next_action": args.next_action or "",
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    append_record(args.store, record)
    print(json.dumps(record, ensure_ascii=False, indent=2))


def _guess_area(text: str) -> str:
    """Guess area from text content."""
    area_keywords = {
        "code-understanding": ["code", "github", "programming", "developer", "api", "sdk"],
        "ai-os": ["ai", "agent", "llm", "gpt", "claude", "model", "prompt"],
        "search-skills": ["search", "skill", "claude code", "cursor", "codex"],
        "skill-ecosystem": ["skill", "plugin", "extension", "marketplace"],
        "business-skills": ["business", "marketing", "sales", "product", "变现"],
        "stocks": ["stock", "invest", "trading", "finance", "股票", "投资"],
        "design-tools": ["design", "ui", "ux", "figma", "css"],
        "content-distribution": ["content", "social", "media", "video", "tiktok", "内容"],
        "rag-docs": ["rag", "document", "knowledge", "embedding", "vector"],
    }
    for area, keywords in area_keywords.items():
        if any(kw in text for kw in keywords):
            return area
    return "inbox"


def cmd_list(args: argparse.Namespace) -> None:
    statuses = set(split_csv(args.status)) if args.status else set()
    areas = set(split_csv(args.area)) if args.area else set()
    records = read_records(args.store)
    if statuses:
        records = [record for record in records if record.get("status") in statuses]
    if areas:
        records = [record for record in records if record.get("area") in areas]
    records = sorted(records, key=lambda item: item.get("updated_at", ""), reverse=True)
    if args.limit:
        records = records[: args.limit]
    if args.json:
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return
    for record in records:
        tags = ",".join(record.get("tags", []))
        print(f"[{record.get('status')}] {record.get('priority')} {record.get('id')} {record.get('area')} :: {record.get('title')}" + (f" #{tags}" if tags else ""))
        if record.get("next_action"):
            print(f"  next: {record['next_action']}")


def cmd_update(args: argparse.Namespace) -> None:
    records = read_records(args.store)
    matched = False
    for record in records:
        if record.get("id") != args.id:
            continue
        matched = True
        if args.status:
            if args.status not in VALID_STATUSES:
                raise SystemExit(f"Invalid status: {args.status}")
            record["status"] = args.status
        if args.priority:
            if args.priority not in VALID_PRIORITIES:
                raise SystemExit(f"Invalid priority: {args.priority}")
            record["priority"] = args.priority
        if args.next_action is not None:
            record["next_action"] = args.next_action
        if args.notes is not None:
            record["notes"] = args.notes
        if args.tags is not None:
            record["tags"] = split_csv(args.tags)
        record["updated_at"] = now_iso()
    if not matched:
        raise SystemExit(f"No task found with id: {args.id}")
    write_records(args.store, records)


def cmd_export_md(args: argparse.Namespace) -> None:
    records = read_records(args.store)
    statuses = ["active", "next", "inbox", "waiting", "done", "archived"]
    print("# Alex Task Radar\n")
    for status in statuses:
        group = [record for record in records if record.get("status") == status]
        if not group:
            continue
        print(f"## {status}\n")
        for record in sorted(group, key=lambda item: (item.get("priority", "P2"), item.get("updated_at", ""))):
            print(f"- **{record.get('priority')}** `{record.get('id')}` [{record.get('area')}] {record.get('title')}")
            if record.get("next_action"):
                print(f"  - Next: {record['next_action']}")
            if record.get("references"):
                print(f"  - References: {', '.join(record['references'])}")
        print()


def cmd_seed_mainlines(args: argparse.Namespace) -> None:
    seed_path = Path(__file__).resolve().parent.parent / "references" / "initial-mainlines.json"
    seeds = json.loads(seed_path.read_text(encoding="utf-8"))
    existing = read_records(args.store)
    existing_titles = {record.get("title") for record in existing}
    created = []
    timestamp = now_iso()
    for seed in seeds:
        if seed["title"] in existing_titles:
            continue
        record = {
            "id": str(uuid.uuid4())[:8],
            "title": seed["title"],
            "status": args.status,
            "priority": seed.get("priority", args.priority),
            "area": seed["area"],
            "source": "seed-mainlines",
            "tags": seed.get("tags", []),
            "references": seed.get("references", []),
            "notes": "Seeded from praxis-knowledge-radar initial mainlines.",
            "next_action": "拆成可执行的下一步。",
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        append_record(args.store, record)
        created.append(record)
    print(json.dumps({"created": len(created), "skipped": len(seeds) - len(created), "records": created}, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=default_store())
    subparsers = parser.add_subparsers(required=True)

    add = subparsers.add_parser("add", help="Add a radar task")
    add.add_argument("--title", default="auto", help="Title (auto-extracted from URL if not provided)")
    add.add_argument("--area", default="", help="Area (auto-guessed if empty)")
    add.add_argument("--source", default="manual")
    add.add_argument("--status", default="inbox")
    add.add_argument("--priority", default="P2")
    add.add_argument("--tags")
    add.add_argument("--references", help="URL(s), comma-separated")
    add.add_argument("--notes")
    add.add_argument("--summary", help="Content summary (auto-fetched if not provided)")
    add.add_argument("--next-action")
    add.add_argument("--id")
    add.add_argument("--no-fetch", action="store_true", help="Don't auto-fetch URL content")
    add.set_defaults(func=cmd_add)

    list_cmd = subparsers.add_parser("list", help="List radar tasks")
    list_cmd.add_argument("--status", help="Comma-separated statuses")
    list_cmd.add_argument("--area", help="Comma-separated areas")
    list_cmd.add_argument("--limit", type=int, default=0)
    list_cmd.add_argument("--json", action="store_true")
    list_cmd.set_defaults(func=cmd_list)

    update = subparsers.add_parser("update", help="Update a radar task")
    update.add_argument("id")
    update.add_argument("--status")
    update.add_argument("--priority")
    update.add_argument("--tags")
    update.add_argument("--notes")
    update.add_argument("--next-action")
    update.set_defaults(func=cmd_update)

    export = subparsers.add_parser("export-md", help="Export Markdown summary")
    export.set_defaults(func=cmd_export_md)

    seed = subparsers.add_parser("seed-mainlines", help="Seed Alex's initial mainline tasks")
    seed.add_argument("--status", default="inbox")
    seed.add_argument("--priority", default="P2")
    seed.set_defaults(func=cmd_seed_mainlines)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
