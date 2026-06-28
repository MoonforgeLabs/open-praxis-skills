#!/usr/bin/env python3
"""
增强版 Task Radar - 支持主线任务管理、状态查询、依赖跟踪、能力同步

用法:
    python3 radar_enhanced.py status                    # 查看所有主线任务状态
    python3 radar_enhanced.py status <area>             # 查看指定主线状态
    python3 radar_enhanced.py next                      # 查看所有主线的下一步行动
    python3 radar_enhanced.py next <area>               # 查看指定主线的下一步
    python3 radar_enhanced.py refs <area>               # 查看指定主线的参考资料
    python3 radar_enhanced.py deps <area>               # 查看指定主线的依赖
    python3 radar_enhanced.py competitors <area>        # 查看指定主线的竞品
    python3 radar_enhanced.py summary                   # 生成主线任务总结报告
    python3 radar_enhanced.py sync <area>               # 同步检查 reference 的最新状态
    python3 radar_enhanced.py sync-all                  # 批量同步所有 learned 任务
"""

import json
import sys
import subprocess
import re
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional

# 数据目录
DATA_DIR = Path.home() / ".praxis-skills" / "data" / "knowledge-radar"
TASKS_FILE = DATA_DIR / "tasks.jsonl"

# 主线任务定义
MAINLINES = {
    "code-understanding": {
        "title": "AI代码理解工作流",
        "description": "CodeGraph + Understand-Anything 双工具协同重塑",
        "priority": "P0",
        "status": "进行中",
        "next_steps": [
            "安装 CodeGraph 和 Understand-Anything",
            "测试代码理解功能",
            "整合到工作流中"
        ],
        "dependencies": ["CodeGraph", "Understand-Anything"],
        "competitors": ["codescope", "codebase-memory-mcp"],
        "references": []
    },
    "skill-creation": {
        "title": "创建 skill 工作流改造",
        "description": "skill 创建、策展和官方 skill 对齐",
        "priority": "P0",
        "status": "已完成",
        "next_steps": [
            "CI/CD 集成（可选）",
            "Shell lint（可选）",
            "Dashboard（可选）"
        ],
        "dependencies": ["praxis-skill-forge", "mott skills", "anthropics/skills"],
        "competitors": [],
        "references": []
    },
    "ai-os": {
        "title": "个人 AI OS 改造",
        "description": "AI OS 和 Agent 系统",
        "priority": "P0",
        "status": "进行中",
        "next_steps": [
            "研究 DeerFlow、Omnigent 等框架",
            "测试 Agent 调度层",
            "整合到外部系统"
        ],
        "dependencies": ["your-ai-os", "your-agent-framework", "deerflow", "tauri", "OpenHarness", "fay", "openapi", "IBM cuga", "Omnigent", "everOs", "ollama/ollama"],
        "competitors": [],
        "references": []
    },
    "rag-docs": {
        "title": "RAG 与文档处理 skill 改造",
        "description": "RAG 和文档处理技能",
        "priority": "P1",
        "status": "待开始",
        "next_steps": [
            "研究 html-anything 和 PixelRAG",
            "测试文档处理功能",
            "整合到 skill 中"
        ],
        "dependencies": ["praxis-document-export", "praxis-diagram", "microsoft/markitdown", "HKUDS/RAG-Anything", "openPencil"],
        "competitors": [],
        "references": []
    },
    "search-skills": {
        "title": "搜索 skill 改造",
        "description": "安全搜索和研究技能改造",
        "priority": "P1",
        "status": "进行中",
        "next_steps": [
            "研究 Agent-Reach 和 anysearch-skill",
            "测试搜索功能",
            "优化搜索策略"
        ],
        "dependencies": ["praxis-search-hub", "addyosmani/agent-skills"],
        "competitors": ["agent-reach", "anysearch-skill", "wiseflow"],
        "references": []
    },
    "daily-news": {
        "title": "每日新闻与监控 skill 改造",
        "description": "GitHub/新闻/视频/监控报告",
        "priority": "P1",
        "status": "进行中",
        "next_steps": [
            "整合 GitHub Trending 监控",
            "优化新闻聚合功能",
            "测试自动化报告"
        ],
        "dependencies": ["praxis-github-watchtower", "praxis-agent-reach-ops", "praxis-news-aggregator", "praxis-youtube-clipper", "external-intake"],
        "competitors": [],
        "references": []
    },
    "knowledge-base": {
        "title": "个人知识库改造",
        "description": "个人知识库和架构参考",
        "priority": "P2",
        "status": "待开始",
        "next_steps": [
            "研究 Obsidian 和第二大脑",
            "测试知识库功能",
            "整合到工作流中"
        ],
        "dependencies": ["awesome-architecture"],
        "competitors": [],
        "references": []
    },
    "skill-ecosystem": {
        "title": "有用 skill 生态整合",
        "description": "有用的外部 skill 生态系统",
        "priority": "P2",
        "status": "进行中",
        "next_steps": [
            "研究 everything-claude-code",
            "测试有用的 skill",
            "整合到工作流中"
        ],
        "dependencies": ["addyosmani/agent-skills", "mott skills", "superpowers", "ECC"],
        "competitors": [],
        "references": []
    },
    "business-skills": {
        "title": "business skill 改造",
        "description": "短视频、小红书、UI 自动化和业务工作流",
        "priority": "P3",
        "status": "待开始",
        "next_steps": [
            "研究 Pixelle-Video 和 MoneyPrinterTurbo",
            "测试短视频制作功能",
            "整合到业务工作流中"
        ],
        "dependencies": ["bytedance/UI-TARS-desktop", "Open-Generative-AI", "Pixelle", "FinceptTerminal", "calesthio/OpenMontage"],
        "competitors": [],
        "references": []
    },
    "stocks": {
        "title": "股票类型处理工作流",
        "description": "交易/投资工作流",
        "priority": "P3",
        "status": "待开始",
        "next_steps": [
            "研究 TradingAgents",
            "测试股票分析功能",
            "整合到工作流中"
        ],
        "dependencies": ["TradingAgents"],
        "competitors": [],
        "references": []
    },
    "patent-skills": {
        "title": "专利撰写 skill 改造",
        "description": "专利写作技能改造",
        "priority": "P2",
        "status": "未开始",
        "next_steps": [
            "研究专利写作工具",
            "测试专利生成功能",
            "整合到 skill 中"
        ],
        "dependencies": ["mott skills"],
        "competitors": [],
        "references": []
    },
    "design-tools": {
        "title": "AI 设计工具生态整合",
        "description": "AI 设计工具生态系统集成",
        "priority": "P1",
        "status": "待开始",
        "next_steps": [
            "研究 Claude Design 和 UI-TARS-desktop",
            "测试设计工具功能",
            "整合到工作流中"
        ],
        "dependencies": ["claude-design", "UI-TARS-desktop", "Codex-Product-Design"],
        "competitors": [],
        "references": []
    },
    "digital-human": {
        "title": "数字人与虚拟形象",
        "description": "数字人和虚拟形象工作流",
        "priority": "P2",
        "status": "待开始",
        "next_steps": [
            "研究 Fay 和 OpenTalking",
            "测试数字人功能",
            "整合到工作流中"
        ],
        "dependencies": ["Fay", "OpenTalking"],
        "competitors": [],
        "references": []
    },
    "content-distribution": {
        "title": "多平台内容分发工作流",
        "description": "多平台内容分发工作流",
        "priority": "P3",
        "status": "待开始",
        "next_steps": [
            "研究 AI 营销智能体",
            "测试内容分发功能",
            "整合到工作流中"
        ],
        "dependencies": ["ai-marketing-agent"],
        "competitors": [],
        "references": []
    }
}


