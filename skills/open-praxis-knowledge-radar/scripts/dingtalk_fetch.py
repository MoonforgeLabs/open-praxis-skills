#!/usr/bin/env python3
"""钉钉消息拉取 — 从钉钉群提取 URL 并入库到 knowledge-radar

用法:
    python3 dingtalk_fetch.py                    # 拉取最近消息
    python3 dingtalk_fetch.py --since 2h         # 拉取最近 2 小时
    python3 dingtalk_fetch.py --chat-id xxx      # 指定群
    python3 dingtalk_fetch.py --dry-run           # 只提取不入库

配置:
    设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
    或创建 ~/.praxis-skills/data/knowledge-radar/dingtalk-config.json:
    {"app_key": "...", "app_secret": "...", "chat_id": "..."}
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# 确保 Path 可用
Path = Path

CONFIG_PATH = Path.home() / ".praxis-skills" / "data" / "knowledge-radar" / "dingtalk-config.json"
RADAR_SCRIPT = Path(__file__).parent / "radar.py"
DINGTALK_API = "https://api.dingtalk.com/v1.0"


def load_config() -> dict[str, str]:
    """Load DingTalk config from file or env vars."""
    config = {}
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            config = json.load(f)
    config["app_key"] = os.getenv("DINGTALK_APP_KEY", config.get("app_key", ""))
    config["app_secret"] = os.getenv("DINGTALK_APP_SECRET", config.get("app_secret", ""))
    config["chat_id"] = os.getenv("DINGTALK_CHAT_ID", config.get("chat_id", ""))
    if not config["app_key"] or not config["app_secret"]:
        print("❌ 缺少钉钉配置。请设置:", file=sys.stderr)
        print(f"   方式 1: export DINGTALK_APP_KEY=... DINGTALK_APP_SECRET=...", file=sys.stderr)
        print(f"   方式 2: 编辑 {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    return config


def get_access_token(app_key: str, app_secret: str) -> str:
    """Get DingTalk access token."""
    url = f"{DINGTALK_API}/oauth2/accessToken"
    data = json.dumps({"appKey": app_key, "appSecret": app_secret}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
    return result.get("accessToken", "")


def fetch_messages(token: str, chat_id: str, since_hours: int = 24) -> list[dict[str, Any]]:
    """Fetch messages from a DingTalk group chat."""
    url = f"{DINGTALK_API}/orgGroupChat/messages"
    params = {
        "chatBotId": chat_id,
        "startTime": int((datetime.now(timezone.utc) - timedelta(hours=since_hours)).timestamp() * 1000),
        "endTime": int(datetime.now(timezone.utc).timestamp() * 1000),
        "maxResults": 100,
    }
    req = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(params)}",
        headers={"x-acs-dingtalk-access-token": token, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read()).get("messages", [])
    except urllib.error.HTTPError as e:
        print(f"⚠️  钉钉 API 错误: {e.code} {e.read().decode()[:200]}", file=sys.stderr)
        return []


def _get_group_members(chat_id: str) -> dict[str, str]:
    """Get group member nicknames mapping (openDingtalkId -> memberGroupNick)."""
    import subprocess

    try:
        cmd = ["dws", "chat", "group", "members", "list", "--id", chat_id, "--format", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return {}

        data = json.loads(result.stdout)
        if not data.get("success"):
            return {}

        members = data.get("result", {}).get("list", [])
        # 建立 openDingtalkId -> memberGroupNick 的映射
        nick_map = {}
        for member in members:
            open_id = member.get("openDingtalkId", "")
            group_nick = member.get("memberGroupNick", "")
            member_nick = member.get("memberNick", "")
            # 优先使用群昵称，其次使用成员昵称
            nick_map[open_id] = group_nick if group_nick else member_nick

        return nick_map

    except Exception:
        return {}


def fetch_chat_messages(token: str, chat_id: str, since_hours_or_time: int | str = 24) -> list[dict[str, Any]]:
    """Fetch messages from a DingTalk group using dws CLI tool.

    Args:
        token: DingTalk access token (unused, kept for compatibility)
        chat_id: Group chat ID
        since_hours_or_time: Either an integer (hours) or a string (datetime like "2026-06-27 10:00:00")
    """
    import subprocess

    try:
        # 确定开始时间
        if isinstance(since_hours_or_time, str) and "-" in since_hours_or_time:
            # 直接传入的时间字符串
            start_str = since_hours_or_time
        else:
            # 传入的是小时数
            since_hours = int(since_hours_or_time)
            from datetime import datetime, timedelta, timezone
            start_time = datetime.now(timezone(timedelta(hours=8))) - timedelta(hours=since_hours)
            start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")

        # 使用 dws CLI 工具获取消息
        cmd = [
            "dws", "chat", "message", "list",
            "--group", chat_id,
            "--time", start_str,
            "--limit", "100",
            "--format", "json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"⚠️  dws 命令失败: {result.stderr[:200]}", file=sys.stderr)
            return []

        data = json.loads(result.stdout)
        if not data.get("success"):
            print(f"⚠️  dws 返回错误: {data.get('errorMsg', 'Unknown')}", file=sys.stderr)
            return []

        messages = data.get("result", {}).get("messages", [])

        # 获取群成员昵称映射
        nick_map = _get_group_members(chat_id)

        # 为每条消息添加昵称信息
        for msg in messages:
            sender_id = msg.get("senderOpenDingTalkId", "")
            msg["senderNick"] = nick_map.get(sender_id, msg.get("sender", ""))

        print(f"✅ 使用 dws CLI 获取到 {len(messages)} 条消息", file=sys.stderr)
        return messages

    except subprocess.TimeoutExpired:
        print("⚠️  dws 命令超时", file=sys.stderr)
        return []
    except Exception as e:
        print(f"⚠️  dws 命令异常: {e}", file=sys.stderr)
        return []


def extract_urls_from_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Extract URLs and context from DingTalk messages."""
    url_pattern = re.compile(r'https?://[^\s<>"\')\]]+')
    results = []
    seen = set()

    for msg in messages:
        content = msg.get("content", "")
        # 优先使用群昵称（senderNick），其次使用 sender
        sender = msg.get("senderNick", msg.get("sender", msg.get("senderId", "unknown")))
        msg_id = msg.get("openMessageId", msg.get("msgId", ""))
        timestamp = msg.get("createTime", msg.get("createAt", 0))

        # Parse content (may be JSON string for rich messages)
        try:
            content_obj = json.loads(content)
            if isinstance(content_obj, dict):
                content = content_obj.get("content", content_obj.get("text", content))
        except (json.JSONDecodeError, TypeError):
            pass

        # Extract URLs
        for url in url_pattern.findall(str(content)):
            # Clean up URL
            url = url.rstrip(".,;:!?")
            if url not in seen:
                seen.add(url)
                results.append({
                    "url": url,
                    "source": "dingtalk",
                    "sender": sender,
                    "msg_id": msg_id,
                    "timestamp": timestamp,
                    "raw_text": str(content)[:200],
                })

    return results


