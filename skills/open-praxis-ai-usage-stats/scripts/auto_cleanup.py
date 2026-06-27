#!/usr/bin/env python3
"""自动清理脚本 - 清理旧数据和报告

用法:
    python3 auto_cleanup.py                    # 清理 90 天前的数据
    python3 auto_cleanup.py --days 30          # 清理 30 天前的数据
    python3 auto_cleanup.py --dry-run          # 预览要清理的内容
    python3 auto_cleanup.py --clean-reports    # 同时清理旧报告
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from db import UsageDB


def parse_args() -> Dict[str, Any]:
    args = sys.argv[1:]
    config = {
        "days": 90,
        "dry_run": False,
        "clean_reports": False,
        "report_days": 30,  # 报告保留 30 天
    }

    i = 0
    while i < len(args):
        a = args[i]
        if a == "--days" and i + 1 < len(args):
            config["days"] = int(args[i + 1])
            i += 2
        elif a == "--report-days" and i + 1 < len(args):
            config["report_days"] = int(args[i + 1])
            i += 2
        elif a == "--dry-run":
            config["dry_run"] = True
            i += 1
        elif a == "--clean-reports":
            config["clean_reports"] = True
            i += 1
        else:
            i += 1

    return config


def cleanup_database(days: int, dry_run: bool) -> int:
    """清理数据库旧记录"""
    db = UsageDB()

    # 查询要删除的记录数
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    count = db.conn.execute(
        "SELECT COUNT(*) FROM events WHERE ts < ?", (cutoff,)
    ).fetchone()[0]

    if dry_run:
        print(f"[预览] 将删除 {count} 条 {days} 天前的数据库记录")
        db.close()
        return count

    # 执行删除
    deleted = db.cleanup_old_records(days)
    db.close()

    print(f"✅ 已删除 {deleted} 条 {days} 天前的数据库记录")
    return deleted


def cleanup_reports(report_days: int, dry_run: bool) -> int:
    """清理旧报告文件"""
    reports_dir = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats" / "reports"

    if not reports_dir.exists():
        print("报告目录不存在")
        return 0

    cutoff = datetime.now() - timedelta(days=report_days)
    deleted = 0

    for report_file in reports_dir.glob("report_*.html"):
        # 从文件名提取时间戳
        try:
            timestamp_str = report_file.stem.split("_")[1] + report_file.stem.split("_")[2]
            file_time = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")

            if file_time < cutoff:
                if dry_run:
                    print(f"[预览] 将删除报告: {report_file.name}")
                else:
                    report_file.unlink()
                    print(f"✅ 已删除报告: {report_file.name}")
                deleted += 1
        except (ValueError, IndexError):
            continue

    if not dry_run and deleted > 0:
        print(f"✅ 共删除 {deleted} 个 {report_days} 天前的报告")

    return deleted


def get_directory_size(path: Path) -> int:
    """获取目录大小"""
    total = 0
    try:
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
    except (OSError, PermissionError):
        pass
    return total


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    config = parse_args()

    print("=" * 50)
    print("📊 AI Usage Stats - 自动清理")
    print("=" * 50)
    print()

    # 显示当前状态
    data_dir = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats"
    db_path = data_dir / "usage.db"
    reports_dir = data_dir / "reports"

    if db_path.exists():
        db_size = db_path.stat().st_size
        print(f"📦 数据库大小: {format_size(db_size)}")

    if reports_dir.exists():
        reports_size = get_directory_size(reports_dir)
        report_count = len(list(reports_dir.glob("report_*.html")))
        print(f"📁 报告数量: {report_count} 个")
        print(f"📁 报告大小: {format_size(reports_size)}")

    print()

    if config["dry_run"]:
        print("🔍 预览模式（不会实际删除）")
        print()

    # 清理数据库
    print(f"📊 清理 {config['days']} 天前的数据库记录...")
    cleanup_database(config["days"], config["dry_run"])

    # 清理报告
    if config["clean_reports"]:
        print()
        print(f"📁 清理 {config['report_days']} 天前的报告文件...")
        cleanup_reports(config["report_days"], config["dry_run"])

    print()
    print("=" * 50)

    if config["dry_run"]:
        print("💡 这是预览模式，添加 --no-dry-run 执行实际清理")
    else:
        print("✅ 清理完成")


if __name__ == "__main__":
    main()
