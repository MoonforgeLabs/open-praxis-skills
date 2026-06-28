#!/usr/bin/env python3
"""Import knowledge-radar-mapping.md records into tasks.jsonl."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Mapping of area to records from knowledge-radar-mapping.md
MAPPING_DATA = {
    "code-understanding": [
        {"date": "2026-06-22", "content": "编程 Agent 的地图之争：codebase-memory-mcp、codegraph、codescope", "link": "https://m.toutiao.com/is/AWshoNWVeuU/"},
        {"date": "2026-06-22", "content": "CodeGraph 与 Understand Anything：为项目搭建知识图谱", "link": "https://m.toutiao.com/is/1bzirMlk2vk/"},
        {"date": "2026-06-25", "content": "CodeGraph+Understand-Anything 双工具协同重塑 AI 代码理解工作流", "link": "https://m.toutiao.com/is/jUq04E6dtho/"},
        {"date": "2026-06-25", "content": "Understand-Anything 用知识图谱搞懂代码库", "link": "https://m.toutiao.com/is/JhN9nvkVZk4/"},
    ],
    "skill-creation": [
        {"date": "2026-04-25", "content": "保姆级教程！一个视频彻底搞懂 Claude Code Skill", "link": "https://m.toutiao.com/is/IMIO9uCHe-E/"},
        {"date": "2026-05-24", "content": "book-to-skill：将任何书籍文档变成 Skill（PDF/EPUB/DOCX 转技能文件）", "link": "https://m.toutiao.com/is/rQNBB74ZbHU/"},
        {"date": "2026-06-15", "content": "book-to-skills 再推：技术书籍转 Claude Code 技能文件上趋势榜", "link": "https://m.toutiao.com/is/rZHE7qogNaE/"},
        {"date": "2026-03-29", "content": "十个顶级 Claude Code Skills", "link": "https://m.toutiao.com/is/4HWjBbsxRfg/"},
        {"date": "2026-04-10", "content": "Claude Skill 榜单：每个都是神器", "link": "https://m.toutiao.com/is/-OfWDWs1YMM/"},
        {"date": "2026-04-10", "content": "装了这 6 个 AI Skill 后再也没加过班", "link": "https://m.toutiao.com/is/RbknIb1rT9o/"},
        {"date": "2026-04-16", "content": "Karpathy 的 CLAUDE.md 28K+ Star", "link": "https://m.toutiao.com/is/EeL7x5I1xYA/"},
        {"date": "2026-05-12", "content": "2026 Claude Code 必装十大 Skill", "link": "https://m.toutiao.com/is/32flTEKZ5xs/"},
        {"date": "2026-05-14", "content": "字节 AI 编程团队推荐的 10 个核心 Skills", "link": "https://m.toutiao.com/is/nH7d7m42DKs/"},
        {"date": "2026-05-16", "content": "Harness 最佳实践：Java SpringBoot + OpenSpec + Claude Code", "link": "https://m.toutiao.com/is/DEC5vmOOsI0/"},
        {"date": "2026-05-16", "content": "2026 实用 Skills 清单必装版", "link": "https://m.toutiao.com/is/e3nBGvGd5xo/"},
        {"date": "2026-05-22", "content": "吴恩达 Claude Skills 中文使用手册", "link": "https://m.toutiao.com/is/YcSb3kOysEo/"},
        {"date": "2026-05-27", "content": "40 个高阶 Skill", "link": "https://m.toutiao.com/is/8BoQdFvwG40/"},
        {"date": "2026-05-27", "content": "50 个必装技能", "link": "https://m.toutiao.com/is/4Nr0i962KRM/"},
        {"date": "2026-05-27", "content": "15 个高星 Skills 盘点", "link": "https://m.toutiao.com/is/vuSFXZ_sWfg/"},
        {"date": "2026-06-12", "content": "Codex 必装的 10 个插件", "link": "https://m.toutiao.com/is/S4vayOSWjLk/"},
        {"date": "2026-06-14", "content": "Google 开源 agent-skills 套件，21 项能力", "link": "https://m.toutiao.com/is/RHPx80tFXDE/"},
        {"date": "2026-06-16", "content": "Google 开源 21 项工程技能", "link": "https://m.toutiao.com/is/cEsvF8EF8Ec/"},
        {"date": "2026-06-21", "content": "中文内容创作最强 10 大 Skill", "link": "https://m.toutiao.com/is/tb4eVVNUBLM/"},
        {"date": "2026-06-24", "content": "claude-code-best-practice 从氛围编程进阶到智能体工程", "link": "https://m.toutiao.com/is/G_43L5vfMT0/"},
    ],
    "ai-os": [
        {"date": "2026-05-12", "content": "OpenSpec、Superpowers 和 Harness：AI 工程化开发三层拼图", "link": "https://m.toutiao.com/is/RUTXt4U7Gew/"},
        {"date": "2026-05-14", "content": "openhuman 霸榜，superpowers 杀入前三", "link": "https://m.toutiao.com/is/d3yDl_y882g/"},
        {"date": "2026-05-18", "content": "Hermes Agent 8 大开源神器", "link": "https://m.toutiao.com/is/lXuXghuPUNw/"},
        {"date": "2026-06-04", "content": "48 小时 2 万星（openhuman）", "link": "https://m.toutiao.com/is/yCnug6UgMfM/"},
        {"date": "2026-06-09", "content": "Agency Agents：106K Star AI 专家角色库", "link": "https://m.toutiao.com/is/f_7bITfs0N4/"},
        {"date": "2026-06-15", "content": "50K+ Star 最强 Agent 教程", "link": "https://m.toutiao.com/is/PB-jzBR_Jxk/"},
        {"date": "2026-06-15", "content": "186K Star Hermes Agent 自主升级 AI 能力", "link": "https://m.toutiao.com/is/8mFzLzD1MAE/"},
        {"date": "2026-06-15", "content": "AI Agent 生态星标暴涨 25K（87K → 112K）", "link": "https://m.toutiao.com/is/kzff0o7PCq0/"},
        {"date": "2026-06-18", "content": "112K Star：200 个 AI 员工", "link": "https://m.toutiao.com/is/4rO_zdSHBQs/"},
        {"date": "2026-06-21", "content": "Fay：开源数字人 Agent 框架", "link": "https://m.toutiao.com/is/KXBCjnwqn4I/"},
        {"date": "2026-06-21", "content": "EverOS：AI Agent 的自进化长期记忆系统", "link": "https://m.toutiao.com/is/OxlDNil83Vs/"},
        {"date": "2026-06-22", "content": "OpenTalking：面向实时对话的开源数字人产线", "link": "https://m.toutiao.com/is/G_-9DjbGu60/"},
        {"date": "2026-06-22", "content": "PewDiePie 开源 AI 工作台（4 天 5 万星）", "link": "https://m.toutiao.com/is/FMrODfIE34s/"},
        {"date": "2026-06-22", "content": "DeerFlow（字节跳动）", "link": "https://m.toutiao.com/is/WfeQkg8MDu8/"},
        {"date": "2026-06-23", "content": "Loop：让 agent 自己干到达标 + 7 个 AI Loop prompt", "link": "https://m.toutiao.com/is/UkMbEdpZf-Y/"},
        {"date": "2026-06-23", "content": "Flowise：拖拽搭建 AI 智能体（36K Star）", "link": "https://m.toutiao.com/is/Kk1Fw4gKfYk/"},
        {"date": "2026-06-24", "content": "omnigent：一个框架打通 Claude Code、Codex、Pi 所有 Agent", "link": "https://m.toutiao.com/is/yX2l5X-50U0/"},
        {"date": "2026-06-24", "content": "Google ADK + A2A 协议搭建多 Agent", "link": "https://m.toutiao.com/is/a-BMwtpOmhQ/"},
        {"date": "2026-06-24", "content": "gstack：Hacker News 老板开源虚拟 AI 研发团队框架", "link": "https://m.toutiao.com/is/bHXcCtGaigs/"},
        {"date": "2026-06-24", "content": "Agent 元调度层（Claude Code 之上）", "link": "https://m.toutiao.com/is/ySWZrb-C-tY/"},
        {"date": "2026-06-25", "content": "IBM CUGA 框架：一行代码跑 Agent", "link": "https://m.toutiao.com/is/dyCGk3WesdM/"},
        {"date": "2026-06-25", "content": "OpenHarness：\"元马具\"架构深度解析", "link": "https://m.toutiao.com/is/uT9H6tqr4RY/"},
        {"date": "2026-06-25", "content": "pi-agent：58K Star 开源编码 Agent", "link": "https://m.toutiao.com/is/lLw3nQawo7Q/"},
    ],
    "rag-docs": [
        {"date": "2026-05-19", "content": "html-anything：Claude Code 作者提到的 HTML 效果", "link": "https://m.toutiao.com/is/_QegAnpzuX0/"},
        {"date": "2026-06-23", "content": "PixelRAG：100% 开源可视化搜索系统，跳过 HTML 解析", "link": "https://m.toutiao.com/is/LGLQSg2eaQQ/"},
        {"date": "2026-06-24", "content": "Google OKF：AI 知识库通用格式", "link": "https://m.toutiao.com/is/lRGtgyqNTyc/"},
    ],
    "search-skills": [
        {"date": "2026-06-16", "content": "Agent-Reach：30.8K Star，让 AI Agent 真正上网冲浪", "link": "https://m.toutiao.com/is/uc3q2R6MRNE/"},
        {"date": "2026-06-21", "content": "anysearch-skill：搜索调用量突破 400 万次", "link": "https://m.toutiao.com/is/nA52qfhIr1w/"},
        {"date": "2026-06-22", "content": "wiseflow", "link": "https://github.com/TeamWiseFlow/wiseflow"},
        {"date": "2026-06-15", "content": "让 Codex/Claude Code 能读 YouTube、B 站、小红书、Twitter 等", "link": "https://m.toutiao.com/is/6mshklM9S3A/"},
    ],
    "daily-news": [
        {"date": "2026-06-11", "content": "GitHub 热门项目一周整理（6.1-6.7）", "link": "https://m.toutiao.com/is/BcKCx-HU5DQ/"},
        {"date": "2026-06-24", "content": "近 7 天 GitHub 飙升 AI 项目（Trending 榜单）", "link": "https://m.toutiao.com/is/z6yyvzD5E9Q/"},
        {"date": "2026-06-24", "content": "GitHub 今日上星最快的开源项目", "link": "https://m.toutiao.com/is/0Da7sJWLLPA/"},
    ],
    "knowledge-base": [
        {"date": "2026-06-11", "content": "AI 时代为什么推荐每个人使用 Obsidian", "link": "https://m.toutiao.com/is/Jser9bwoDn4/"},
        {"date": "2026-06-14", "content": "\"第二大脑\"开源 349K Star，把所有笔记变成 AI 知识库", "link": "https://m.toutiao.com/is/CBfx3dPzTSM/"},
        {"date": "2026-06-21", "content": "LLM Wiki V2（基于 Karpathy gist 更新）", "link": "https://m.toutiao.com/is/u9ef0PKeSX8/"},
        {"date": "2026-06-25", "content": "awesome-architecture：架构图谱，AI 时代的架构判断力知识库", "link": "https://m.toutiao.com/is/_axGikJ9c7c/"},
    ],
    "skill-ecosystem": [
        {"date": "2026-03-18", "content": "GitHub 7 万+ Star Claude Code 最佳实践", "link": "https://m.toutiao.com/is/pG62VoS40CE/"},
        {"date": "2026-03-31", "content": "Claude Code 创始人 84 条实战精华", "link": "https://m.toutiao.com/is/Jo6quhi88fI/"},
        {"date": "2026-04-19", "content": "Google 工程师用 Claude Code 自动化 80% 工作", "link": "https://m.toutiao.com/is/gA1Brghy5YM/"},
        {"date": "2026-04-23", "content": "awesome-claude-code 解锁 Claude Code 潜力", "link": "https://m.toutiao.com/is/_NFJIcm7AGE/"},
        {"date": "2026-04-29", "content": "12 个让 AI 工程师效率起飞的神级 GitHub 仓库", "link": "https://m.toutiao.com/is/R3s8YyyTcMA/"},
        {"date": "2026-05-12", "content": "Anthropic 讲解如何用 Claude Code 做几乎所有事情", "link": "https://m.toutiao.com/is/GBPloas6lQ8/"},
        {"date": "2026-05-15", "content": "Claude Code 最佳实践 32K Star 开源", "link": "https://m.toutiao.com/is/PA-uk_yOAeA/"},
        {"date": "2026-05-16", "content": "witr 工具：一行命令查看进程来路（15.4K Star）", "link": "https://m.toutiao.com/is/Wfj7bWHo7zk/"},
        {"date": "2026-05-16", "content": "全网 Claude Code 入门资源合集", "link": "https://m.toutiao.com/is/-xw1JKAA-SE/"},
        {"date": "2026-05-16", "content": "Codex 最佳实践完整指南", "link": "https://m.toutiao.com/is/0eOVao0eNpg/"},
        {"date": "2026-05-18", "content": "Claude Code 自动配置插件", "link": "https://m.toutiao.com/is/NXI-gxzz1xo/"},
        {"date": "2026-05-19", "content": "CC-Connect：在飞书、微信调用 Claude Code", "link": "https://m.toutiao.com/is/F--oZnrkCds/"},
        {"date": "2026-05-27", "content": "everything-claude-code 169K Star", "link": "https://m.toutiao.com/is/83wooTK_3dM/"},
        {"date": "2026-06-01", "content": "CC Switch：让 Codex 接入任意国产大模型", "link": "https://m.toutiao.com/is/y7lE9NRHsns/"},
        {"date": "2026-06-11", "content": "阿里 open-code-review AI 代码审查工具", "link": "https://m.toutiao.com/is/hd-FEn1zn6Y/"},
        {"date": "2026-06-17", "content": "GitHub 648K Star 4 个超猛开源项目", "link": "https://m.toutiao.com/is/aJcypNHZXA8/"},
        {"date": "2026-06-20", "content": "5.3K Star 桌面神器，Claude/Codex/Cursor 一个窗口全搞定", "link": "https://m.toutiao.com/is/DeMY-MNtJCU/"},
        {"date": "2026-06-20", "content": "46.8K Star 开源版 Claude Design", "link": "https://m.toutiao.com/is/Ee53u9luwv0/"},
        {"date": "2026-06-21", "content": "Cloudflare 免费 AI 服务", "link": "https://m.toutiao.com/is/SnzG8Efs30k/"},
        {"date": "2026-06-23", "content": "国产 Codex（一比一复刻）", "link": "https://m.toutiao.com/is/TeK0LRd-RJI/"},
        {"date": "2026-06-24", "content": "Tabbit 国际版（美团，免费接入 GPT-5.5 等）", "link": "https://m.toutiao.com/is/Ty58TPTLwBs/"},
        {"date": "2026-06-26", "content": "NVIDIA 免费 API：100+ 顶级模型免费用", "link": "https://m.toutiao.com/is/-eYyseEr9CI/"},
    ],
    "business-skills": [
        {"date": "2026-06-15", "content": "新 AI 赚钱工具上线 GitHub", "link": "https://m.toutiao.com/is/OT09pVg5OPs/"},
        {"date": "2026-06-15", "content": "Pixelle-Video 22K Star：AI 全自动短视频引擎", "link": "https://m.toutiao.com/is/_bp-Ws047dk/"},
        {"date": "2026-06-15", "content": "MoneyPrinterTurbo：短视频制作门槛被打穿", "link": "https://m.toutiao.com/is/CkE1QaBSdBo/"},
        {"date": "2026-06-23", "content": "世界上第一个开源智能化视频制作系统", "link": "https://m.toutiao.com/is/ODRJcOnSQmE/"},
        {"date": "2026-06-24", "content": "OpenMontage（今日上星最快）", "link": "https://m.toutiao.com/is/0Da7sJWLLPA/"},
        {"date": "2026-06-24", "content": "开源 AI 原生设计编辑器（颠覆 Figma）", "link": "https://m.toutiao.com/is/a-PGaLVQqJU/"},
        {"date": "2026-06-26", "content": "14 平台一键分发 + 自动赚钱 AI 营销智能体", "link": "https://m.toutiao.com/is/qbNngo95YUE/"},
    ],
    "stocks": [
        {"date": "2026-06-22", "content": "63K Star 开源项目\"预测未来\"", "link": "https://m.toutiao.com/is/YxVpaybGuB8/"},
        {"date": "2026-06-24", "content": "46K Star AI 炒股工具（fork 比 star 还多）", "link": "https://m.toutiao.com/is/81Bf_krH00Q/"},
        {"date": "2026-06-24", "content": "TradingAgents 78K Star：AI 替你炒股，年化收益超 50%", "link": "https://m.toutiao.com/is/RpFinKsBeZA/"},
    ],
}


def create_record(area: str, item: dict, timestamp: str) -> dict:
    """Create a task record from mapping data."""
    return {
        "id": str(uuid.uuid4())[:8],
        "title": item["content"],
        "status": "inbox",
        "priority": "P2",
        "area": area,
        "source": "knowledge-radar-mapping",
        "tags": ["reference", "mapping"],
        "references": [item["link"]] if item.get("link") else [],
        "notes": f"Imported from knowledge-radar-mapping.md. Date: {item['date']}",
        "next_action": "",
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def main():
    store_path = Path.home() / ".praxis-skills" / "data" / "knowledge-radar" / "tasks.jsonl"
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    records = []
    for area, items in MAPPING_DATA.items():
        for item in items:
            records.append(create_record(area, item, timestamp))

    # Append to existing file
    with store_path.open("a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"Imported {len(records)} records to {store_path}")
    print(f"Breakdown by area:")
    for area, items in MAPPING_DATA.items():
        print(f"  {area}: {len(items)} records")


if __name__ == "__main__":
    main()