def _mask_username(username: str) -> str:
    """Mask username for privacy protection."""
    if not username:
        return "user"
    # 保留最后一个字符，其余用 * 替换
    if len(username) <= 2:
        return "*" + username[-1]
    return "*" * (len(username) - 1) + username[-1]


def _extract_summary_from_message(raw_text: str) -> str:
    """Extract summary from DingTalk message content."""
    if not raw_text:
        return ""

    # 移除 URL 部分
    text = re.sub(r'https?://[^\s]+', '', raw_text)

    # 移除 [分享] 等前缀
    text = re.sub(r'^\[分享\]\s*', '', text)

    # 移除来源标识（如 "- 今日头条"）
    text = re.sub(r'\s*-\s*(今日头条|微信|微博|知乎|豆瓣|B站|bilibili|YouTube|GitHub)\s*', '', text)

    # 移除 "全文约 XXX 字" 等
    text = re.sub(r'全文约\s*\d+\s*字[，,]?\s*', '', text)

    # 清理多余空白
    text = re.sub(r'\s+', ' ', text).strip()

    # 限制长度
    if len(text) > 300:
        text = text[:297] + "..."

    return text


def _fetch_url_summary(url: str) -> str:
    """Fetch URL content and extract summary."""
    try:
        import subprocess
        # 使用 curl 获取页面内容（限制大小和时间）
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "10", "--max-filesize", "1048576", url],
            capture_output=True, text=True, timeout=15
        )

        if result.returncode != 0:
            return ""

        html_content = result.stdout

        # 提取 <title> 标签
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""

        # 提取 meta description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html_content, re.IGNORECASE)
        if not desc_match:
            desc_match = re.search(r'<meta[^>]*content=["\'](.*?)["\'][^>]*name=["\']description["\']', html_content, re.IGNORECASE)
        description = desc_match.group(1).strip() if desc_match else ""

        # 提取 og:description
        og_desc_match = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\'](.*?)["\']', html_content, re.IGNORECASE)
        if not og_desc_match:
            og_desc_match = re.search(r'<meta[^>]*content=["\'](.*?)["\'][^>]*property=["\']og:description["\']', html_content, re.IGNORECASE)
        og_description = og_desc_match.group(1).strip() if og_desc_match else ""

        # 优先使用 og:description，其次 description，最后 title
        summary = og_description or description or title

        # 清理 HTML 实体和多余空白
        summary = re.sub(r'&[a-zA-Z]+;', ' ', summary)
        summary = re.sub(r'&#\d+;', ' ', summary)
        summary = re.sub(r'\s+', ' ', summary).strip()

        # 限制长度
        if len(summary) > 300:
            summary = summary[:297] + "..."

        return summary

    except Exception:
        return ""