def load_tasks() -> List[Dict[str, Any]]:
    """加载所有任务"""
    if not TASKS_FILE.exists():
        return []

    tasks = []
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks


def get_area_tasks(tasks: List[Dict], area: str) -> List[Dict]:
    """获取指定区域的任务"""
    return [t for t in tasks if t.get('area') == area]


def show_status(area: str = None):
    """显示主线任务状态"""
    tasks = load_tasks()

    if area:
        if area not in MAINLINES:
            print(f"❌ 未知的主线任务: {area}")
            print(f"可用的主线任务: {', '.join(MAINLINES.keys())}")
            return

        mainline = MAINLINES[area]
        area_tasks = get_area_tasks(tasks, area)

        print(f"\n{'='*60}")
        print(f"【{area}】{mainline['title']}")
        print(f"{'='*60}")
        print(f"描述: {mainline['description']}")
        print(f"优先级: {mainline['priority']}")
        print(f"状态: {mainline['status']}")
        print(f"任务数: {len(area_tasks)}")

        if mainline['next_steps']:
            print(f"\n下一步行动:")
            for i, step in enumerate(mainline['next_steps'], 1):
                print(f"  {i}. {step}")

        if mainline['dependencies']:
            print(f"\n依赖项目:")
            for dep in mainline['dependencies']:
                print(f"  - {dep}")

        if mainline['competitors']:
            print(f"\n竞品:")
            for comp in mainline['competitors']:
                print(f"  - {comp}")

        if area_tasks:
            print(f"\n历史资料 ({len(area_tasks)} 条):")
            for t in area_tasks[:5]:
                refs = t.get('references', [])
                ref_str = f" [链接: {refs[0]}]" if refs else ""
                print(f"  - {t['title'][:60]}{ref_str}")
            if len(area_tasks) > 5:
                print(f"  ... 还有 {len(area_tasks)-5} 条")
    else:
        print(f"\n{'='*60}")
        print("主线任务状态总览")
        print(f"{'='*60}\n")

        for area, mainline in sorted(MAINLINES.items()):
            area_tasks = get_area_tasks(tasks, area)
            status_icon = "✅" if mainline['status'] == "已完成" else "🔄" if mainline['status'] == "进行中" else "⏳"
            print(f"{status_icon} [{mainline['priority']}] {area}: {mainline['title']}")
            print(f"   状态: {mainline['status']} | 任务数: {len(area_tasks)}")
            if mainline['next_steps']:
                print(f"   下一步: {mainline['next_steps'][0]}")
            print()


