---
name: praxis-knowledge-radar
description: >
  个人知识线索追踪器：文章/链接输入 → 归类入库 → 状态流转 → 同步检查。
  支持手动输入、外部消息自动订阅（可选）、URL 自动抓取。
  触发词："记录这个"、"加入雷达"、"reading list"、"学习队列"、"还有哪些没学"、
  "学习雷达"。
---

## When to Use

- 用户想记录文章/链接到学习队列
- 用户想查看待学习列表或学习进度
- 用户想从外部消息源（如钉钉、Slack 等）自动订阅内容
- 用户说"记录这个"、"加入雷达"、"reading list"

## Quick Reference

```bash
# 添加条目
python3 scripts/radar.py add --title "标题" --area "ai-os" --source manual --references "https://..."

# 查看状态
python3 scripts/radar_enhanced.py status

# 列出待处理
python3 scripts/radar.py list --status inbox,next

# 更新状态
python3 scripts/radar.py update --id <id> --status learning
```

# Reading Radar

> **快速开始**: 新用户请查看 [QUICKSTART.md](QUICKSTART.md)

## 📑 文档导航

| 文档 | 用途 | 适合人群 |
|------|------|---------|
| **[QUICKSTART.md](QUICKSTART.md)** | 5 分钟快速上手 | 新手 |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | 架构和功能分层 | 所有用户 |
| **[SETUP.md](SETUP.md)** | 详细配置指南 | 需要配置的用户 |
| **SKILL.md** | 完整功能参考 | 进阶用户 |

---

## 🚀 快速开始（30 秒）

```bash
# 1. 查看状态
python3 scripts/radar_enhanced.py status

# 2. 添加一个想法
python3 scripts/radar.py add --title "学习主题" --area "ai-os" --source manual

# 3. 开始学习
python3 scripts/radar.py update --id <id> --status learning
```

**完整指南**: [QUICKSTART.md](QUICKSTART.md) | **架构说明**: [ARCHITECTURE.md](ARCHITECTURE.md)

---

个人知识线索追踪器：从日常阅读中捕获有价值的内容，归类存储，追踪状态。

```
输入（文章/链接/外部消息）
    ↓  自动抓取标题/摘要
归类（area + tags）
    ↓  JSONL 存储
状态流转（inbox → next → active → done）
```

## Storage

Default local store:

- `PRAXIS_KNOWLEDGE_RADAR_STORE`, if set.
- Otherwise `~/.praxis-skills/data/knowledge-radar/tasks.jsonl`.

Use `scripts/radar.py` for append/list/update/export operations. Prefer JSONL over ad hoc Markdown so the radar can later sync into external systems.

## Core Workflow

1. Capture the raw user idea without over-normalizing it.
2. Assign a short title, source, status, priority, area, and tags.
3. Preserve evidence links, quoted snippets, and reference projects when provided.
4. Convert vague ideas into a next action only when the user asks for planning or triage.
5. Keep completed items in the store with `status=done`; never delete history unless the user asks.
6. When asked "还有哪些问题" or "已经做了哪些问题", summarize by status, area, and mainline.

## Status Model

Use these statuses:

- `inbox`: captured but not triaged.
- `next`: actionable soon.
- `active`: currently being worked.
- `learning`: 正在学习中，已有学习笔记。
- `learned`: 学习完成，等待应用。
- `applied`: 已应用到具体项目/skill。
- `waiting`: blocked by external input or scheduled monitoring.
- `done`: completed or intentionally closed.
- `archived`: retained for history but no longer active.

Use priorities `P0`, `P1`, `P2`, or `P3`. Default to `P2` unless the user indicates urgency.

## Capture Modes

### Manual Input

When the user says "记录这个 URL", "加入雷达", "reading list":

```bash
python3 scripts/radar.py add --title "文章标题" --area "ai-os" --source manual --references "https://..." --status inbox
```

### 可选：外部消息源订阅（如钉钉、Slack 等）

<!-- 可选通知插件 - 钉钉是区域特定功能，非核心依赖 -->

从外部消息源（如钉钉、Slack 等）中自动提取 URL 并入库：

```bash
# 1. 配置钉钉（首次）
python3 scripts/setup_dingtalk.py

# 2. 拉取最近 24 小时的消息
python3 scripts/dingtalk_fetch.py

# 3. 只拉取最近 2 小时
python3 scripts/dingtalk_fetch.py --since 2h

# 4. dry-run（只提取不入库）
python3 scripts/dingtalk_fetch.py --dry-run
```

配置文件：`~/.praxis-skills/data/knowledge-radar/dingtalk-config.json`

### URL 自动抓取