def _load_existing_urls() -> set[str]:
    """Load existing URLs from tasks.jsonl for deduplication."""
    existing_urls = set()
    tasks_file = Path.home() / ".praxis-skills" / "data" / "knowledge-radar" / "tasks.jsonl"

    if not tasks_file.exists():
        return existing_urls

    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        task = json.loads(line)
                        refs = task.get("references", [])
                        for ref in refs:
                            # 提取 URL 的基础部分（去除查询参数）
                            base_url = ref.split("?")[0] if "?" in ref else ref
                            existing_urls.add(base_url)
                            existing_urls.add(ref)
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass

    return existing_urls


def ingest_to_radar(url_entry: dict[str, str], dry_run: bool = False, existing_urls: set[str] | None = None) -> bool:
    """Add a URL entry to the reading radar."""
    url = url_entry["url"]

    # 去重检查
    base_url = url.split("?")[0] if "?" in url else url
    if existing_urls and (url in existing_urls or base_url in existing_urls):
        print(f"  ⏭️  跳过（已存在）: {url[:60]}...", file=sys.stderr)
        return False

    source = url_entry.get("source", "dingtalk")
    sender = url_entry.get("sender", "")
    raw_text = url_entry.get("raw_text", "")

    # Build radar entry
    title = _extract_title_from_url(url)
    area = _guess_area(url, raw_text)
    tags = ["dingtalk", "auto-capture"]
    if sender:
        tags.append(f"from:{_mask_username(sender)}")

    # 脱敏处理用户名
    masked_sender = _mask_username(sender) if sender else "user"

    # 优先从消息内容中提取摘要，其次从 URL 抓取
    summary = _extract_summary_from_message(raw_text)
    if not summary:
        summary = _fetch_url_summary(url)

    if summary:
        print(f"  📝 摘要: {summary[:60]}...", file=sys.stderr)

    # 尝试从消息内容中提取更好的标题
    if raw_text and (title == url or len(title) < 10 or title.isdigit()):
        # 尝试提取 [分享] 后面的标题
        title_match = re.search(r'\[分享\]\s*(.*?)(?:\s*-\s*(?:今日头条|微信|微博|知乎|豆瓣|B站|bilibili|YouTube|GitHub)\s*$)', raw_text)
        if not title_match:
            title_match = re.search(r'\[分享\]\s*(.*?)(?:\s*https?://|$)', raw_text)
        if title_match:
            extracted_title = title_match.group(1).strip()
            # 清理标题中的多余信息
            extracted_title = re.sub(r'\s*全文约\s*\d+\s*字.*$', '', extracted_title)
            if len(extracted_title) > 5:
                title = extracted_title

    cmd = [
        sys.executable, str(RADAR_SCRIPT), "add",
        "--title", title or url,
        "--area", area,
        "--source", source,
        "--tags", ",".join(tags),
        "--references", url,
        "--notes", f"From DingTalk ({masked_sender}): {raw_text[:100]}" if raw_text else f"From DingTalk",
        "--status", "inbox",
    ]

    # 添加摘要参数
    if summary:
        cmd.extend(["--summary", summary])

    if dry_run:
        print(f"  [dry-run] {' '.join(cmd[:6])}...")
        return True

    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        # 添加到已存在 URL 集合
        if existing_urls is not None:
            existing_urls.add(url)
            existing_urls.add(base_url)
        return True
    else:
        print(f"  ⚠️  入库失败: {result.stderr[:200]}", file=sys.stderr)
        return False


