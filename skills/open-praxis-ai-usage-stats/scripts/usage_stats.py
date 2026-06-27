#!/usr/bin/env python3
"""AI Usage Stats - 统计所有 AI agent runtime 的使用情况

用法:
    python3 usage_stats.py [选项]

选项:
    today           统计今天
    week            统计最近 7 天（默认）
    month           统计最近 30 天
    --days N        统计最近 N 天
    --all-time      统计全部历史
    --runtime all|claude|codex|openhuman  按 runtime 过滤
    --kind all|skill|agent|tool           按类型过滤
    --project NAME  按项目过滤
    --name NAME     按名称过滤
    --limit N       排行榜条数（默认 10）
    --format json   JSON 输出
    --save          保存报告到文件
    --output-dir    自定义报告目录
    --web           启动 Web 仪表盘
    --port PORT     Web 仪表盘端口（默认 8080）
    --migrate       从旧日志迁移到 SQLite
    --cleanup       清理旧记录
    --cleanup-days  清理天数（默认 90）
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import Counter

# ── Capability Tiers ──────────────────────────────────────────
# All commands are CORE tier: pure Python stdlib, zero external deps.
# See praxis-skill-forge/references/capability-tiers.md for convention.
# ──────────────────────────────────────────────────────────────

CAPABILITY_TIERS = {
    "stats":           {"tier": "CORE", "deps": [], "desc": "Show usage statistics"},
    "report":          {"tier": "CORE", "deps": [], "desc": "Generate markdown/JSON report"},
    "web":             {"tier": "CORE", "deps": [], "desc": "Launch web dashboard"},
    "migrate":         {"tier": "CORE", "deps": [], "desc": "Migrate old logs to SQLite"},
    "cleanup":         {"tier": "CORE", "deps": [], "desc": "Clean up old records"},
    "hook-install":    {"tier": "CORE", "deps": [], "desc": "Install PostToolUse hook"},
    "hook-collect":    {"tier": "CORE", "deps": [], "desc": "Collect hook data (auto)"},
    "check-deps":      {"tier": "CORE", "deps": [], "desc": "Check dependencies"},
    "log":             {"tier": "CORE", "deps": [], "desc": "Manually log a usage event"},
}

# 添加当前目录到 path
sys.path.insert(0, str(Path(__file__).parent))

from db import UsageDB, get_db
from parsers import parse_all_runtimes
from outcome import infer_outcome, analyze_skill_flow, get_outcome_stats


# 默认配置
DEFAULT_REPORT_DIR = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats" / "reports"
DEFAULT_WEB_DIR = Path(__file__).parent.parent / "web"


def parse_args() -> Dict[str, Any]:
    """解析命令行参数"""
    args = sys.argv[1:]
    config = {
        "days": 7,
        "all_time": False,
        "save": False,
        "format": "markdown",
        "limit": 10,
        "output_dir": None,
        "runtime": "all",
        "kind": "all",
        "project": None,
        "name": None,
        "web": False,
        "port": 8080,
        "migrate": False,
        "cleanup": False,
        "cleanup_days": 90,
        "tiers": False,
    }

    i = 0
    while i < len(args):
        a = args[i]

        if a == "--days" and i + 1 < len(args):
            config["days"] = int(args[i + 1])
            i += 2
        elif a == "--all-time":
            config["all_time"] = True
            i += 1
        elif a == "--save":
            config["save"] = True
            i += 1
        elif a == "--json" or (a == "--format" and i + 1 < len(args) and args[i + 1] == "json"):
            config["format"] = "json"
            i += 2 if a == "--format" else 1
        elif a == "--format" and i + 1 < len(args):
            config["format"] = args[i + 1]
            i += 2
        elif a == "--limit" and i + 1 < len(args):
            config["limit"] = int(args[i + 1])
            i += 2
        elif a == "--output-dir" and i + 1 < len(args):
            config["output_dir"] = Path(args[i + 1])
            i += 2
        elif a == "--runtime" and i + 1 < len(args):
            runtime = args[i + 1].strip().lower()
            if runtime not in {"all", "claude", "codex", "openhuman"}:
                raise SystemExit("--runtime must be one of: all, claude, codex, openhuman")
            config["runtime"] = runtime
            i += 2
        elif a == "--kind" and i + 1 < len(args):
            kind = args[i + 1].strip().lower()
            if kind not in {"all", "skill", "agent", "tool"}:
                raise SystemExit("--kind must be one of: all, skill, agent, tool")
            config["kind"] = kind
            i += 2
        elif a == "--project" and i + 1 < len(args):
            config["project"] = args[i + 1]
            i += 2
        elif a == "--name" and i + 1 < len(args):
            config["name"] = args[i + 1]
            i += 2
        elif a == "--web":
            config["web"] = True
            i += 1
        elif a == "--port" and i + 1 < len(args):
            config["port"] = int(args[i + 1])
            i += 2
        elif a == "--migrate":
            config["migrate"] = True
            i += 1
        elif a == "--cleanup":
            config["cleanup"] = True
            i += 1
        elif a == "--cleanup-days" and i + 1 < len(args):
            config["cleanup_days"] = int(args[i + 1])
            i += 2
        elif a == "--tiers":
            config["tiers"] = True
            i += 1
        elif a == "today":
            config["days"] = 1
            i += 1
        elif a == "week":
            config["days"] = 7
            i += 1
        elif a == "month":
            config["days"] = 30
            i += 1
        else:
            i += 1

    return config


def migrate_to_sqlite(db: UsageDB, days: int = 365) -> int:
    """从旧日志迁移到 SQLite"""
    print("开始迁移旧日志到 SQLite...")

    since = datetime.now() - timedelta(days=days)
    records = parse_all_runtimes(since, runtime="all")

    if not records:
        print("没有找到旧日志记录")
        return 0

    # 批量插入
    count = db.insert_events_batch(records)
    print(f"成功迁移 {count} 条记录")

    return count


def format_markdown_output(stats: Dict[str, Any], events: List[Dict[str, Any]],
                           config: Dict[str, Any]) -> str:
    """格式化 Markdown 输出"""
    if not events:
        return "没有找到使用记录。"

    days = config["days"]
    limit = config["limit"]
    today = datetime.now().date()

    lines = []
    period = "全部时间" if config["all_time"] else f"过去 {days} 天"
    lines.append(f"# 📊 AI 使用统计（{period}）\n")

    # 总体统计
    total = stats["total"]
    lines.append(f"**总事件数**: {total['total_events']}  |  "
                 f"**总 Token**: {total['total_tokens_in'] + total['total_tokens_out']:,}  |  "
                 f"**总成本**: ${total['total_cost']:.2f}  |  "
                 f"**会话数**: {total['unique_sessions']}")
    lines.append("")

    # 健康评分
    health = stats.get("health_score", {})
    if health:
        score = health.get("score", 0)
        emoji = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
        lines.append(f"## {emoji} 健康评分: {score}/100")
        lines.append(f"- 成功率评分: {health.get('success_score', 0)}/40")
        lines.append(f"- 使用频率评分: {health.get('frequency_score', 0)}/30")
        lines.append(f"- 多样性评分: {health.get('diversity_score', 0)}/30")
        lines.append(f"- 成功率: {health.get('success_rate', 0)}%")
        lines.append(f"- 日均使用: {health.get('daily_average', 0)} 次")
        lines.append("")

    # 按类型统计
    lines.append("## 📈 按类型")
    lines.append(f"| {'类型':<8} | {'次数':>5} | {'Token':>10} | {'成本':>8} |")
    lines.append("|----------|------:|----------:|--------:|")
    for item in stats["by_kind"]:
        lines.append(f"| {item['kind']:<8} | {item['count']:>5} | "
                     f"{item['tokens']:>10,} | ${item['cost']:>7.2f} |")
    lines.append("")

    # 按 Runtime 统计
    lines.append("## 🖥️ 按 Runtime")
    lines.append(f"| {'Runtime':<10} | {'次数':>5} | {'Token':>10} | {'成本':>8} |")
    lines.append("|------------|------:|----------:|--------:|")
    for item in stats["by_runtime"]:
        lines.append(f"| {item['runtime']:<10} | {item['count']:>5} | "
                     f"{item['tokens']:>10,} | ${item['cost']:>7.2f} |")
    lines.append("")

    # 按模型统计
    if stats["by_model"]:
        lines.append("## 🤖 按模型")
        lines.append(f"| {'模型':<35} | {'次数':>5} | {'Token':>10} | {'成本':>8} |")
        lines.append("|" + "-" * 37 + "|------:|----------:|--------:|")
        for item in stats["by_model"][:limit]:
            lines.append(f"| {item['model']:<35} | {item['count']:>5} | "
                         f"{item['tokens']:>10,} | ${item['cost']:>7.2f} |")
        lines.append("")

    # Top Skills
    if stats["top_skills"]:
        lines.append("## 🏆 Top Skills")
        lines.append(f"| {'Skill':<35} | {'次数':>5} | {'Token':>10} | {'成本':>8} | {'平均延迟':>8} |")
        lines.append("|" + "-" * 37 + "|------:|----------:|--------:|--------:|")
        for item in stats["top_skills"][:limit]:
            avg_latency = f"{item['avg_latency']:.0f}ms" if item.get('avg_latency') else "N/A"
            lines.append(f"| {item['name']:<35} | {item['count']:>5} | "
                         f"{item['tokens']:>10,} | ${item['cost']:>7.2f} | {avg_latency:>8} |")
        lines.append("")

    # Top Agents
    if stats["top_agents"]:
        lines.append("## 🤖 Top Agents")
        lines.append(f"| {'Agent':<35} | {'次数':>5} | {'Token':>10} | {'成本':>8} |")
        lines.append("|" + "-" * 37 + "|------:|----------:|--------:|")
        for item in stats["top_agents"][:limit]:
            lines.append(f"| {item['name']:<35} | {item['count']:>5} | "
                         f"{item['tokens']:>10,} | ${item['cost']:>7.2f} |")
        lines.append("")

    # Top Tools
    if stats["top_tools"]:
        lines.append("## 🔧 Top Tools")
        lines.append(f"| {'Tool':<35} | {'次数':>5} | {'Token':>10} | {'成本':>8} |")
        lines.append("|" + "-" * 37 + "|------:|----------:|--------:|")
        for item in stats["top_tools"][:limit]:
            lines.append(f"| {item['name']:<35} | {item['count']:>5} | "
                         f"{item['tokens']:>10,} | ${item['cost']:>7.2f} |")
        lines.append("")

    # 成功率统计
    success_stats = stats["success_stats"]
    if success_stats:
        lines.append("## ✅ 成功率")
        total_known = (success_stats["success_count"] or 0) + (success_stats["failed_count"] or 0)
        success_rate = (success_stats["success_count"] / total_known * 100) if total_known > 0 else 0
        lines.append(f"- ✅ 成功: {success_stats['success_count'] or 0}")
        lines.append(f"- ❌ 失败: {success_stats['failed_count'] or 0}")
        lines.append(f"- ❓ 未知: {success_stats['unknown_count'] or 0}")
        lines.append(f"- 📊 成功率: {success_rate:.1f}%")
        lines.append("")

    # 按项目统计
    if stats["by_project"]:
        lines.append("## 📁 按项目")
        lines.append(f"| {'项目':<30} | {'次数':>5} | {'Token':>10} | {'成本':>8} |")
        lines.append("|" + "-" * 32 + "|------:|----------:|--------:|")
        for item in stats["by_project"][:limit]:
            lines.append(f"| {item['project']:<30} | {item['count']:>5} | "
                         f"{item['tokens']:>10,} | ${item['cost']:>7.2f} |")
        lines.append("")

    # 每日趋势
    if stats["daily_trend"]:
        lines.append("## 📅 每日趋势")
        lines.append(f"| {'日期':<12} | {'次数':>5} | {'Token':>10} | {'成本':>8} |")
        lines.append("|--------------|------:|----------:|--------:|")
        for item in stats["daily_trend"][:14]:
            lines.append(f"| {item['date']:<12} | {item['count']:>5} | "
                         f"{item['tokens']:>10,} | ${item['cost']:>7.2f} |")
        lines.append("")

    # 周对比
    if len(stats["daily_trend"]) >= 7:
        this_week = sum(item["count"] for item in stats["daily_trend"][:7])
        last_week = sum(item["count"] for item in stats["daily_trend"][7:14]) if len(stats["daily_trend"]) >= 14 else 0
        if last_week > 0:
            delta = this_week - last_week
            sign = "+" if delta >= 0 else ""
            pct = delta / last_week * 100
            lines.append(f"## 📊 周对比")
            lines.append(f"本周: {this_week}  |  上周: {last_week}  |  变化: {sign}{delta} ({sign}{pct:.0f}%)")
            lines.append("")

    # 最近事件
    lines.append("## 🕐 最近事件")
    lines.append(f"| {'时间':<16} | {'Runtime':<10} | {'类型':<6} | {'名称':<25} | {'Token':>8} | {'成本':>8} | {'结果':<10} |")
    lines.append("|" + "-" * 18 + "|" + "-" * 12 + "|--------|" + "-" * 27 + "|----------:|--------:|------------|")
    for e in events[-15:]:
        ts_short = e["ts"][:16] if len(e["ts"]) > 16 else e["ts"]
        tokens = e.get("tokens_in", 0) + e.get("tokens_out", 0)
        cost = e.get("cost_usd", 0.0)
        outcome = e.get("outcome", "unknown")
        outcome_emoji = "✅" if outcome == "likely_solved" else "❌" if outcome == "likely_failed" else "❓"
        lines.append(f"| {ts_short:<16} | {e['runtime']:<10} | {e['kind']:<6} | "
                     f"{e['name']:<25} | {tokens:>8,} | ${cost:>7.2f} | {outcome_emoji} {outcome:<8} |")
    lines.append("")

    return "\n".join(lines)


def format_json_output(stats: Dict[str, Any], events: List[Dict[str, Any]],
                       config: Dict[str, Any]) -> str:
    """格式化 JSON 输出"""
    # 转换 config 中的 Path 对象为字符串
    serializable_config = {}
    for key, value in config.items():
        if isinstance(value, Path):
            serializable_config[key] = str(value)
        else:
            serializable_config[key] = value

    output = {
        "generated_at": datetime.now().isoformat(),
        "config": serializable_config,
        "stats": stats,
        "events": events[:1000],  # 限制输出数量
    }
    return json.dumps(output, ensure_ascii=False, indent=2)


def start_web_server(port: int = 8080):
    """启动 Web 仪表盘"""
    import http.server
    import socketserver
    import webbrowser

    web_dir = DEFAULT_WEB_DIR
    if not web_dir.exists():
        print(f"错误: Web 目录不存在 {web_dir}")
        return

    # 导出数据到 JSON 供 Web 使用
    db = get_db()
    stats = db.query_stats(days=30)
    events = db.query_events(days=30)

    data_file = web_dir / "data.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump({"stats": stats, "events": events}, f, ensure_ascii=False)

    db.close()

    # 启动 HTTP 服务器
    os.chdir(web_dir)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Web 仪表盘已启动: http://localhost:{port}")
        print("按 Ctrl+C 停止服务器")

        # 自动打开浏览器
        webbrowser.open(f"http://localhost:{port}")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")


def main():
    """主入口"""
    config = parse_args()

    # 初始化数据库
    db = get_db()

    # 迁移旧日志
    if config["migrate"]:
        count = migrate_to_sqlite(db)
        print(f"迁移完成: {count} 条记录")
        db.close()
        return

    # 清理旧记录
    if config["cleanup"]:
        count = db.cleanup_old_records(config["cleanup_days"])
        print(f"清理完成: 删除了 {count} 条旧记录")
        db.close()
        return

    # 显示能力层级
    if config["tiers"]:
        tiers_output = {"ok": True, "tiers": {}}
        for name, info in CAPABILITY_TIERS.items():
            tier = info["tier"]
            tiers_output["tiers"].setdefault(tier, []).append({
                "command": name, "deps": info["deps"], "desc": info["desc"]
            })
        tiers_output["summary"] = {
            tier: f"{len(cmds)} commands — {'keep in open-source' if tier == 'CORE' else 'optional'}"
            for tier, cmds in tiers_output["tiers"].items()
        }
        print(json.dumps(tiers_output, ensure_ascii=False, indent=2))
        return

    # 启动 Web 仪表盘
    if config["web"]:
        db.close()
        start_web_server(config["port"])
        return

    # 计算时间范围
    if config["all_time"]:
        days = 0  # 0 表示全部时间
    else:
        days = config["days"]

    # 检查数据库是否为空，自动迁移
    count = db.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    if count == 0:
        print("📊 数据库为空，正在自动迁移历史数据...")
        try:
            from parsers import parse_all_runtimes
            since = datetime.now() - timedelta(days=30)
            records = parse_all_runtimes(since, runtime="all")

            if records:
                db.insert_events_batch(records)
                print(f"✅ 已自动迁移 {len(records)} 条历史记录\n")
            else:
                print("⚠️  没有找到历史数据\n")
        except Exception as e:
            print(f"⚠️  自动迁移失败: {e}")
            print("   可以手动运行: python3 scripts/usage_stats.py --migrate\n")

    # 查询统计信息
    stats = db.query_stats(days=days, runtime=config["runtime"])

    # 查询事件列表
    events = db.query_events(
        days=days,
        runtime=config["runtime"],
        kind=config["kind"],
        project=config["project"],
        name=config["name"],
    )

    # 添加健康评分
    stats["health_score"] = db.get_health_score(days=days or 30)

    # 输出
    if config["format"] == "json":
        output = format_json_output(stats, events, config)
    else:
        output = format_markdown_output(stats, events, config)

    print(output)

    # 保存报告
    if config["save"]:
        report_dir = config["output_dir"] or DEFAULT_REPORT_DIR
        report_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')

        # 保存 Markdown
        md_file = report_dir / f"usage-{timestamp}.md"
        md_file.write_text(format_markdown_output(stats, events, config))

        # 保存 JSON
        json_file = report_dir / f"usage-{timestamp}.json"
        json_file.write_text(format_json_output(stats, events, config))

        # 导出完整数据
        export_file = report_dir / f"usage-{timestamp}-full.json"
        db.export_json(export_file, days=days, runtime=config["runtime"])

        print(f"\n报告已保存:")
        print(f"  Markdown: {md_file}")
        print(f"  JSON: {json_file}")
        print(f"  完整数据: {export_file}")

    db.close()


if __name__ == "__main__":
    main()
