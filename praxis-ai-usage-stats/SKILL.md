---
name: praxis-ai-usage-stats
description: >
  Use when the user asks about AI usage statistics, tool stats, skill rankings,
  or cost tracking. Captures tool/skill/agent calls across Claude Code, Codex,
  and OpenHuman with SQLite persistence, token stats, cost estimation, and web dashboard.
  触发词："使用统计"、"usage stats"、"工具统计"、"tool stats"、"用了什么"、"skill 排行"、"agent 统计"。
metadata:
  distribution:
    channel: all
    standalone: true
  dependencies:
    cli: []
    python: []
    skills: []
---

# AI Usage Stats

统计 skill / agent / tool 三类事件的使用情况，跨所有 AI agent runtime。

## Overview

**核心原则**：
1. **零依赖** — 100% Python 标准库（含 sqlite3），无需 pip/npm
2. **本地优先** — 所有数据存储在 `~/.praxis-ai-usage-stats/`，不上传云端
3. **自动捕获** — PostToolUse hook 自动记录，无需手动操作

## When to Use

- 查看 AI agent 的使用统计（"用了什么工具"、"skill 排行"）
- 追踪 Token 消耗和成本估算
- 分析跨 runtime（Claude Code / Codex / OpenHuman）的使用趋势
- 生成使用报告或 Web 仪表盘

## When NOT to Use

- **创建新 skill** — 这是统计工具，不用于创建 skill
- **调试 skill** — use `superpowers:systematic-debugging`
- **实时监控单次调用** — 这是聚合统计工具，不是 tracing 工具

## 🚀 Quick Start

```bash
# 1. 安装（跨平台，自动配置 hook 和软连接）
python3 scripts/install.py

# 2. 检查依赖状态
python3 scripts/install.py --check

# 3. 查看今天的统计
python3 scripts/usage_stats.py today

# 4. 生成 Web 仪表盘
python3 scripts/usage_stats.py --web
```

## Quick Reference

| 命令 | 用途 | 示例 |
|------|------|------|
| `usage_stats.py today` | 今日统计 | `python3 scripts/usage_stats.py today` |
| `usage_stats.py week` | 最近 7 天（默认） | `python3 scripts/usage_stats.py` |
| `usage_stats.py month` | 最近 30 天 | `python3 scripts/usage_stats.py month` |
| `usage_stats.py --all-time` | 全部历史 | `python3 scripts/usage_stats.py --all-time` |
| `usage_stats.py --web` | Web 仪表盘 | `python3 scripts/usage_stats.py --web --port 9090` |
| `usage_stats.py --migrate` | 迁移旧日志到 SQLite | `python3 scripts/usage_stats.py --migrate` |
| `usage_stats.py --cleanup` | 清理旧记录 | `python3 scripts/usage_stats.py --cleanup --cleanup-days 30` |
| `generate_report.py` | HTML 报告 | `python3 scripts/generate_report.py --open` |
| `log_usage.py` | 手动记录 | `python3 scripts/log_usage.py --kind skill --name xxx` |
| `install.py --check` | 检查安装状态 | `python3 scripts/install.py --check` |

> **详细用法和过滤选项**: [usage-examples.md](references/usage-examples.md)

## 数据源

| Runtime | 数据源路径 |
|---------|-----------|
| Claude Code | `~/.claude/tool-usage.log`（hook 自动记录） |
| Claude Code | `~/.claude/projects/**/*.jsonl`（会话 tool_use） |
| Codex | `~/.codex/skill-usage.log`、`tool-usage.log` |
| OpenHuman | `~/.openhuman/users/*/workspace/session_raw/*.jsonl` |

## Hook 工作原理

安装 hook 后，Claude Code 每次工具调用自动触发：

```
工具调用 → PostToolUse hook → hook_collect.py → SQLite 数据库
```

捕获信息：工具名称、调用时间、Runtime、项目、模型、Token 使用、成本、会话 ID。

## 配置

### 模型费率

在 `scripts/hook_collect.py` 中配置：

```python
MODEL_RATES = {
    "claude-3-5-sonnet": {"input": 3.0, "output": 15.0, "cache_read": 0.3},
    "claude-3-opus": {"input": 15.0, "output": 75.0, "cache_read": 1.5},
    "gpt-4": {"input": 30.0, "output": 60.0, "cache_read": 0.0},
}
```

### 数据库路径

默认: `~/.praxis-ai-usage-stats/usage.db`。可在 `scripts/db.py` 中修改。

## 隐私与安全

- ✅ 本地存储，不上传云端
- ✅ 只读扫描日志，不修改原始文件
- ✅ Context 截断到 200 字符

## 故障排除

**Hook 不工作**:
```bash
python3 scripts/hook_install.py status    # 检查状态
python3 scripts/hook_install.py uninstall  # 卸载
python3 scripts/hook_install.py install    # 重装
```

**数据库问题**:
```bash
ls -la ~/.praxis-ai-usage-stats/          # 检查文件
rm ~/.praxis-ai-usage-stats/usage.db      # 删除旧库
python3 scripts/usage_stats.py --migrate  # 重新初始化
```

**权限问题**:
```bash
chmod +x scripts/hook_collect.py
```

## 目录结构

```
praxis-ai-usage-stats/
├── SKILL.md
├── scripts/
│   ├── usage_stats.py         # 主入口
│   ├── db.py                  # SQLite 管理
│   ├── hook_collect.py        # PostToolUse hook 脚本
│   ├── hook_install.py        # hook 安装/卸载
│   ├── parsers.py             # JSONL 解析器
│   ├── outcome.py             # 成功/失败判断
│   ├── generate_report.py     # HTML 报告生成
│   ├── install.py             # 跨平台安装脚本
│   ├── check_dependencies.py  # 依赖检查
│   ├── log_usage.py           # 手动记录
│   └── auto_cleanup.py        # 自动清理
├── web/
│   ├── index.html             # Web 仪表盘
│   └── app.js                 # 前端逻辑
└── references/
    ├── usage-examples.md      # 详细用法示例
    ├── design-principles.md   # 设计原则
    └── install-guide.md       # 安装指南
```

## Gotchas

- **首次使用需要安装 hook**: 运行 `python3 scripts/install.py` 后才会自动捕获。之前的调用不会被记录。
- **SQLite 是 Python 内置**: 不需要 `pip install`，但需要 Python 3.10+。
- **Web 仪表盘用内置 http.server**: 不需要额外依赖，但端口可能被占用。
- **hook_collect.py 必须有执行权限**: `chmod +x scripts/hook_collect.py`。
- **迁移旧数据**: 升级到 SQLite 后运行 `--migrate` 导入旧日志。
- **清理策略**: 默认保留 90 天数据，`--cleanup-days` 可调整。

## Common Mistakes

| 错误 | 修复 |
|------|------|
| 安装后看不到数据 | 确认 hook 已安装: `python3 scripts/hook_install.py status` |
| "数据库锁定" 错误 | 关闭其他使用同一数据库的进程 |
| Web 仪表盘空白 | 确认有数据: `python3 scripts/usage_stats.py today` |
| Token 统计为 0 | hook 需要在工具调用时触发，手动记录不含 token |
| 跨平台安装失败 | 使用 `python3 scripts/install.py`（不要用 install.sh） |