def show_next(area: str = None):
    """显示下一步行动"""
    if area:
        if area not in MAINLINES:
            print(f"❌ 未知的主线任务: {area}")
            return

        mainline = MAINLINES[area]
        print(f"\n【{area}】{mainline['title']} - 下一步行动")
        print(f"{'='*60}")

        if mainline['next_steps']:
            for i, step in enumerate(mainline['next_steps'], 1):
                print(f"  {i}. {step}")
        else:
            print("  暂无下一步行动")
    else:
        print(f"\n{'='*60}")
        print("所有主线任务的下一步行动")
        print(f"{'='*60}\n")

        for area, mainline in sorted(MAINLINES.items()):
            if mainline['next_steps']:
                print(f"【{area}】{mainline['title']}")
                print(f"  下一步: {mainline['next_steps'][0]}")
                print()


def show_refs(area: str):
    """显示参考资料"""
    tasks = load_tasks()
    area_tasks = get_area_tasks(tasks, area)

    if not area_tasks:
        print(f"❌ 没有找到 {area} 的参考资料")
        return

    print(f"\n【{area}】参考资料 ({len(area_tasks)} 条)")
    print(f"{'='*60}")

    for t in area_tasks:
        refs = t.get('references', [])
        ref_str = f" [链接: {refs[0]}]" if refs else ""
        print(f"- {t['title']}{ref_str}")
        if t.get('notes'):
            print(f"  备注: {t['notes'][:80]}")


