#!/usr/bin/env python3
"""
数据迁移脚本 - 将各 skill 数据迁移到统一目录

用法:
    python3 migrate_data.py                    # 迁移所有数据
    python3 migrate_data.py --dry-run          # 预览迁移
    python3 migrate_data.py --skill <name>     # 迁移指定 skill
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


# 统一数据目录
ALEX_SKILLS_DATA = Path.home() / ".alex-skills" / "data"

# 数据源映射
DATA_SOURCES = {
    "task-radar": {
        "old_path": Path.home() / ".alex-skills" / "alex-task-radar",
        "files": ["tasks.jsonl"],
        "description": "任务雷达数据",
    },
    "safe-search": {
        "old_path": Path.home() / ".alex-safe-search",
        "files": ["audit.jsonl"],
        "description": "安全搜索审计日志",
    },
    "ai-usage-stats": {
        "old_path": Path.home() / ".alex-ai-usage-stats",
        "files": ["usage.db", "events.jsonl"],
        "description": "AI 使用统计数据",
    },
}


def check_source_exists(skill_name: str) -> Tuple[bool, List[Path]]:
    """检查源数据是否存在"""
    config = DATA_SOURCES.get(skill_name)
    if not config:
        return False, []

    old_path = config["old_path"]
    existing_files = []

    for file_name in config["files"]:
        file_path = old_path / file_name
        if file_path.exists():
            existing_files.append(file_path)

    return len(existing_files) > 0, existing_files


def migrate_skill(skill_name: str, dry_run: bool = False) -> bool:
    """迁移单个 skill 的数据"""
    config = DATA_SOURCES.get(skill_name)
    if not config:
        print(f"❌ 未知 skill: {skill_name}")
        return False

    old_path = config["old_path"]
    new_path = ALEX_SKILLS_DATA / skill_name

    print(f"\n=== {skill_name} ===")
    print(f"  源目录: {old_path}")
    print(f"  目标目录: {new_path}")

    # 检查源文件
    exists, existing_files = check_source_exists(skill_name)
    if not exists:
        print(f"  ⚠️  源数据不存在，跳过")
        return True

    # 创建目标目录
    if not dry_run:
        new_path.mkdir(parents=True, exist_ok=True)

    # 迁移文件
    migrated_count = 0
    for file_path in existing_files:
        file_name = file_path.name
        new_file_path = new_path / file_name

        if dry_run:
            print(f"  [预览] {file_name} → {new_file_path}")
        else:
            try:
                # 复制文件
                shutil.copy2(file_path, new_file_path)
                print(f"  ✅ {file_name} → {new_file_path}")
                migrated_count += 1
            except Exception as e:
                print(f"  ❌ {file_name} 迁移失败: {e}")
                return False

    if not dry_run:
        print(f"  ✅ 迁移完成: {migrated_count} 个文件")

    return True


def update_skill_config(skill_name: str, dry_run: bool = False) -> bool:
    """更新 skill 配置，指向新路径"""
    print(f"\n=== 更新 {skill_name} 配置 ===")

    # 这里需要根据具体 skill 的配置文件来更新
    # 暂时只打印提示
    if dry_run:
        print(f"  [预览] 需要更新 {skill_name} 的配置文件")
    else:
        print(f"  ⚠️  需要手动更新 {skill_name} 的配置文件")

    return True


def cleanup_old_dirs(skill_name: str, dry_run: bool = False) -> bool:
    """清理旧目录"""
    config = DATA_SOURCES.get(skill_name)
    if not config:
        return False

    old_path = config["old_path"]

    print(f"\n=== 清理 {skill_name} 旧目录 ===")

    if dry_run:
        print(f"  [预览] 删除: {old_path}")
    else:
        # 检查是否还有其他文件
        remaining_files = list(old_path.glob("*"))
        if remaining_files:
            print(f"  ⚠️  旧目录还有文件，不删除: {old_path}")
            for f in remaining_files:
                print(f"    - {f.name}")
        else:
            try:
                old_path.rmdir()
                print(f"  ✅ 已删除: {old_path}")
            except Exception as e:
                print(f"  ❌ 删除失败: {e}")
                return False

    return True


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    skill_filter = None

    if "--skill" in args:
        idx = args.index("--skill")
        if idx + 1 < len(args):
            skill_filter = args[idx + 1]

    print("=" * 60)
    print("📦 Alex Skills 数据迁移")
    print("=" * 60)
    print(f"统一数据目录: {ALEX_SKILLS_DATA}")
    print(f"模式: {'预览' if dry_run else '执行'}")

    # 确保统一目录存在
    if not dry_run:
        ALEX_SKILLS_DATA.mkdir(parents=True, exist_ok=True)

    # 迁移各 skill
    skills_to_migrate = [skill_filter] if skill_filter else list(DATA_SOURCES.keys())
    success_count = 0

    for skill_name in skills_to_migrate:
        if skill_name not in DATA_SOURCES:
            print(f"\n❌ 未知 skill: {skill_name}")
            continue

        # 迁移数据
        if migrate_skill(skill_name, dry_run):
            # 更新配置
            update_skill_config(skill_name, dry_run)
            # 清理旧目录
            cleanup_old_dirs(skill_name, dry_run)
            success_count += 1

    # 总结
    print("\n" + "=" * 60)
    print(f"📊 迁移总结")
    print("=" * 60)
    print(f"  总计: {len(skills_to_migrate)} 个 skill")
    print(f"  成功: {success_count} 个")
    print(f"  失败: {len(skills_to_migrate) - success_count} 个")

    if dry_run:
        print("\n💡 这是预览模式，添加 --no-dry-run 执行实际迁移")
    else:
        print("\n✅ 迁移完成！")
        print("\n下一步:")
        print("  1. 更新各 skill 的配置文件，指向新路径")
        print("  2. 测试各 skill 是否正常工作")
        print("  3. 确认无误后删除旧目录")


if __name__ == "__main__":
    main()
