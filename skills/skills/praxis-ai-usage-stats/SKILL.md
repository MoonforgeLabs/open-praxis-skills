---
name: praxis-ai-usage-stats
description: >
  统计所有 AI agent runtime（Claude Code、Codex、OpenHuman 等）
  的 skill/agent/tool 使用情况。支持实时捕获、SQLite 持久化、
  Token 统计、成本估算、成功/失败判断、Web 仪表盘。
  触发词："使用统计"、"usage stats"、"工具统计"、"tool stats"、
  "用了什么"、"skill 排行"、"agent 统计"、"AI usage"。
version: 1.0.0
---

# AI Usage Stats

统计 skill / agent / tool 三类事件的使用情况，跨所有 AI agent runtime。

## ✨ 功能特性

### 核心功能
- ✅ **实时捕获**: PostToolUse hook 自动捕获 Claude Code 调用
- ✅ **SQLite 持久化**: 数据存储在本地数据库，支持快速查询
- ✅ **多 Runtime 支持**: Claude Code、Codex、OpenHuman
- ✅ **Token 统计**: input/output/cache token 详细统计
- ✅ **成本估算**: 根据模型费率自动计算成本
- ✅ **成功/失败判断**: 启发式推断 skill 执行结果
- ✅ **健康评分**: 综合评估使用健康度

### 输出格式
- 📊 **Markdown 报告**: 终端友好的格式化输出
- 📈 **Web 仪表盘**: 交互式图表和实时数据
- 📁 **JSON 导出**: 便于程序化处理

### 分析维度
- 按类型 (skill/agent/tool)
- 按 Runtime (claude/codex/openhuman)
- 按模型 (claude-3-5-sonnet, gpt-4, etc.)
- 按项目
- 按时间趋势
- Top 排行榜

## 📦 数据源

| Runtime | 数据源路径 |
|---------|-----------|
| Claude Code | `~/.claude/tool-usage.log`（hook 自动记录） |
| Claude Code | `~/.claude/skill-usage.log`（历史 skill 日志） |
| Claude Code | `~/.claude/projects/**/*.jsonl`（会话 tool_use） |
| Codex | `~/.codex/skill-usage.log`、`agent-usage.log`、`tool-usage.log` |
| Codex | `~/.codex/sessions/**/*.jsonl`、`archived_sessions/**/*.jsonl` |
| OpenHuman | `~/.openhuman/users/*/workspace/session_raw/*.jsonl` |
| OpenHuman | `~/.openhuman/users/*/workspace/state/skill-usage.log` |

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/MoonforgeLabs/praxis-skills.git
cd praxis-skills/skills/praxis-ai-usage-stats
```

### 2. 安装（跨平台）

**macOS / Linux:**
```bash
python3 scripts/install.py
```

**Windows:**
```powershell
python scripts/install.py
```

**安装脚本会自动：**
- ✅ 创建软连接到 Claude Code、Codex、OpenHuman
- ✅ 配置 PostToolUse hook
- ✅ 设置脚本执行权限

### 3. 检查依赖状态

```bash
python3 scripts/install.py --check
```

输出示例：
```
============================================================
📊 praxis-ai-usage-stats 依赖检查报告
============================================================

【软连接】
  ✅ Claude
  ✅ Codex
  ✅ Openhuman

【Hook 配置】
  ✅ Claude Code
  ✅ Codex
  ➖ OpenHuman (不需要)

【数据存储】
  ✅ 数据库

总结: ✅ 6/6 正常
============================================================
```

### 4. 迁移旧数据（可选）

```bash
# 从旧日志迁移到 SQLite
python3 scripts/usage_stats.py --migrate
```

### 5. 开始使用

```bash
# 查看今天的统计
python3 scripts/usage_stats.py today

# 查看最近 7 天（默认）
python3 scripts/usage_stats.py

# 查看全部历史
python3 scripts/usage_stats.py --all-time

# 生成交互式 HTML 报告
python3 scripts/generate_report.py --open
```

## 📖 详细用法

### 安装选项

```bash
# 安装到所有 runtime（默认）
python3 scripts/install.py

# 只安装到 Claude Code
python3 scripts/install.py --claude

# 只安装到 Codex
python3 scripts/install.py --codex

# 只安装到 OpenHuman
python3 scripts/install.py --openhuman