def show_deps(area: str = None):
    """显示依赖"""
    if area:
        if area not in MAINLINES:
            print(f"❌ 未知的主线任务: {area}")
            return

        mainline = MAINLINES[area]
        print(f"\n【{area}】{mainline['title']} - 依赖")
        print(f"{'='*60}")

        if mainline['dependencies']:
            for dep in mainline['dependencies']:
                print(f"  - {dep}")
        else:
            print("  暂无依赖")
    else:
        print(f"\n{'='*60}")
        print("所有主线任务的依赖")
        print(f"{'='*60}\n")

        for area, mainline in sorted(MAINLINES.items()):
            if mainline['dependencies']:
                print(f"【{area}】{mainline['title']}")
                for dep in mainline['dependencies']:
                    print(f"  - {dep}")
                print()


def show_competitors(area: str = None):
    """显示竞品"""
    if area:
        if area not in MAINLINES:
            print(f"❌ 未知的主线任务: {area}")
            return

        mainline = MAINLINES[area]
        print(f"\n【{area}】{mainline['title']} - 竞品")
        print(f"{'='*60}")

        if mainline['competitors']:
            for comp in mainline['competitors']:
                print(f"  - {comp}")
        else:
            print("  暂无竞品")
    else:
        print(f"\n{'='*60}")
        print("所有主线任务的竞品")
        print(f"{'='*60}\n")

        for area, mainline in sorted(MAINLINES.items()):
            if mainline['competitors']:
                print(f"【{area}】{mainline['title']}")
                for comp in mainline['competitors']:
                    print(f"  - {comp}")
                print()


def show_summary():
    """生成总结报告"""
    tasks = load_tasks()

    print(f"\n{'='*60}")
    print("Task Radar 总结报告")
    print(f"{'='*60}\n")

    # 统计
    total_tasks = len(tasks)
    areas_count = len(MAINLINES)

    print(f"📊 统计:")
    print(f"  - 总任务数: {total_tasks}")
    print(f"  - 主线任务数: {areas_count}")

    # 按优先级统计
    priority_count = defaultdict(int)
    for mainline in MAINLINES.values():
        priority_count[mainline['priority']] += 1

    print(f"\n📈 按优先级:")
    for p in ['P0', 'P1', 'P2', 'P3']:
        if p in priority_count:
            print(f"  - {p}: {priority_count[p]} 个主线")

    # 按状态统计
    status_count = defaultdict(int)
    for mainline in MAINLINES.values():
        status_count[mainline['status']] += 1

    print(f"\n📈 按状态:")
    for status, count in status_count.items():
        print(f"  - {status}: {count} 个主线")

    # 重点任务
    print(f"\n🎯 重点任务 (P0):")
    for area, mainline in sorted(MAINLINES.items()):
        if mainline['priority'] == 'P0':
            area_tasks = get_area_tasks(tasks, area)
            print(f"  - {area}: {mainline['title']} ({len(area_tasks)} 条资料)")

    # 待办事项
    print(f"\n📝 待办事项:")
    for area, mainline in sorted(MAINLINES.items()):
        if mainline['next_steps']:
            print(f"  - {area}: {mainline['next_steps'][0]}")


def parse_github_url(ref: str) -> Optional[tuple]:
    """解析 GitHub URL 或 owner/repo 格式"""
    # 处理 URL 格式
    github_url_pattern = r'https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/.*)?$'
    match = re.match(github_url_pattern, ref)
    if match:
        return match.group(1), match.group(2)

    # 处理 owner/repo 格式
    if '/' in ref and not ref.startswith('http'):
        parts = ref.split('/')
        if len(parts) == 2:
            return parts[0], parts[1]

    return None


