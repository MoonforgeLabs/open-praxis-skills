#!/usr/bin/env python3
"""检查 praxis-ai-usage-stats 的依赖状态

用法:
    python3 check_dependencies.py           # 检查所有依赖
    python3 check_dependencies.py --fix     # 自动修复缺失的依赖
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List


def check_hook_config(runtime: str) -> Dict[str, Any]:
    """检查 hook 配置"""
    if runtime == "claude":
        settings_path = Path.home() / ".claude" / "settings.json"
        if not settings_path.exists():
            return {"status": "missing", "detail": "settings.json 不存在"}

        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            hooks = config.get("hooks", {}).get("PostToolUse", [])
            for hook in hooks:
                hook_list = hook.get("hooks", [])
                for h in hook_list:
                    command = h.get("command", "")
                    if "hook_collect.py" in command:
                        return {"status": "ok", "detail": "PostToolUse hook 已配置"}

            return {"status": "missing", "detail": "PostToolUse hook 未配置"}
        except Exception as e:
            return {"status": "error", "detail": f"读取配置失败: {e}"}

    elif runtime == "codex":
        hooks_path = Path.home() / ".codex" / "skills" / "praxis-ai-usage-stats" / "hooks" / "hooks.json"
        if hooks_path.exists():
            return {"status": "ok", "detail": "Codex hooks 配置已存在"}
        else:
            return {"status": "missing", "detail": "Codex hooks 配置不存在"}

    elif runtime == "openhuman":
        return {"status": "not_applicable", "detail": "OpenHuman 不需要 hook 配置"}

    return {"status": "unknown", "detail": "未知 runtime"}


def check_symlink(runtime: str) -> Dict[str, Any]:
    """检查软连接"""
    skill_dirs = {
        "claude": Path.home() / ".claude" / "skills" / "praxis-ai-usage-stats",
        "codex": Path.home() / ".codex" / "skills" / "praxis-ai-usage-stats",
        "openhuman": Path.home() / ".openhuman" / "skills" / "praxis-ai-usage-stats",
    }

    skill_dir = skill_dirs.get(runtime)
    if not skill_dir:
        return {"status": "error", "detail": "未知 runtime"}

    if skill_dir.is_symlink():
        target = skill_dir.resolve()
        return {"status": "ok", "detail": f"软连接指向: {target}"}
    elif skill_dir.exists():
        return {"status": "warning", "detail": "目录存在，但不是软连接（建议使用软连接）"}
    else:
        return {"status": "missing", "detail": "目录不存在"}


def check_database() -> Dict[str, Any]:
    """检查数据库"""
    db_path = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats" / "usage.db"
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        return {"status": "ok", "detail": f"数据库已创建 ({size_mb:.1f} MB)"}
    else:
        return {"status": "missing", "detail": "数据库不存在"}


def check_scripts() -> Dict[str, Any]:
    """检查脚本权限"""
    scripts_dir = Path.home() / ".claude" / "skills" / "praxis-ai-usage-stats" / "scripts"
    if not scripts_dir.exists():
        return {"status": "missing", "detail": "scripts 目录不存在"}

    required_scripts = [
        "usage_stats.py",
        "hook_collect.py",
        "hook_install.py",
        "generate_report.py",
        "auto_cleanup.py",
    ]

    missing = []
    for script in required_scripts:
        script_path = scripts_dir / script
        if not script_path.exists():
            missing.append(script)

    if missing:
        return {"status": "warning", "detail": f"缺少脚本: {', '.join(missing)}"}
    else:
        return {"status": "ok", "detail": "所有必需脚本都存在"}


def check_all_dependencies() -> Dict[str, Dict[str, Any]]:
    """检查所有依赖"""
    results = {}

    # 检查各 runtime 的软连接
    for runtime in ["claude", "codex", "openhuman"]:
        results[f"{runtime}_symlink"] = check_symlink(runtime)

    # 检查各 runtime 的 hook 配置
    for runtime in ["claude", "codex", "openhuman"]:
        results[f"{runtime}_hook"] = check_hook_config(runtime)

    # 检查数据库
    results["database"] = check_database()

    # 检查脚本
    results["scripts"] = check_scripts()

    return results


def print_report(results: Dict[str, Dict[str, Any]]):
    """打印检查报告"""
    print("=" * 60)
    print("📊 praxis-ai-usage-stats 依赖检查报告")
    print("=" * 60)
    print()

    # 按类别分组
    categories = {
        "软连接": ["claude_symlink", "codex_symlink", "openhuman_symlink"],
        "Hook 配置": ["claude_hook", "codex_hook", "openhuman_hook"],
        "数据存储": ["database"],
        "脚本文件": ["scripts"],
    }

    for category, keys in categories.items():
        print(f"【{category}】")
        for key in keys:
            if key in results:
                result = results[key]
                status = result["status"]
                detail = result["detail"]

                if status == "ok":
                    emoji = "✅"
                elif status == "warning":
                    emoji = "⚠️"
                elif status == "missing":
                    emoji = "❌"
                elif status == "not_applicable":
                    emoji = "➖"
                else:
                    emoji = "❓"

                # 提取 runtime 名称
                runtime = key.split("_")[0].capitalize()
                if runtime == "Claude":
                    runtime = "Claude Code"
                elif runtime == "Codex":
                    runtime = "Codex"
                elif runtime == "Openhuman":
                    runtime = "OpenHuman"
                else:
                    runtime = key

                print(f"  {emoji} {runtime}: {detail}")
        print()

    # 统计
    ok_count = sum(1 for r in results.values() if r["status"] == "ok")
    warning_count = sum(1 for r in results.values() if r["status"] == "warning")
    missing_count = sum(1 for r in results.values() if r["status"] == "missing")

    print("=" * 60)
    print(f"总结: ✅ {ok_count} 正常 | ⚠️ {warning_count} 警告 | ❌ {missing_count} 缺失")
    print("=" * 60)


def print_fix_instructions(results: Dict[str, Dict[str, Any]]):
    """打印修复说明"""
    print()
    print("🔧 修复说明")
    print("=" * 60)

    has_missing = False

    # 检查是否需要创建软连接
    for runtime in ["claude", "codex", "openhuman"]:
        key = f"{runtime}_symlink"
        if key in results and results[key]["status"] == "missing":
            if not has_missing:
                print()
                print("1. 创建软连接:")
                print("   运行安装脚本:")
                print("   ~/.claude/skills/praxis-skill-forge/scripts/install_skill.sh praxis-ai-usage-stats")
                print()
                print("   或手动创建:")
                has_missing = True

            skill_dirs = {
                "claude": "~/.claude/skills/praxis-ai-usage-stats",
                "codex": "~/.codex/skills/praxis-ai-usage-stats",
                "openhuman": "~/.openhuman/skills/praxis-ai-usage-stats",
            }
            print(f"   ln -s /path/to/praxis-ai-usage-stats {skill_dirs[runtime]}")

    # 检查是否需要配置 hook
    for runtime in ["claude", "codex"]:
        key = f"{runtime}_hook"
        if key in results and results[key]["status"] == "missing":
            if not has_missing:
                print()
                has_missing = True

            if runtime == "claude":
                print("2. 配置 Claude Code hook:")
                print("   python3 ~/.claude/skills/praxis-ai-usage-stats/scripts/hook_install.py install")
                print()
            elif runtime == "codex":
                print("3. 配置 Codex hook:")
                print("   创建 ~/.codex/skills/praxis-ai-usage-stats/hooks/hooks.json")
                print()

    if not has_missing:
        print("✅ 所有依赖都已满足，无需修复！")


def main():
    fix_mode = "--fix" in sys.argv

    results = check_all_dependencies()
    print_report(results)

    if fix_mode:
        print_fix_instructions(results)
    else:
        # 检查是否有缺失
        has_missing = any(r["status"] == "missing" for r in results.values())
        if has_missing:
            print()
            print("💡 提示: 运行 'python3 check_dependencies.py --fix' 查看修复说明")


if __name__ == "__main__":
    main()