# 检查依赖状态
python3 scripts/install.py --check
```

### 时间范围

```bash
python3 scripts/usage_stats.py today      # 今天
python3 scripts/usage_stats.py week       # 最近 7 天（默认）
python3 scripts/usage_stats.py month      # 最近 30 天
python3 scripts/usage_stats.py --days 14  # 最近 14 天
python3 scripts/usage_stats.py --all-time # 全部历史
```

## 📖 详细用法

### 时间范围

```bash
python3 scripts/usage_stats.py today      # 今天
python3 scripts/usage_stats.py week       # 最近 7 天（默认）
python3 scripts/usage_stats.py month      # 最近 30 天
python3 scripts/usage_stats.py --days 14  # 最近 14 天
python3 scripts/usage_stats.py --all-time # 全部历史
```

### 过滤选项

```bash
# 按 Runtime 过滤
python3 scripts/usage_stats.py --runtime claude
python3 scripts/usage_stats.py --runtime codex
python3 scripts/usage_stats.py --runtime openhuman

# 按类型过滤
python3 scripts/usage_stats.py --kind skill
python3 scripts/usage_stats.py --kind agent
python3 scripts/usage_stats.py --kind tool

# 按项目过滤
python3 scripts/usage_stats.py --project myCode

# 按名称过滤
python3 scripts/usage_stats.py --name praxis-translate

# 组合过滤
python3 scripts/usage_stats.py --runtime claude --kind skill --days 7
```

### 输出控制

```bash
# JSON 输出
python3 scripts/usage_stats.py --format json
python3 scripts/usage_stats.py --json

# 保存报告到文件
python3 scripts/usage_stats.py --save
python3 scripts/usage_stats.py --save --output-dir ./reports

# 自定义排行榜条数
python3 scripts/usage_stats.py --limit 20
```

### Web 仪表盘

```bash
# 启动 Web 仪表盘（默认端口 8080）
python3 scripts/usage_stats.py --web

# 自定义端口
python3 scripts/usage_stats.py --web --port 9090
```

访问 http://localhost:8080 查看交互式仪表盘。

### 数据库管理

```bash
# 迁移旧日志
python3 scripts/usage_stats.py --migrate

# 清理旧记录（默认 90 天）
python3 scripts/usage_stats.py --cleanup
python3 scripts/usage_stats.py --cleanup --cleanup-days 30
```

## 🎯 Hook 工作原理

安装 hook 后，Claude Code 会在每次工具调用后自动执行 hook 脚本：

```
Claude Code 调用工具
  → PostToolUse hook 触发
    → hook_collect.py 捕获调用信息
      → 存储到 SQLite 数据库
        → 你可以随时查看统计
```

### Hook 捕获的信息

- **工具名称**: Skill、Agent、Tool 的具体名称
- **调用时间**: ISO 8601 格式的时间戳
- **Runtime**: claude/codex/openhuman
- **项目**: 当前工作目录
- **模型**: 使用的 AI 模型
- **Token 使用**: input/output/cache token 数量
- **成本**: 根据模型费率计算的成本
- **会话 ID**: 用于关联同一会话的调用

## 📊 报告内容

### 总体统计
- 总事件数
- 总 Token 使用量
- 总成本估算
- 唯一会话数
- 唯一项目数

### 健康评分（0-100）
- **成功率评分**（0-40）: 基于成功/失败比例
- **使用频率评分**（0-30）: 基于日均使用次数
- **多样性评分**（0-30）: 基于使用的 Runtime 数量

### 分类统计
- 按类型 (skill/agent/tool)
- 按 Runtime
- 按模型
- 按项目

### 排行榜
- Top Skills
- Top Agents
- Top Tools

### 趋势分析
- 每日使用趋势
- 周对比

### 成功率
- ✅ 成功 (likely_solved)
- ❌ 失败 (likely_failed)
- ❓ 未知 (unknown)

## 🔧 配置

### 模型费率

在 `scripts/hook_collect.py` 中配置模型费率：

```python
MODEL_RATES = {
    "claude-3-5-sonnet": {"input": 3.0, "output": 15.0, "cache_read": 0.3},
    "claude-3-opus": {"input": 15.0, "output": 75.0, "cache_read": 1.5},
    "gpt-4": {"input": 30.0, "output": 60.0, "cache_read": 0.0},
    # ... 更多模型
}
```

### 数据库路径

默认数据库路径: `~/.praxis-ai-usage-stats/usage.db`

可以在 `scripts/db.py` 中修改：

```python
DB_PATH = Path.home() / ".praxis-ai-usage-stats" / "usage.db"
```

## 📁 目录结构

```
praxis-ai-usage-stats/
├── SKILL.md                    # 本文档
├── scripts/
│   ├── usage_stats.py         # 主入口
│   ├── db.py                  # SQLite 数据库管理
│   ├── hook_collect.py        # PostToolUse hook 脚本
│   ├── hook_install.py        # hook 安装/卸载
│   ├── parsers.py             # JSONL 解析器
│   ├── outcome.py             # 成功/失败判断
│   └── log_usage.py           # 手动记录
├── web/
│   ├── index.html             # Web 仪表盘
│   └── app.js                 # 前端逻辑
└── references/
    ├── design-principles.md   # 设计原则
    └── install-guide.md       # 安装指南
