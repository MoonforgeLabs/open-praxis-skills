#!/usr/bin/env python3
"""
open-praxis-ai-usage-stats 跨平台安装脚本

支持: macOS, Linux, Windows

用法:
    python3 install.py              # 安装到所有 runtime
    python3 install.py --claude     # 只安装到 Claude Code
    python3 install.py --codex      # 只安装到 Codex
    python3 install.py --openhuman  # 只安装到 OpenHuman
    python3 install.py --check      # 检查依赖状态
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional


# 配置
SKILL_NAME = "open-praxis-ai-usage-stats"
SKILL_DIR = Path(__file__).parent.parent.resolve()

# Runtime 配置
RUNTIMES = {
    "claude": {
        "skills_dir": Path.home() / ".claude" / "skills",
        "settings_path": Path.home() / ".claude" / "settings.json",
        "needs_hook": True,
    },
    "codex": {
        "skills_dir": Path.home() / ".codex" / "skills",
        "settings_path": None,  # Codex 使用 hooks.json
        "needs_hook": True,
    },
    "openhuman": {
        "skills_dir": Path.home() / ".openhuman" / "skills",
        "settings_path": None,
        "needs_hook": False,
    },
}


def create_symlink(target: Path, link_path: Path) -> bool:
    """创建软连接（跨平台）"""
    try:
        # 如果目标已存在，先删除
        if link_path.is_symlink():
            link_path.unlink()
        elif link_path.exists():
            if link_path.is_dir():
                shutil.rmtree(link_path)
            else:
                link_path.unlink()

        # 创建父目录
        link_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建软连接
        if sys.platform == "win32":
            # Windows 需要管理员权限创建软连接
            # 尝试使用 junction（不需要管理员权限）
            try:
                os.symlink(target, link_path, target_is_directory=True)
            except OSError:
                # 如果失败，尝试使用 junction
                import subprocess
                subprocess.run(["mklink", "/J", str(link_path), str(target)],
                             shell=True, check=True)
        else:
            # macOS/Linux
            os.symlink(target, link_path)

        return True
    except OSError as e:
        print(f"❌ 创建软连接失败: {e}")
        return False


def setup_claude_hook() -> bool:
    """配置 Claude Code hook"""
    settings_path = RUNTIMES["claude"]["settings_path"]

    try:
        # 读取现有配置
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}

        # 确保 hooks 结构存在
        if "hooks" not in config:
            config["hooks"] = {}
        if "PostToolUse" not in config["hooks"]:
            config["hooks"]["PostToolUse"] = []

        # 检查是否已配置
        hook_path = str(SKILL_DIR / "scripts" / "hook_collect.py")
        for hook in config["hooks"]["PostToolUse"]:
            hooks_list = hook.get("hooks", [])
            for h in hooks_list:
                if hook_path in h.get("command", ""):
                    print("✅ Claude Code hook 已配置")
                    return True

        # 添加 hook
        config["hooks"]["PostToolUse"].append({
            "matcher": "Skill|Bash|Read|Write|Edit|Agent",
            "hooks": [
                {
                    "type": "command",
                    "command": f"python3 {hook_path} || true"
                }
            ]
        })

        # 保存配置
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print("✅ Claude Code hook 配置成功")
        return True

    except Exception as e:
        print(f"❌ Claude Code hook 配置失败: {e}")
        return False


def setup_codex_hooks() -> bool:
    """配置 Codex hooks"""
    hooks_dir = RUNTIMES["codex"]["skills_dir"] / SKILL_NAME / "hooks"
    hooks_file = hooks_dir / "hooks.json"

    try:
        hooks_dir.mkdir(parents=True, exist_ok=True)

        # 检查是否已配置
        if hooks_file.exists():
            print("✅ Codex hooks 配置已存在")
            return True

        # 创建 hooks 配置
        hook_path = str(SKILL_DIR / "scripts" / "hook_collect.py")
        hooks_config = {
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "Skill|Bash|Read|Write|Edit|Agent",
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"python3 {hook_path} || true",
                                "async": False
                            }
                        ]
                    }
                ]
            }
        }

        with open(hooks_file, 'w', encoding='utf-8') as f:
            json.dump(hooks_config, f, indent=2, ensure_ascii=False)

        print("✅ Codex hooks 配置成功")
        return True

    except Exception as e:
        print(f"❌ Codex hooks 配置失败: {e}")
        return False


def set_permissions() -> bool:
    """设置脚本执行权限"""
    if sys.platform == "win32":
        # Windows 不需要设置执行权限
        return True

    scripts_dir = SKILL_DIR / "scripts"
    try:
        for script in scripts_dir.glob("*.py"):
            script.chmod(0o755)
        for script in scripts_dir.glob("*.sh"):
            script.chmod(0o755)
        print("✅ 脚本执行权限已设置")
        return True
    except Exception as e:
        print(f"⚠️  设置权限失败: {e}")
        return False


def install_runtime(runtime_name: str) -> bool:
    """安装到指定 runtime"""
    config = RUNTIMES[runtime_name]
    skills_dir = config["skills_dir"]
    skill_link = skills_dir / SKILL_NAME

    print(f"\n=== {runtime_name.capitalize()} ===")

    # 创建软连接
    if create_symlink(SKILL_DIR, skill_link):
        print(f"✅ 软连接已创建: {skill_link}")
    else:
        return False

    # 配置 hook（如果需要）
    if config["needs_hook"]:
        if runtime_name == "claude":
            setup_claude_hook()
        elif runtime_name == "codex":
            setup_codex_hooks()

    return True


def check_dependencies() -> Dict[str, bool]:
    """检查依赖状态"""
    results = {}

    # 检查各 runtime
    for runtime_name, config in RUNTIMES.items():
        skill_link = config["skills_dir"] / SKILL_NAME
        results[f"{runtime_name}_symlink"] = skill_link.is_symlink() or skill_link.exists()

    # 检查 Claude Code hook
    settings_path = RUNTIMES["claude"]["settings_path"]
    if settings_path.exists():
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            hooks = config.get("hooks", {}).get("PostToolUse", [])
            hook_configured = False
            for hook in hooks:
                for h in hook.get("hooks", []):
                    if "hook_collect.py" in h.get("command", ""):
                        hook_configured = True
            results["claude_hook"] = hook_configured
        except:
            results["claude_hook"] = False
    else:
        results["claude_hook"] = False

    # 检查 Codex hooks
    hooks_file = RUNTIMES["codex"]["skills_dir"] / SKILL_NAME / "hooks" / "hooks.json"
    results["codex_hook"] = hooks_file.exists()

    # 检查数据库
    db_path = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats" / "usage.db"
    results["database"] = db_path.exists()

    return results


def print_check_report(results: Dict[str, bool]):
    """打印检查报告"""
    print("\n" + "=" * 60)
    print("📊 open-praxis-ai-usage-stats 依赖检查报告")
    print("=" * 60)

    print("\n【软连接】")
    for runtime in ["claude", "codex", "openhuman"]:
        key = f"{runtime}_symlink"
        status = "✅" if results.get(key) else "❌"
        print(f"  {status} {runtime.capitalize()}")

    print("\n【Hook 配置】")
    print(f"  {'✅' if results.get('claude_hook') else '❌'} Claude Code")
    print(f"  {'✅' if results.get('codex_hook') else '❌'} Codex")
    print(f"  ➖ OpenHuman (不需要)")

    print("\n【数据存储】")
    print(f"  {'✅' if results.get('database') else '⚠️'} 数据库")

    ok_count = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n总结: ✅ {ok_count}/{total} 正常")
    print("=" * 60)


def main():
    # 解析参数
    args = sys.argv[1:]

    # 检查依赖
    if "--check" in args:
        results = check_dependencies()
        print_check_report(results)
        return

    # 确定要安装的 runtime
    runtimes_to_install = []
    if not args or "--all" in args:
        runtimes_to_install = list(RUNTIMES.keys())
    else:
        if "--claude" in args:
            runtimes_to_install.append("claude")
        if "--codex" in args:
            runtimes_to_install.append("codex")
        if "--openhuman" in args:
            runtimes_to_install.append("openhuman")

    if not runtimes_to_install:
        print("使用方法:")
        print("  python3 install.py              # 安装到所有 runtime")
        print("  python3 install.py --claude     # 只安装到 Claude Code")
        print("  python3 install.py --codex      # 只安装到 Codex")
        print("  python3 install.py --openhuman  # 只安装到 OpenHuman")
        print("  python3 install.py --check      # 检查依赖状态")
        return

    print(f"📦 安装 {SKILL_NAME}")
    print(f"   源目录: {SKILL_DIR}")
    print(f"   平台: {sys.platform}")

    # 安装到各 runtime
    success_count = 0
    for runtime in runtimes_to_install:
        if install_runtime(runtime):
            success_count += 1

    # 设置权限
    set_permissions()

    # 自动迁移数据
    print("\n=== 迁移历史数据 ===")
    try:
        # 导入 parsers 模块
        sys.path.insert(0, str(SKILL_DIR / "scripts"))
        from parsers import parse_all_runtimes
        from db import UsageDB
        from datetime import datetime, timedelta

        # 检查数据库是否为空
        db = UsageDB()
        count = db.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        if count == 0:
            print("📊 数据库为空，正在迁移历史数据...")
            # 迁移最近 30 天的数据
            since = datetime.now() - timedelta(days=30)
            records = parse_all_runtimes(since, runtime="all")

            if records:
                db.insert_events_batch(records)
                print(f"✅ 已迁移 {len(records)} 条历史记录")
            else:
                print("⚠️  没有找到历史数据")
        else:
            print(f"✅ 数据库已有 {count} 条记录")

        db.close()
    except Exception as e:
        print(f"⚠️  数据迁移失败: {e}")
        print("   可以手动运行: python3 scripts/usage_stats.py --migrate")

    # 显示结果
    print(f"\n🎉 安装完成！({success_count}/{len(runtimes_to_install)})")
    print(f"\n使用方法:")
    print(f"  python3 ~/.claude/skills/{SKILL_NAME}/scripts/usage_stats.py today")
    print(f"  python3 ~/.claude/skills/{SKILL_NAME}/scripts/generate_report.py --open")


if __name__ == "__main__":
    main()
