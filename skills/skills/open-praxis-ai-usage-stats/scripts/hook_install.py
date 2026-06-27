#!/usr/bin/env python3
"""Hook 安装/卸载脚本 - 用于管理 Claude Code 的 PostToolUse hook

用法:
    python3 hook_install.py install   # 安装 hook
    python3 hook_install.py uninstall # 卸载 hook
    python3 hook_install.py status    # 查看状态
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional


# Claude Code 设置文件路径
SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
SETTINGS_BACKUP_PATH = Path.home() / ".claude" / "settings.json.backup"

# Hook 脚本路径
HOOK_SCRIPT = Path(__file__).parent / "hook_collect.py"

# Hook 配置
HOOK_CONFIG = {
    "matcher": "",
    "hooks": [
        {
            "type": "command",
            "command": f"python3 {HOOK_SCRIPT} || true"
        }
    ]
}


def load_settings() -> Dict[str, Any]:
    """加载 Claude Code 设置"""
    if not SETTINGS_PATH.exists():
        return {}

    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"警告: 无法读取设置文件: {e}")
        return {}


def save_settings(settings: Dict[str, Any]) -> bool:
    """保存 Claude Code 设置"""
    try:
        # 创建备份
        if SETTINGS_PATH.exists():
            backup_path = SETTINGS_BACKUP_PATH
            if backup_path.exists():
                # 保留原始备份
                pass
            else:
                import shutil
                shutil.copy2(SETTINGS_PATH, backup_path)
                print(f"已创建备份: {backup_path}")

        # 保存设置
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        return True
    except OSError as e:
        print(f"错误: 无法保存设置文件: {e}")
        return False


def get_hooks(settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    """获取当前 hooks 配置"""
    return settings.get("hooks", {}).get("PostToolUse", [])


def is_hook_installed(settings: Dict[str, Any]) -> bool:
    """检查 hook 是否已安装"""
    hooks = get_hooks(settings)
    hook_path = str(HOOK_SCRIPT)

    for hook in hooks:
        # 检查新的 hooks 数组格式
        hooks_list = hook.get("hooks", [])
        if isinstance(hooks_list, list):
            for h in hooks_list:
                if hook_path in h.get("command", ""):
                    return True
        # 兼容旧的 hook 字段格式
        if hook_path in hook.get("hook", ""):
            return True

    return False


def install_hook() -> bool:
    """安装 hook"""
    print("正在安装 PostToolUse hook...")

    # 检查 hook 脚本是否存在
    if not HOOK_SCRIPT.exists():
        print(f"错误: Hook 脚本不存在: {HOOK_SCRIPT}")
        return False

    # 加载设置
    settings = load_settings()

    # 初始化 hooks 结构
    if "hooks" not in settings:
        settings["hooks"] = {}
    if "PostToolUse" not in settings["hooks"]:
        settings["hooks"]["PostToolUse"] = []

    # 检查是否已安装
    if is_hook_installed(settings):
        print("Hook 已安装，无需重复安装")
        return True

    # 添加 hook
    settings["hooks"]["PostToolUse"].append(HOOK_CONFIG)

    # 保存设置
    if save_settings(settings):
        print("✅ Hook 安装成功!")
        print(f"Hook 配置: {HOOK_CONFIG}")
        print(f"设置文件: {SETTINGS_PATH}")
        return True
    else:
        print("❌ Hook 安装失败")
        return False


def uninstall_hook() -> bool:
    """卸载 hook"""
    print("正在卸载 PostToolUse hook...")

    # 加载设置
    settings = load_settings()

    # 检查是否已安装
    if not is_hook_installed(settings):
        print("Hook 未安装，无需卸载")
        return True

    # 移除 hook
    hook_path = str(HOOK_SCRIPT)
    hooks = get_hooks(settings)
    new_hooks = [h for h in hooks if hook_path not in h.get("hook", "")]

    settings["hooks"]["PostToolUse"] = new_hooks

    # 保存设置
    if save_settings(settings):
        print("✅ Hook 卸载成功!")
        return True
    else:
        print("❌ Hook 卸载失败")
        return False


def show_status() -> None:
    """显示 hook 状态"""
    print("📊 Hook 状态")
    print("=" * 50)

    # 检查设置文件
    if not SETTINGS_PATH.exists():
        print("❌ Claude Code 设置文件不存在")
        return

    # 加载设置
    settings = load_settings()

    # 检查 hooks 配置
    hooks = get_hooks(settings)

    if not hooks:
        print("⚠️  未配置任何 PostToolUse hook")
        return

    print(f"已配置 {len(hooks)} 个 PostToolUse hook:")
    print()

    for i, hook in enumerate(hooks, 1):
        matcher = hook.get("matcher", "")
        hook_cmd = hook.get("hook", "")

        print(f"  {i}. Matcher: {matcher or '(所有工具)'}")
        print(f"     Hook: {hook_cmd[:80]}...")
        print()

    # 检查 praxis-ai-usage-stats hook
    if is_hook_installed(settings):
        print("✅ praxis-ai-usage-stats hook 已安装")
    else:
        print("⚠️  praxis-ai-usage-stats hook 未安装")

    # 检查数据库
    db_path = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats" / "usage.db"
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"✅ 数据库已创建: {db_path} ({size_mb:.2f} MB)")
    else:
        print("⚠️  数据库未创建")

    # 检查事件日志
    events_file = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats" / "events.jsonl"
    if events_file.exists():
        with open(events_file, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        print(f"✅ 事件日志已创建: {events_file} ({line_count} 条记录)")
    else:
        print("⚠️  事件日志未创建")


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 hook_install.py install   # 安装 hook")
        print("  python3 hook_install.py uninstall # 卸载 hook")
        print("  python3 hook_install.py status    # 查看状态")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "install":
        success = install_hook()
        sys.exit(0 if success else 1)
    elif command == "uninstall":
        success = uninstall_hook()
        sys.exit(0 if success else 1)
    elif command == "status":
        show_status()
    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
