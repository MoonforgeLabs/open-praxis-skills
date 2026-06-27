#!/usr/bin/env python3
"""生成知识雷达报告 - Markdown 或 HTML 格式（带摘要表格）

用法:
    python3 generate_report_v2.py                    # 生成 Markdown 报告
    python3 generate_report_v2.py --format html      # 生成 HTML 报告
    python3 generate_report_v2.py --output report.md # 指定输出文件
    python3 generate_report_v2.py --open             # 生成后打开
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# 默认路径
TASKS_FILE = Path.home() / ".praxis-skills" / "data" / "knowledge-radar" / "tasks.jsonl"
REPORT_DIR = Path.home() / ".praxis-skills" / "data" / "knowledge-radar" / "reports"


def load_tasks() -> list[dict[str, Any]]:
    """加载所有任务"""
    if not TASKS_FILE.exists():
        return []

    tasks = []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    tasks.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return tasks


def get_status_emoji(status: str) -> str:
    """获取状态对应的 emoji"""
    emojis = {
        "inbox": "📥",
        "next": "➡️",
        "active": "🔄",
        "learning": "📖",
        "learned": "✅",
        "applied": "🎯",
        "waiting": "⏳",
        "done": "✔️",
        "archived": "📦",
    }
    return emojis.get(status, "❓")


def get_priority_emoji(priority: str) -> str:
    """获取优先级对应的 emoji"""
    emojis = {
        "P0": "🔴",
        "P1": "🟠",
        "P2": "🟡",
        "P3": "🟢",
    }
    return emojis.get(priority, "⚪")


def get_area_emoji(area: str) -> str:
    """获取领域对应的 emoji"""
    emojis = {
        "code-understanding": "💻",
        "patent-skills": "📝",
        "rag-docs": "📚",
        "search-skills": "🔍",
        "skill-creation": "🛠️",
        "daily-news": "📰",
        "ai-os": "🤖",
        "knowledge-base": "🧠",
        "skill-ecosystem": "🌐",
        "business-skills": "💼",
        "stocks": "📈",
        "design-tools": "🎨",
        "digital-human": "👤",
        "content-distribution": "📢",
    }
    return emojis.get(area, "📁")


def generate_markdown_report(tasks: list[dict[str, Any]], detailed: bool = True) -> str:
    """生成 Markdown 格式报告"""
    now = datetime.now(timezone(timedelta(hours=8)))
    lines = []

    # 标题
    lines.append(f"# 📡 知识雷达报告")
    lines.append(f"")
    lines.append(f"**生成时间**: {now.strftime('%Y-%m-%d %H:%M:%S')} CST")
    lines.append(f"")

    # 统计概览
    status_counts = {}
    area_counts = {}
    priority_counts = {}
    source_counts = {}

    for task in tasks:
        status = task.get("status", "unknown")
        area = task.get("area", "uncategorized")
        priority = task.get("priority", "P2")
        source = task.get("source", "unknown")

        status_counts[status] = status_counts.get(status, 0) + 1
        area_counts[area] = area_counts.get(area, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
        source_counts[source] = source_counts.get(source, 0) + 1

    lines.append(f"## 📊 统计概览")
    lines.append(f"")
    lines.append(f"**总任务数**: {len(tasks)}")
    lines.append(f"")

    # 状态分布
    lines.append(f"### 状态分布")
    lines.append(f"")
    lines.append(f"| 状态 | 数量 | 占比 |")
    lines.append(f"|------|------|------|")
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        emoji = get_status_emoji(status)
        pct = count / len(tasks) * 100 if tasks else 0
        lines.append(f"| {emoji} {status} | {count} | {pct:.1f}% |")
    lines.append(f"")

    # 领域分布
    lines.append(f"### 领域分布")
    lines.append(f"")
    lines.append(f"| 领域 | 数量 | 占比 |")
    lines.append(f"|------|------|------|")
    for area, count in sorted(area_counts.items(), key=lambda x: -x[1]):
        emoji = get_area_emoji(area)
        pct = count / len(tasks) * 100 if tasks else 0
        lines.append(f"| {emoji} {area} | {count} | {pct:.1f}% |")
    lines.append(f"")

    # 优先级分布
    lines.append(f"### 优先级分布")
    lines.append(f"")
    lines.append(f"| 优先级 | 数量 | 占比 |")
    lines.append(f"|--------|------|------|")
    for priority, count in sorted(priority_counts.items()):
        emoji = get_priority_emoji(priority)
        pct = count / len(tasks) * 100 if tasks else 0
        lines.append(f"| {emoji} {priority} | {count} | {pct:.1f}% |")
    lines.append(f"")

    # 来源分布
    lines.append(f"### 来源分布")
    lines.append(f"")
    lines.append(f"| 来源 | 数量 | 占比 |")
    lines.append(f"|------|------|------|")
    for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        pct = count / len(tasks) * 100 if tasks else 0
        lines.append(f"| {source} | {count} | {pct:.1f}% |")
    lines.append(f"")

    # 最近入库的 URL（带摘要表格）
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 🔗 最近入库的 URL")
    lines.append(f"")
    lines.append(f"| 领域 | 标题 | 摘要 | 来源 | 时间 |")
    lines.append(f"|------|------|------|------|------|")

    recent_tasks = sorted(tasks, key=lambda x: x.get("created_at", ""), reverse=True)[:15]
    for task in recent_tasks:
        title = task.get("title", "无标题")
        url = task.get("references", [""])[0] if task.get("references") else ""
        source = task.get("source", "-")
        created = task.get("created_at", "")[:10]
        area = task.get("area", "")
        area_emoji = get_area_emoji(area)
        summary = task.get("content_summary", "")

        # 截断标题
        if len(title) > 40:
            title = title[:37] + "..."

        # 截断摘要
        if len(summary) > 80:
            summary = summary[:77] + "..."
        elif not summary:
            summary = "-"

        # 创建链接
        if url:
            title_link = f"[{title}]({url})"
        else:
            title_link = title

        lines.append(f"| {area_emoji} {area} | {title_link} | {summary} | {source} | {created} |")

    lines.append(f"")

    # 按状态分组的任务列表
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 📋 任务列表")
    lines.append(f"")

    # 按状态分组
    status_order = ["inbox", "next", "active", "learning", "learned", "applied", "waiting", "done", "archived"]
    tasks_by_status = {}
    for task in tasks:
        status = task.get("status", "unknown")
        if status not in tasks_by_status:
            tasks_by_status[status] = []
        tasks_by_status[status].append(task)

    for status in status_order:
        if status not in tasks_by_status:
            continue

        status_tasks = tasks_by_status[status]
        emoji = get_status_emoji(status)

        lines.append(f"### {emoji} {status.upper()} ({len(status_tasks)})")
        lines.append(f"")

        if detailed:
            # 详细模式：显示完整信息
            lines.append(f"| # | 优先级 | 领域 | 标题 | 摘要 | 来源 | 时间 |")
            lines.append(f"|---|--------|------|------|------|------|------|")

            for i, task in enumerate(status_tasks[:20], 1):  # 最多显示 20 条
                priority = task.get("priority", "P2")
                area = task.get("area", "-")
                title = task.get("title", "无标题")[:40]
                source = task.get("source", "-")
                created = task.get("created_at", "")[:10]
                summary = task.get("content_summary", "")[:50]

                priority_emoji = get_priority_emoji(priority)
                area_emoji = get_area_emoji(area)

                if not summary:
                    summary = "-"

                lines.append(f"| {i} | {priority_emoji} {priority} | {area_emoji} {area} | {title} | {summary} | {source} | {created} |")

            if len(status_tasks) > 20:
                lines.append(f"| ... | ... | ... | 还有 {len(status_tasks) - 20} 条 | ... | ... | ... |")
        else:
            # 简洁模式：只显示标题
            for task in status_tasks[:10]:
                title = task.get("title", "无标题")
                area = task.get("area", "")
                area_emoji = get_area_emoji(area)
                lines.append(f"- {area_emoji} {title}")

            if len(status_tasks) > 10:
                lines.append(f"- ... 还有 {len(status_tasks) - 10} 条")

        lines.append(f"")

    # 待学习队列
    learning_tasks = [t for t in tasks if t.get("status") in ["inbox", "next"]]
    if learning_tasks:
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 📖 待学习队列 ({len(learning_tasks)})")
        lines.append(f"")

        # 按优先级排序
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        learning_tasks.sort(key=lambda x: priority_order.get(x.get("priority", "P2"), 2))

        for task in learning_tasks[:15]:
            title = task.get("title", "无标题")
            priority = task.get("priority", "P2")
            area = task.get("area", "")
            priority_emoji = get_priority_emoji(priority)
            area_emoji = get_area_emoji(area)

            lines.append(f"- {priority_emoji} {area_emoji} {title}")

        if len(learning_tasks) > 15:
            lines.append(f"- ... 还有 {len(learning_tasks) - 15} 条")

        lines.append(f"")

    # 页脚
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*报告由 knowledge-radar 自动生成*")

    return "\n".join(lines)


def generate_html_report(tasks: list[dict[str, Any]]) -> str:
    """生成 HTML 格式报告"""
    now = datetime.now(timezone(timedelta(hours=8)))

    # 统计数据
    status_counts = {}
    area_counts = {}
    priority_counts = {}

    for task in tasks:
        status = task.get("status", "unknown")
        area = task.get("area", "uncategorized")
        priority = task.get("priority", "P2")

        status_counts[status] = status_counts.get(status, 0) + 1
        area_counts[area] = area_counts.get(area, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    # 生成 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📡 知识雷达报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .header p {{
            color: #666;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-card h3 {{
            font-size: 1.2em;
            color: #666;
            margin-bottom: 15px;
        }}
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .stat-detail {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}
        .stat-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f5f5f5;
        }}
        .stat-item:last-child {{
            border-bottom: none;
        }}
        .stat-label {{
            color: #666;
        }}
        .stat-value {{
            font-weight: bold;
            color: #333;
        }}
        .section {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .task-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            min-width: 80px;
            text-align: center;
            display: inline-block;
        }}
        .badge-inbox {{ background: #e3f2fd; color: #1976d2; }}
        .badge-next {{ background: #fff3e0; color: #f57c00; }}
        .badge-active {{ background: #e8f5e9; color: #388e3c; }}
        .badge-learning {{ background: #f3e5f5; color: #7b1fa2; }}
        .badge-learned {{ background: #e8f5e9; color: #2e7d32; }}
        .badge-applied {{ background: #e0f7fa; color: #00838f; }}
        .badge-waiting {{ background: #fff8e1; color: #f9a825; }}
        .badge-done {{ background: #e8eaf6; color: #3f51b5; }}
        .badge-archived {{ background: #fafafa; color: #616161; }}
        .url-link {{
            color: #1976d2;
            text-decoration: none;
            font-weight: 500;
        }}
        .url-link:hover {{
            text-decoration: underline;
        }}
        .summary-text {{
            color: #666;
            font-size: 0.9em;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: rgba(255,255,255,0.8);
            font-size: 0.9em;
        }}
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            table {{
                font-size: 0.9em;
            }}
            th, td {{
                padding: 8px 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📡 知识雷达报告</h1>
            <p>生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')} CST</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>📊 总任务数</h3>
                <div class="stat-number">{len(tasks)}</div>
            </div>
            <div class="stat-card">
                <h3>📥 待处理</h3>
                <div class="stat-number">{status_counts.get('inbox', 0) + status_counts.get('next', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>📖 学习中</h3>
                <div class="stat-number">{status_counts.get('learning', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>✅ 已完成</h3>
                <div class="stat-number">{status_counts.get('learned', 0) + status_counts.get('applied', 0) + status_counts.get('done', 0)}</div>
            </div>
        </div>

        <div class="section">
            <h2>🔗 最近入库的 URL</h2>
            <table>
                <thead>
                    <tr>
                        <th>领域</th>
                        <th>标题</th>
                        <th>摘要</th>
                        <th>来源</th>
                        <th>时间</th>
                    </tr>
                </thead>
                <tbody>
"""

    # 最近入库的 URL
    area_emojis = {
        "code-understanding": "💻", "patent-skills": "📝", "rag-docs": "📚",
        "search-skills": "🔍", "skill-creation": "🛠️", "daily-news": "📰",
        "ai-os": "🤖", "knowledge-base": "🧠", "skill-ecosystem": "🌐",
        "business-skills": "💼", "stocks": "📈", "design-tools": "🎨",
        "digital-human": "👤", "content-distribution": "📢"
    }

    recent_tasks = sorted(tasks, key=lambda x: x.get("created_at", ""), reverse=True)[:15]
    for task in recent_tasks:
        title = task.get("title", "无标题")
        url = task.get("references", [""])[0] if task.get("references") else ""
        source = task.get("source", "-")
        created = task.get("created_at", "")[:10]
        area = task.get("area", "")
        area_emoji = area_emojis.get(area, "📁")
        summary = task.get("content_summary", "")

        # 截断标题
        if len(title) > 50:
            title = title[:47] + "..."

        # 截断摘要
        if len(summary) > 100:
            summary = summary[:97] + "..."
        elif not summary:
            summary = "-"

        # 创建链接
        if url:
            title_html = f'<a href="{url}" target="_blank" class="url-link">{title}</a>'
        else:
            title_html = title

        html += f"""
                    <tr>
                        <td>{area_emoji} {area}</td>
                        <td>{title_html}</td>
                        <td class="summary-text" title="{summary}">{summary}</td>
                        <td>{source}</td>
                        <td>{created}</td>
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>📈 状态分布</h2>
            <div class="stat-detail">
"""

    # 状态分布
    status_emojis = {
        "inbox": "📥", "next": "➡️", "active": "🔄", "learning": "📖",
        "learned": "✅", "applied": "🎯", "waiting": "⏳", "done": "✔️", "archived": "📦"
    }
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        emoji = status_emojis.get(status, "❓")
        pct = count / len(tasks) * 100 if tasks else 0
        html += f"""
                <div class="stat-item">
                    <span class="stat-label">{emoji} {status}</span>
                    <span class="stat-value">{count} ({pct:.1f}%)</span>
                </div>
"""

    html += """
            </div>
        </div>

        <div class="section">
            <h2>📁 领域分布</h2>
            <div class="stat-detail">
"""

    # 领域分布
    for area, count in sorted(area_counts.items(), key=lambda x: -x[1]):
        emoji = area_emojis.get(area, "📁")
        pct = count / len(tasks) * 100 if tasks else 0
        html += f"""
                <div class="stat-item">
                    <span class="stat-label">{emoji} {area}</span>
                    <span class="stat-value">{count} ({pct:.1f}%)</span>
                </div>
"""

    html += """
            </div>
        </div>

        <div class="section">
            <h2>📋 任务列表</h2>
            <table>
                <thead>
                    <tr>
                        <th>状态</th>
                        <th>优先级</th>
                        <th>领域</th>
                        <th>标题</th>
                        <th>摘要</th>
                        <th>来源</th>
                        <th>时间</th>
                    </tr>
                </thead>
                <tbody>
"""

    # 任务列表
    status_order = ["inbox", "next", "active", "learning", "learned", "applied", "waiting", "done", "archived"]
    tasks_by_status = {}
    for task in tasks:
        status = task.get("status", "unknown")
        if status not in tasks_by_status:
            tasks_by_status[status] = []
        tasks_by_status[status].append(task)

    for status in status_order:
        if status not in tasks_by_status:
            continue

        status_tasks = tasks_by_status[status]
        emoji = status_emojis.get(status, "❓")

        # 显示前 10 条
        for task in status_tasks[:10]:
            title = task.get("title", "无标题")[:50]
            priority = task.get("priority", "P2")
            area = task.get("area", "")
            source = task.get("source", "-")
            created = task.get("created_at", "")[:10]
            summary = task.get("content_summary", "")[:60]

            priority_colors = {"P0": "🔴", "P1": "🟠", "P2": "🟡", "P3": "🟢"}
            priority_emoji = priority_colors.get(priority, "⚪")
            area_emoji = area_emojis.get(area, "📁")

            if not summary:
                summary = "-"

            html += f"""
                    <tr>
                        <td><span class="task-badge badge-{status}">{emoji} {status}</span></td>
                        <td>{priority_emoji} {priority}</td>
                        <td>{area_emoji} {area}</td>
                        <td>{title}</td>
                        <td class="summary-text" title="{summary}">{summary}</td>
                        <td>{source}</td>
                        <td>{created}</td>
                    </tr>
"""

        if len(status_tasks) > 10:
            html += f"""
                    <tr>
                        <td colspan="7" style="text-align: center; color: #999;">
                            ... 还有 {len(status_tasks) - 10} 条 {status} 任务
                        </td>
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>📡 报告由 knowledge-radar 自动生成</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def main():
    parser = argparse.ArgumentParser(description="生成知识雷达报告")
    parser.add_argument("--format", choices=["md", "html"], default="md", help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--open", action="store_true", help="生成后打开")
    parser.add_argument("--simple", action="store_true", help="简洁模式")
    args = parser.parse_args()

    # 加载任务
    tasks = load_tasks()
    print(f"📊 加载了 {len(tasks)} 个任务")

    # 生成报告
    if args.format == "html":
        report = generate_html_report(tasks)
        ext = "html"
    else:
        report = generate_markdown_report(tasks, detailed=not args.simple)
        ext = "md"

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = REPORT_DIR / f"report-{timestamp}.{ext}"

    # 保存报告
    output_path.write_text(report, encoding="utf-8")
    print(f"✅ 报告已生成: {output_path}")

    # 打开报告
    if args.open:
        import subprocess
        if sys.platform == "darwin":
            subprocess.run(["open", str(output_path)])
        elif sys.platform == "win32":
            subprocess.run(["start", str(output_path)], shell=True)
        else:
            subprocess.run(["xdg-open", str(output_path)])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
