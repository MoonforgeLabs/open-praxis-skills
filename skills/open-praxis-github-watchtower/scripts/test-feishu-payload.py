#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from zoneinfo import ZoneInfo

now = datetime.now(ZoneInfo("Asia/Shanghai"))
payload = {
    "source": "github-project-watchtower",
    "project": "multiple",
    "repo": "",
    "fork_repo": "",
    "category": "github_daily_watch",
    "event_type": "github_daily_report",
    "severity": "info",
    "title": f"GitHub 项目监控测试 {now:%Y-%m-%d %H:%M:%S}",
    "summary": "这是一条 GitHub Watchtower 字段显示测试。飞书建议显示 title 和 summary 字段。",
    "text": "GitHub Watchtower 字段显示测试\n\n这是一条 GitHub Watchtower 字段显示测试。",
    "content": "这是一条 GitHub Watchtower 字段显示测试。飞书建议显示 title 和 summary 字段。",
    "url": "",
    "date": f"{now:%Y-%m-%d}",
    "time": f"{now:%H:%M:%S}",
    "timezone": "Asia/Shanghai",
    "run_id": f"{now:%H%M%S}",
    "status": "test",
}
print(json.dumps(payload, ensure_ascii=False, indent=2))