直接给 URL，自动提取标题/摘要/归类：

```bash
python3 scripts/radar.py add --source url --references "https://..." --status inbox
```

## 状态流转

```bash
# 开始学习
python3 scripts/radar.py update --id <id> --status learning

# 学完了
python3 scripts/radar.py update --id <id> --status learned --notes "关键点..."

# 已应用
python3 scripts/radar.py update --id <id> --status applied --notes "用到了哪里"
```

## 查询

```bash
python3 scripts/radar.py list --status inbox,next      # 待处理
python3 scripts/radar.py list --status learning          # 学习中
python3 scripts/radar.py list --status learned           # 学完待用
python3 scripts/radar.py list --status applied           # 已应用
```

## 种子数据

```bash
python3 scripts/radar.py seed-mainlines
```

## Monitored Inputs

For Feishu, WeChat, Toutiao, GitHub, YouTube, news, or other sources:

1. Only ingest sources the user has authorized and that tools can access.
2. Record the input source and source URL/message ID when available.
3. Classify each candidate as `task`, `reference`, `question`, or `watch` in tags.
4. Add tasks as `inbox` unless the user explicitly asks to promote them.
5. Keep private content out of public skill files; only store it in the local task store.

Use Feishu MCP/search tools when available for Feishu documents and comments. For WeChat/Toutiao or other apps, use available local/export tools; if no connector exists, tell the user what export format is needed.

## Review Workflow

When asked what remains:

```bash
python3 scripts/radar.py list --status inbox,next,active,waiting
```

When asked what is done:

```bash
python3 scripts/radar.py list --status done --limit 50
```

Return:

- `Active / Next`: the most important open tasks.
- `Waiting`: blocked or monitoring-dependent items.
- `Done`: recently closed items.
- `Suggested next action`: one concrete action per top item.

## Mainline Areas

Use these initial areas unless a better area is obvious:

- `code-understanding`: CodeGraph + Understand-Anything workflow.
- `patent-skills`: patent-writing skill refactor.
- `rag-docs`: RAG and document-processing skills.
- `search-skills`: search-hub and research skill refactor.
- `skill-creation`: skill creation, curation, and official-skill alignment.
- `daily-news`: GitHub/news/video/watchtower reporting.
- `ai-os`: AI OS and agent systems.
- `knowledge-base`: personal knowledge base and architecture references.
- `skill-ecosystem`: useful external skill ecosystems.
- `business-skills`: short-video, Xiaohongshu, UI automation, and business workflows.
- `stocks`: trading/investment workflows.
- `design-tools`: AI design tool ecosystem integration.
- `digital-human`: digital human and virtual avatar workflows.
- `content-distribution`: multi-platform content distribution workflows.

The seed list lives in `references/initial-mainlines.json` and is mirrored for humans in `references/initial-mainlines.md`.

## Downstream Integration

This skill can serve as an intake layer for external systems:

- Keep local JSONL schema stable for downstream consumers.
- Export Markdown summaries with `scripts/radar.py export-md` when needed.
- Use environment variables for external system paths; do not hardcode.
- Separate personal/private task evidence from reusable skill logic.

## Mapping Import

To import records from `knowledge-radar-mapping.md` (chat history mapping):

```bash
python3 scripts/import-mapping.py
```

This imports 93 records from the mapping file (2026-03-18 ~ 2026-06-26) into the local task store. Records are added as `inbox` status with `reference` and `mapping` tags.

After import, review and triage:

```bash
python3 scripts/radar.py list --status inbox --area code-understanding
python3 scripts/radar.py list --status inbox --area skill-creation
```

## Enhanced Query System

Use `scripts/radar_enhanced.py` for advanced mainline task management:

```bash
python3 scripts/radar_enhanced.py status              # All mainline status
python3 scripts/radar_enhanced.py status <area>       # Specific mainline details
python3 scripts/radar_enhanced.py next                # Next actions (all)
python3 scripts/radar_enhanced.py next <area>         # Next actions (specific)
python3 scripts/radar_enhanced.py refs <area>         # Historical references
python3 scripts/radar_enhanced.py deps                # Dependencies (all)
python3 scripts/radar_enhanced.py deps <area>         # Dependencies (specific)
python3 scripts/radar_enhanced.py competitors         # Competitors (all)
python3 scripts/radar_enhanced.py competitors <area>  # Competitors (specific)
python3 scripts/radar_enhanced.py summary             # Summary report
```

Shows:
- Total task count and mainline count
- Priority distribution
- Status distribution
- P0 priority tasks
- All pending next actions

## 能力同步（Capability Sync）