```

## 🛠️ 手动记录

对于不支持 hook 的 runtime，可以手动记录：

```bash
# 记录 skill 调用
python3 scripts/log_usage.py --kind skill --name <name> --context "简短描述"

# 记录 agent 调用
python3 scripts/log_usage.py --kind agent --name <name> --context "简短描述"

# 记录 tool 调用
python3 scripts/log_usage.py --kind tool --name <name> --context "简短描述"
```

## 🎨 Web 仪表盘功能

Web 仪表盘提供以下功能：

- 📊 **实时统计卡片**: 总事件数、Token、成本、成功率、健康评分
- 📈 **使用趋势图**: 每日事件数和 Token 使用趋势
- 🍩 **分布图表**: 类型、Runtime、模型、项目分布
- 🏆 **排行榜**: Top Skills、Top Tools
- 📋 **事件列表**: 最近 50 条事件详情
- 🔄 **自动刷新**: 每 5 分钟自动更新数据
- 📱 **响应式设计**: 支持移动端访问

## 🔒 隐私与安全

- ✅ **本地存储**: 所有数据存储在本地 `~/.praxis-ai-usage-stats/`
- ✅ **只读访问**: 只扫描日志，不修改原始文件
- ✅ **无网络传输**: 不上传任何数据到云端
- ✅ **Token 脱敏**: 不记录 API token 原文
- ✅ **Context 截断**: 用户消息截断到 200 字符

## 🆚 对比其他工具

| 功能 | praxis-ai-usage-stats | skill-tracker | claude-skills-usage |
|------|---------------------|---------------|---------------------|
| 实时捕获 | ✅ | ✅ | ✅ |
| SQLite 存储 | ✅ | ✅ | ✅ |
| Token 统计 | ✅ | ❌ | ✅ |
| 成本估算 | ✅ | ❌ | ✅ |
| 延迟统计 | ❌ | ❌ | ✅ |
| 成功/失败判断 | ✅ | ❌ | ✅ |
| Web 仪表盘 | ✅ | ✅ | ❌ |
| 多 Runtime | ✅ | ❌ | ❌ |
| 健康评分 | ✅ | ❌ | ❌ |
| 自动清理 | ✅ | ✅ | ❌ |

## 🐛 故障排除

### Hook 不工作

```bash
# 检查 hook 状态
python3 scripts/hook_install.py status

# 重新安装 hook
python3 scripts/hook_install.py uninstall
python3 scripts/hook_install.py install
```

### 数据库问题

```bash
# 检查数据库文件
ls -la ~/.praxis-ai-usage-stats/

# 重新初始化数据库
rm ~/.praxis-ai-usage-stats/usage.db
python3 scripts/usage_stats.py --migrate
```

### 权限问题

```bash
# 确保 hook 脚本有执行权限
chmod +x scripts/hook_collect.py
```

## 🏷️ 能力层级

```bash
python3 scripts/usage_stats.py --tiers   # 查看层级
```

| 层级 | 命令数 | 依赖 | 开源策略 |
|------|--------|------|---------|
| **CORE** | 9/9 | Python 标准库，零外部依赖 | 全部保留 |

本 skill 100% 使用 Python 标准库（含 sqlite3），无 pip/npm/系统工具依赖。
开源裁剪：无需裁剪，直接 ship。

## 📝 更新日志

### v1.0.0 (2026-06-25)
- ✨ 新增 PostToolUse hook 实时捕获
- ✨ 新增 SQLite 持久化存储
- ✨ 新增 Token 统计和成本估算
- ✨ 新增成功/失败启发式判断
- ✨ 新增健康评分
- ✨ 新增 Web 仪表盘
- ✨ 新增多 Runtime 统一视图
- ✨ 新增自动清理机制
- 🔄 重构代码结构
- 📚 完善文档

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