def check_github_repo(owner: str, repo: str) -> Dict[str, Any]:
    """检查 GitHub 仓库的最新状态"""
    result = {
        "exists": False,
        "stars": 0,
        "last_updated": None,
        "recent_commits": [],
        "error": None
    }

    try:
        # 使用 gh CLI 获取仓库信息
        cmd = f"gh api repos/{owner}/{repo} --jq '.stargazers_count, .updated_at'"
        output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)

        if output.returncode == 0:
            lines = output.stdout.strip().split('\n')
            if len(lines) >= 2:
                result["exists"] = True
                result["stars"] = int(lines[0])
                result["last_updated"] = lines[1]

        # 获取最近的 commits
        cmd = f"gh api repos/{owner}/{repo}/commits?per_page=5 --jq '.[].commit.message' 2>/dev/null"
        output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)

        if output.returncode == 0 and output.stdout.strip():
            result["recent_commits"] = [m.strip() for m in output.stdout.strip().split('\n') if m.strip()][:3]

    except Exception as e:
        result["error"] = str(e)

    return result


def check_local_skill(skill_name: str) -> Dict[str, Any]:
    """检查本地 skill 的状态"""
    result = {
        "exists": False,
        "path": None,
        "last_modified": None,
        "files": []
    }

    # 检查可能的路径
    possible_paths = [
        Path.home() / ".claude" / "skills" / skill_name,
        Path.home() / "Documents" / "myCode" / "skills" / "praxis-skills" / "skills" / skill_name,
    ]

    for path in possible_paths:
        if path.exists():
            result["exists"] = True
            result["path"] = str(path)

            # 获取最后修改时间
            try:
                mtime = path.stat().st_mtime
                result["last_modified"] = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
            except:
                pass

            # 列出文件
            try:
                result["files"] = [f.name for f in path.iterdir() if f.is_file()][:10]
            except:
                pass

            break

    return result


def sync_task(area: str, show_all: bool = False):
    """同步检查指定任务的 reference 状态"""
    tasks = load_tasks()

    # 找到该 area 的主线任务
    mainline_task = None
    for t in tasks:
        if t.get('area') == area and 'mainline' in t.get('tags', []):
            mainline_task = t
            break

    if not mainline_task:
        print(f"❌ 未找到 {area} 的主线任务")
        return

    print(f"\n{'='*60}")
    print(f"🔄 同步检查: {mainline_task['title']}")
    print(f"{'='*60}")
    print(f"状态: {mainline_task.get('status', 'unknown')}")
    print(f"参考来源: {', '.join(mainline_task.get('references', []))}")

    # 获取已记录的 reference_state
    ref_state = mainline_task.get('reference_state', {})

    # 检查每个 reference
    new_capabilities = []
    updated_refs = []

    for ref in mainline_task.get('references', []):
        print(f"\n📍 检查: {ref}")

        # 解析 GitHub URL
        github_info = parse_github_url(ref)

        if github_info:
            owner, repo = github_info
            print(f"   GitHub: {owner}/{repo}")

            repo_info = check_github_repo(owner, repo)

            if repo_info["exists"]:
                print(f"   ⭐ Stars: {repo_info['stars']}")
                print(f"   📅 最后更新: {repo_info['last_updated']}")

                if repo_info["recent_commits"]:
                    print(f"   📝 最近提交:")
                    for commit in repo_info["recent_commits"][:3]:
                        print(f"      - {commit[:60]}...")

                # 对比已记录的状态
                recorded = ref_state.get(ref, {})
                if recorded:
                    last_checked = recorded.get('last_checked', 'never')
                    print(f"   🔍 上次检查: {last_checked}")

                    # 检查是否有新 capabilities
                    recorded_caps = set(recorded.get('capabilities', []))
                    # 这里可以扩展：从 commit message 中提取新功能
                else:
                    print(f"   ⚠️  未记录状态，建议更新 reference_state")

                updated_refs.append(ref)
            else:
                print(f"   ❌ 仓库不存在或无法访问")
                if repo_info["error"]:
                    print(f"   错误: {repo_info['error']}")

        else:
            # 检查本地 skill
            local_info = check_local_skill(ref)
            if local_info["exists"]:
                print(f"   📁 本地路径: {local_info['path']}")
                print(f"   📅 最后修改: {local_info['last_modified']}")
                if local_info["files"]:
                    print(f"   📄 文件: {', '.join(local_info['files'][:5])}")
            else:
                print(f"   ℹ️  非 GitHub 仓库，跳过检查")

    # 生成同步报告
    print(f"\n{'='*60}")
    print(f"📊 同步报告")
    print(f"{'='*60}")

    if updated_refs:
        print(f"\n✅ 已检查 {len(updated_refs)} 个 GitHub 仓库:")
        for ref in updated_refs:
            print(f"   - {ref}")

    # 从该 area 的参考文章中提取新信息
    area_tasks = [t for t in tasks if t.get('area') == area and 'mainline' not in t.get('tags', [])]
    if area_tasks:
        print(f"\n📚 该领域有 {len(area_tasks)} 条参考文章待学习")
        for t in area_tasks[:5]:
            print(f"   - {t['title'][:50]}...")

    # 建议
    print(f"\n💡 建议:")
    print(f"   1. 定期运行 sync 检查 reference 更新")
    print(f"   2. 关注最近 commits 中的新功能")
    print(f"   3. 将新能力同步到本地 skill")

    return updated_refs


