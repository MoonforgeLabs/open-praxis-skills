---
name: open-praxis-knowledge-radar
description: >
  Use when用户想把文章/链接加入学习队列、查看待学习列表、追踪学习进度，或从钉钉自动订阅内容。触发词："记录这个"、"加入雷达"、"reading list"、"学习队列"、"还有哪些没学"。
---

# Alex Reading Radar

个人知识吸收管线：从日常阅读中捕获有价值的内容，归类存储，等待学习内化，最终应用到 praxis-skills / moonforge 等项目。

```
输入（文章/链接/钉钉消息）
    ↓  自动抓取标题/摘要
归类（area + tags）
    ↓  JSONL 存储
学习（inbox → learning → learned）
    ↓  学习笔记
输出（applied_to → 优化 skill/项目）
```

## Storage

Default local store:

- `PRAXIS_KNOWLEDGE_RADAR_STORE`, if set.
- Otherwise `~/.praxis-skills/data/knowledge-radar/tasks.jsonl`.

Use `scripts/radar.py` for append/list/update/export operations.

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

### DingTalk 自动订阅

从钉钉群消息中自动提取 URL 并入库：

```bash
# 1. 配置钉钉（首次）
python3 scripts/setup_dingtalk.py

# 2. 增量拉取（推荐，从上次拉取位置继续）
python3 scripts/dingtalk_fetch.py --incremental

# 3. 指定时间范围拉取
python3 scripts/dingtalk_fetch.py --since 2h

# 4. dry-run（只提取不入库）
python3 scripts/dingtalk_fetch.py --dry-run
```

**增量模式**：记录上次拉取时间，下次从该时间点继续拉取，确保不遗漏消息。

**去重机制**：基于 URL 去重，已入库的 URL 不会重复入库。

**摘要提取**：自动从消息内容中提取标题和摘要。

配置文件：`~/.praxis-skills/data/knowledge-radar/dingtalk-config.json`
状态文件：`~/.praxis-skills/data/knowledge-radar/fetch_state.json`

详见 `references/dingtalk-integration.md`。

### 自动捕获（Cron Job）

设置定时自动捕获钉钉群消息：

```bash
# 设置 cron job（推荐每 30 分钟）
bash scripts/setup_auto_capture.sh

# 手动触发自动捕获
bash scripts/auto_capture.sh

# 带钉钉通知
bash scripts/auto_capture.sh --notify
```

自动捕获功能：
- 每 30 分钟自动检查钉钉群消息
- 增量拉取，不遗漏消息
- 基于 URL 去重
- 自动提取标题和摘要
- 自动清理超过 7 天的报告和 30 天的日志

详见 `references/auto-capture.md`。

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

## 报告生成

```bash
# 生成 HTML 报告（带样式）
python3 scripts/generate_report_v2.py --format html --open

# 生成 Markdown 报告
python3 scripts/generate_report_v2.py --format md
```

报告包含：
- 统计概览（状态/领域/优先级/来源分布）
- 最近入库的 URL（带摘要表格）
- 任务列表（按状态分组）
- 待学习队列

详见 `references/report-generation.md`。

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
- `ai-os`: Moonforge and personal AI OS.
- `knowledge-base`: personal knowledge base and architecture references.
- `skill-ecosystem`: useful external skill ecosystems.
- `business-skills`: short-video, Xiaohongshu, UI automation, and business workflows.
- `stocks`: trading/investment workflows.
- `design-tools`: AI design tool ecosystem integration.
- `digital-human`: digital human and virtual avatar workflows.
- `content-distribution`: multi-platform content distribution workflows.

The seed list lives in `references/initial-mainlines.json` and is mirrored for humans in `references/initial-mainlines.md`.

## Moonforge Integration

Treat this skill as the personal intake layer for a future Moonforge radar station:

- Keep local JSONL schema stable.
- Export Markdown summaries with `scripts/radar.py export-md` when the user wants a report.
- Do not assume Moonforge paths; ask or use environment variables when syncing is requested.
- Separate personal/private task evidence from reusable public skill logic.

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
python3 scripts/radar_enhanced.py status                    # 查看所有主线任务状态
python3 scripts/radar_enhanced.py status <area>             # 查看指定主线状态
python3 scripts/radar_enhanced.py next                      # 查看所有主线的下一步行动
python3 scripts/radar_enhanced.py next <area>               # 查看指定主线的下一步
python3 scripts/radar_enhanced.py refs <area>               # 查看指定主线的参考资料
python3 scripts/radar_enhanced.py deps <area>               # 查看指定主线的依赖
python3 scripts/radar_enhanced.py competitors <area>        # 查看指定主线的竞品
python3 scripts/radar_enhanced.py summary                   # 生成主线任务总结报告
python3 scripts/radar_enhanced.py sync <area>               # 同步检查 reference 的最新状态
python3 scripts/radar_enhanced.py sync-all                  # 批量同步所有 learned 任务
```

详见 `references/enhanced-query.md`。

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

### Dedup 检查

```bash
python3 scripts/knowledge_ops.py dedup
```

检查重复条目（同 URL 或同标题）。

### 学习进度

```bash
python3 scripts/knowledge_ops.py progress
```

按 area 显示学习完成度。

### Inbox 分拣

```bash
python3 scripts/knowledge_ops.py triage
```

显示 inbox 中待分拣的条目。

详见 `references/knowledge-ops.md`。

## 存储清理

```bash
# 干运行（查看会清理什么）
bash scripts/cleanup.sh --dry-run

# 实际清理
bash scripts/cleanup.sh
```

清理策略：
- 报告文件：保留 7 天
- 日志文件：保留 30 天
- 报告目录：最大 10MB
- 日志目录：最大 5MB

详见 `references/report-generation.md`。

## References

- `references/dingtalk-integration.md` - 钉钉集成详解
- `references/auto-capture.md` - 自动捕获详解
- `references/report-generation.md` - 报告生成详解
- `references/knowledge-ops.md` - 知识运维详解
- `references/enhanced-query.md` - 增强查询详解
- `references/initial-mainlines.json` - 初始主线任务数据
- `references/initial-mainlines.md` - 初始主线任务说明