当参考的 skill 或项目有更新时，自动检查并同步新能力。

### 检查单个任务

```bash
python3 scripts/radar_enhanced.py sync <area>
```

Example:
```bash
python3 scripts/radar_enhanced.py sync skill-creation
```

功能：
- 检查 GitHub 仓库的最新状态（stars、最后更新、最近提交）
- 检查本地 skill 的文件变化
- 对比已记录的 `reference_state`，发现新能力
- 生成同步报告和建议

### 批量同步所有 learned 任务

```bash
python3 scripts/radar_enhanced.py sync-all
```

自动检查所有 `status=learned` 的主线任务，批量生成同步报告。

### 批量同步 + 通知

<!-- 可选通知插件 - 钉钉通知是区域特定功能，非核心依赖 -->

```bash
python3 scripts/radar_enhanced.py sync-all --notify
```

同步完成后自动发送通知消息（需配置通知插件，如钉钉等）。

### Reference State 结构

在 `tasks.jsonl` 中，`reference_state` 字段记录每个参考来源的状态：

```json
{
  "reference_state": {
    "praxis-skill-forge": {
      "last_checked": "2026-06-27",
      "version": "1.0",
      "capabilities": ["validate", "package", "install", "eval", "description-improve"]
    },
    "anthropics/skills": {
      "last_checked": "2026-06-27",
      "stars": 155646,
      "last_updated": "2026-06-27T06:09:11Z",
      "capabilities": ["create", "validate", "package"]
    }
  }
}
```

### 定期扫描

#### 设置 Cron Job

```bash
# 交互式设置（推荐）
bash scripts/setup_cron.sh

# 或手动添加（每周一早上 9 点）
0 9 * * 1 /path/to/scheduled_sync.sh
```

#### 手动运行

```bash
bash scripts/scheduled_sync.sh
```

日志位置：`~/.praxis-skills/data/knowledge-radar/logs/sync-*.log`

### 钉钉通知配置（可选）

<!-- 可选通知插件 - 钉钉是区域特定功能，非核心依赖。其他用户可自行实现类似插件。 -->

#### 首次配置

```bash
python3 scripts/dingtalk_notify.py setup
```

按提示输入：
- Webhook URL（从钉钉群机器人获取）
- Secret（可选，加签模式）

#### 测试配置

```bash
python3 scripts/dingtalk_notify.py test
```

#### 手动发送消息

```bash
python3 scripts/dingtalk_notify.py send --title "标题" --content "内容"
```

### 关注点

- GitHub 仓库的最近 commits（新功能、bug 修复）
- Stars 增长（项目热度）
- 本地 skill 的文件变化（手动更新）

## 知识运维

### 间隔重复（Spaced Repetition）

学完一个知识点后，自动安排复习计划（FSRS-6 算法）：

```
学完 → 第 1 天 → 第 3 天 → 第 7 天 → 第 14 天 → 第 30 天 → 第 90 天
```

```bash
# 查看今日复习任务
python3 scripts/knowledge_ops.py review

# 标记复习完成（自动安排下次）
python3 scripts/knowledge_ops.py review --do
```

### 知识 Lint

定期检查知识库质量：

```bash
python3 scripts/knowledge_ops.py lint           # 检查
python3 scripts/knowledge_ops.py lint --fix     # 自动修复
```

检查项：
- 🔴 重复条目（同 URL 不同时间入库）
- 🟡 过期条目（inbox 超过 30 天未处理）
- 🟡 不完整条目（learned 但没学习笔记）
- 🔵 孤儿条目（learned 超过 14 天但没 applied）
- 🟡 未分类条目（没有 area）

### 内容质量分级

```bash
python3 scripts/knowledge_ops.py grade
```

| 等级 | 来源 | 优先级 |
|------|------|--------|
| A | 官方文档、学术论文 | 最高 |
| B | 高星 GitHub、知名博客 | 高 |
| C | 社区内容（Reddit、推特） | 中 |
| D | 其他 | 低 |

### 其他运维命令

```bash
python3 scripts/knowledge_ops.py dedup      # 检查重复条目
python3 scripts/knowledge_ops.py progress   # 学习进度
python3 scripts/knowledge_ops.py triage     # Inbox 分拣
```

## 存储

| 环境变量 | 默认值 | 用途 |
|---------|--------|------|
| `PRAXIS_KNOWLEDGE_RADAR_STORE` | `~/.praxis-skills/data/knowledge-radar/tasks.jsonl` | 知识条目存储 |

> **定位**: Radar 只做线索追踪（捕获 → 状态流转 → 查询），不存储学习笔记。深度知识管理留给未来的底层知识库。