def sync_all(notify: bool = False):
    """批量同步所有 learned 状态的任务"""
    tasks = load_tasks()

    # 找到所有 learned 状态的主线任务
    learned_tasks = []
    for t in tasks:
        if t.get('status') == 'learned' and 'mainline' in t.get('tags', []):
            learned_tasks.append(t)

    if not learned_tasks:
        print("ℹ️  没有找到 learned 状态的任务")
        return

    print(f"\n{'='*60}")
    print(f"🔄 批量同步: {len(learned_tasks)} 个 learned 任务")
    print(f"{'='*60}")

    sync_results = []
    for t in learned_tasks:
        area = t.get('area')
        if area:
            result = sync_task(area)
            sync_results.append({
                "area": area,
                "title": t.get('title', ''),
                "updated_refs": result if result else []
            })
            print()

    # Optional: send DingTalk notification
    if notify:
        send_dingtalk_notification(sync_results)


def send_dingtalk_notification(sync_results: list):
    """Send DingTalk sync notification (optional feature)"""
    try:
        # Import DingTalk notification module (optional dependency)
        sys.path.insert(0, str(Path(__file__).parent))
        from dingtalk_notify import load_config, send_message

        config = load_config()
        if not config or not config.get('webhook'):
            print("ℹ️  DingTalk notification not configured, skipping")
            return

        # 构建通知内容
        content_lines = ["### 📊 知识雷达同步报告\n"]

        for result in sync_results:
            area = result['area']
            title = result['title']
            updated_refs = result['updated_refs']

            content_lines.append(f"**{area}**: {title}")
            if updated_refs:
                content_lines.append(f"- 已检查 {len(updated_refs)} 个 GitHub 仓库")
            else:
                content_lines.append("- 无 GitHub 仓库更新")
            content_lines.append("")

        content_lines.append(f"\n📅 扫描时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        content_lines.append("\n💡 运行 `python3 scripts/radar_enhanced.py sync <area>` 查看详情")

        content = "\n".join(content_lines)

        # 发送消息
        send_message(
            config['webhook'],
            "知识雷达同步报告",
            content,
            config.get('secret')
        )

    except Exception as e:
        print(f"⚠️  DingTalk notification failed: {e}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]
    area = sys.argv[2] if len(sys.argv) > 2 else None

    if command == "status":
        show_status(area)
    elif command == "next":
        show_next(area)
    elif command == "refs":
        if not area:
            print("❌ 请指定主线任务名称")
            return
        show_refs(area)
    elif command == "deps":
        show_deps(area)
    elif command == "competitors":
        show_competitors(area)
    elif command == "summary":
        show_summary()
    elif command == "sync":
        if not area:
            print("❌ 请指定主线任务名称")
            return
        sync_task(area)
    elif command == "sync-all":
        notify = "--notify" in sys.argv
        sync_all(notify=notify)
    else:
        print(f"❌ 未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