def _extract_title_from_url(url: str) -> str:
    """Try to extract a title from the URL path."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.rstrip("/")
    if path:
        # Use last path segment as title hint
        segment = path.split("/")[-1]
        segment = segment.replace("-", " ").replace("_", " ").replace(".html", "").replace(".md", "")
        if len(segment) > 5:
            return segment.title()
    return parsed.netloc


def _guess_area(url: str, text: str) -> str:
    """Guess the reading area from URL and text content."""
    combined = f"{url} {text}".lower()
    area_keywords = {
        "code-understanding": ["code", "github", "programming", "developer", "api"],
        "ai-os": ["ai", "agent", "llm", "gpt", "claude", "model"],
        "search-skills": ["search", "skill", "claude code", "cursor"],
        "skill-ecosystem": ["skill", "plugin", "extension", "marketplace"],
        "business-skills": ["business", "marketing", "sales", "product"],
        "stocks": ["stock", "invest", "trading", "finance", "market"],
        "design-tools": ["design", "ui", "ux", "figma", "css"],
        "content-distribution": ["content", "social", "media", "video", "tiktok"],
    }
    for area, keywords in area_keywords.items():
        if any(kw in combined for kw in keywords):
            return area
    return "inbox"


def _load_last_fetch_time() -> str:
    """Load the last fetch timestamp from state file."""
    state_file = Path.home() / ".praxis-skills" / "data" / "knowledge-radar" / "fetch_state.json"

    if not state_file.exists():
        return ""

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
            return state.get("last_fetch_time", "")
    except Exception:
        return ""


def _save_last_fetch_time(fetch_time: str) -> None:
    """Save the last fetch timestamp to state file."""
    state_file = Path.home() / ".praxis-skills" / "data" / "knowledge-radar" / "fetch_state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)

    state = {
        "last_fetch_time": fetch_time,
        "updated_at": datetime.now(timezone(timedelta(hours=8))).isoformat()
    }

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="DingTalk message fetcher for knowledge-radar")
    parser.add_argument("--since", default="24h", help="Fetch messages from last N hours (e.g. 2h, 24h, 7d)")
    parser.add_argument("--chat-id", help="Override chat ID from config")
    parser.add_argument("--dry-run", action="store_true", help="Extract URLs but don't ingest")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--incremental", action="store_true", help="Incremental mode: fetch from last fetch time")
    args = parser.parse_args()

    config = load_config()
    chat_id = args.chat_id or config["chat_id"]

    # 确定开始时间
    if args.incremental:
        # 增量模式：从上次拉取时间开始
        last_fetch_time = _load_last_fetch_time()
        if last_fetch_time:
            start_time = last_fetch_time
            print(f"📥 增量模式：从 {last_fetch_time} 开始拉取...")
        else:
            # 首次运行，使用 --since 参数
            since = args.since.lower()
            if since.endswith("d"):
                since_hours = int(since[:-1]) * 24
            elif since.endswith("h"):
                since_hours = int(since[:-1])
            else:
                since_hours = int(since)
            start_time = (datetime.now(timezone(timedelta(hours=8))) - timedelta(hours=since_hours)).strftime("%Y-%m-%d %H:%M:%S")
            print(f"📥 首次运行：从 {start_time} 开始拉取...")
    else:
        # 普通模式：使用 --since 参数
        since = args.since.lower()
        if since.endswith("d"):
            since_hours = int(since[:-1]) * 24
        elif since.endswith("h"):
            since_hours = int(since[:-1])
        else:
            since_hours = int(since)
        start_time = (datetime.now(timezone(timedelta(hours=8))) - timedelta(hours=since_hours)).strftime("%Y-%m-%d %H:%M:%S")
        print(f"📥 拉取最近 {since_hours} 小时的消息...")

    print(f"🔑 获取钉钉 Access Token...")
    token = get_access_token(config["app_key"], config["app_secret"])
    if not token:
        print("❌ 获取 Token 失败，请检查 AppKey/AppSecret", file=sys.stderr)
        return 1

    messages = fetch_chat_messages(token, chat_id, start_time)
    print(f"   收到 {len(messages)} 条消息")

    url_entries = extract_urls_from_messages(messages)
    print(f"🔗 提取到 {len(url_entries)} 个 URL")

    if args.json:
        print(json.dumps(url_entries, ensure_ascii=False, indent=2))
        return 0

    # 加载已存在的 URL 用于去重
    existing_urls = _load_existing_urls()
    print(f"📋 已存在 {len(existing_urls)} 个 URL（去重用）")

    ingested = 0
    skipped = 0
    for entry in url_entries:
        url = entry["url"]
        print(f"  → {url[:80]}")
        result = ingest_to_radar(entry, dry_run=args.dry_run, existing_urls=existing_urls)
        if result:
            ingested += 1
        else:
            skipped += 1

    action = "提取" if args.dry_run else "入库"
    print(f"\n✅ {action}完成: {ingested}/{len(url_entries)} 个 URL（跳过 {skipped} 个重复）")

    # 保存最后拉取时间（当前时间）
    if not args.dry_run:
        current_time = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
        _save_last_fetch_time(current_time)
        print(f"💾 已保存拉取时间: {current_time}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
