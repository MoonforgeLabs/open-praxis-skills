---
name: open-praxis-search-hub
description: |
  Alex 的安全搜索网关。用于统一执行网页搜索、GitHub 仓库搜索、GitHub 代码搜索、B站/小红书/今日头条/雪球等渠道搜索，集中处理风控、限流、审计和降级。
  当用户提到“搜索网关”“安全搜索”“GitHub 搜索风控”“统一搜索入口”“日报搜索降风险”“避免 GitHub 封号”时使用。
  默认 GitHub 搜索处于 safe mode，需要显式解除风控后才恢复。
---

# Alex Safe Search

统一搜索入口，目标是把搜索能力从零散脚本里收拢到一个可审计、可限流、可降级的网关。

## Public / Private Boundary

Use `<WORKSPACE>/praxis-local-configs/docs/moonforge-public-private-boundary.md` for search result routing. The search gateway design is `public-extension`; channel credentials, audit logs, account risk state, private queries, and personal watchlists are `private-config` or `private-knowledge`.

Search results that become Moonforge signals should include `visibility`, `open_source_action`, and destination before being promoted to learning notes, watchlists, or backlog.

## 核心原则

1. **账号安全优先**：GitHub flagged 期间默认不做 GitHub Search API 和 GitHub Code Search。
2. **先读后写**：本 skill 只负责搜索和读取公开信息，不发帖、不评论、不修改外部状态。
3. **按渠道分级**：RSS / 官方网页优先，搜索 API 次之，登录态平台谨慎使用。
4. **集中审计**：每次搜索记录到本地审计日志，不记录 token。
5. **显式降级**：某个渠道被禁用时，返回“已跳过”而不是绕路猛搜。
6. **可恢复**：GitHub 账号解除 flagged 后，通过配置开关逐步恢复。

## 默认风控状态

当前默认认为 GitHub 账号处于 flagged 风险期：

- GitHub repository search：禁用
- GitHub code search：禁用
- GitHub fork sync：不属于本 skill，仍建议暂停
- Exa / RSS / B站 / 小红书 / 今日头条 / 雪球：可按需启用，但仍需限流

## 推荐用法

### 只检查状态

```bash
python3 skills/praxis-search-hub/scripts/safe_search.py status
```

### 依赖体检

```bash
python3 skills/praxis-search-hub/scripts/safe_search.py doctor
```

`doctor` 会检查：`agent-reach`、`mcporter`、`opencli`、`bili`、`gh`、`last30days` skill 是否存在，并给出缺失依赖的恢复建议。

### 网页搜索，优先 Exa

```bash
python3 skills/praxis-search-hub/scripts/safe_search.py web "open source agent framework" --limit 5
```

### GitHub 仓库搜索，默认会被风控拦截

```bash
python3 skills/praxis-search-hub/scripts/safe_search.py github-repos "mcp server" --limit 5
```

如果确实要恢复 GitHub 搜索，先确认账号已解除 flagged，再设置：

```bash
PRAXIS_SEARCH_GITHUB_ENABLED=true python3 skills/praxis-search-hub/scripts/safe_search.py github-repos "mcp server" --limit 5
```

### Dry-run

```bash
python3 skills/praxis-search-hub/scripts/safe_search.py github-repos "agent" --dry-run
```

### 社交平台搜索，走 Agent-Reach 生态后端

```bash
python3 skills/praxis-search-hub/scripts/safe_search.py social bilibili "OpenHuman MCP" --limit 5
python3 skills/praxis-search-hub/scripts/safe_search.py social xiaohongshu "AI 工作流" --limit 5
python3 skills/praxis-search-hub/scripts/safe_search.py social toutiao "AI Agent" --limit 5
python3 skills/praxis-search-hub/scripts/safe_search.py social reddit "agent reach" --limit 5
```

注意：今日头条当前走 `opencli toutiao hot` 公开热榜；`query` 用于审计和日报上下文，不代表站内关键词搜索。

如果 `bili` 或 `opencli` 不存在，命令会返回 `skipped=true`，不会绕路搜索。

### GitHub 搜索建议（零 API 消耗）

不调用 GitHub API，只生成可直接使用的搜索链接和命令：

```bash
python3 skills/praxis-search-hub/scripts/safe_search.py gh-suggest "mcp server" --limit 5
```

输出包含 4 种变体查询（原始、加 stars 筛选、最近活跃、最近新建），每种都给出：
- `github_url` — 浏览器直接打开
- `cli_command` — 复制到终端执行
- `cli_with_fields` — 带字段的 gh 命令

### 单仓库查询（走 Core API，5000/hr，安全）

已知 `owner/repo` 时，直接查详情，不走 Search API：

```bash
python3 skills/praxis-search-hub/scripts/safe_search.py gh-lookup anthropics/claude-code
```

返回 stars、forks、语言、license、topics、最近推送时间等。走 `gh api repos/...`（Core API，配额 5000/hr），完全不会触发 Search API 限流。

### 深度研究，路由到 last30days

```bash
python3 skills/praxis-search-hub/scripts/safe_search.py deep-research "OpenHuman personal assistant setup"
```

默认不会自动执行 last30days，只会检测它是否安装并给出手动调用建议。若要允许自动化流程提示 last30days，可设置：

```bash
PRAXIS_SEARCH_LAST30DAYS_ENABLED=true python3 skills/praxis-search-hub/scripts/safe_search.py deep-research "topic"
```

## 研究能力

### research — 多源研究管道

```bash
python3 scripts/safe_search.py research "AI agent framework" --max-sources 5
python3 scripts/safe_search.py research "MCP server" --social  # 含社交媒体
```

自动编排：web 搜索 → 内置 API → gh-suggest → (可选 social)，去重后返回结构化报告，带证据分级和置信度。

### catalog — 研究记忆

```bash
python3 scripts/safe_search.py catalog list              # 查看所有研究过的主题
python3 scripts/safe_search.py catalog recall --query "AI agent"  # 回忆相关研究
python3 scripts/safe_search.py catalog prune              # 清理过期条目
```

每次 `research` 搜索自动存入 catalog，下次搜同类主题时自动召回历史结果。

### gate — 搜索策略分析

```bash
python3 scripts/safe_search.py gate
```

分析审计日志，告诉你哪些渠道对哪些查询类型最有效。

### 证据分级

每个搜索结果自动获得信任等级：
- **A**: 官方文档、主源（docs.github.com、arxiv.org 等）
- **B**: 高质量次源（stars≥100 的仓库、Exa 搜索结果）
- **C**: 社区内容（Reddit、博客、社交媒体）
- **D**: 低权威源

## GitHub 限流机制

即使 `PRAXIS_SEARCH_GITHUB_ENABLED=true`，GitHub 搜索也受以下**硬限制**保护：

| 限制 | 值 | 说明 |
|------|------|------|
| 最小调用间隔 | 3 秒 | 保证不超过 20 次/分钟（GitHub 上限 30/min） |
| 单会话最大调用 | 10 次 | 防止单次自动化任务消耗过多配额 |
| remaining 地板 | < 10 自动暂停 | 当 GitHub 返回 `x-ratelimit-remaining < 10` 时拒绝新请求 |
| ETag 缓存 | 15 分钟 | 304 响应不消耗 rate limit |
| 跨进程安全 | 文件锁 | 多个会话同时运行也不会互相踩踏 |

### 查看限流状态

```bash
python3 skills/praxis-search-hub/scripts/safe_search.py ratelimit show
```

### 重置限流状态

```bash
python3 skills/praxis-search-hub/scripts/safe_search.py ratelimit reset
```

### 限流状态文件

- `~/.praxis-search-hub/ratelimit.json` — 共享状态（ETag 缓存、上次调用时间、remaining）
- `~/.praxis-search-hub/ratelimit.lock` — 文件锁（自动管理，勿手动编辑）

## 环境变量

| 变量 | 默认值 | 说明 |
|---|---:|---|
| `PRAXIS_SEARCH_GITHUB_ENABLED` | `false` | 是否允许 GitHub Search API（即使开启也受限流保护） |
| `PRAXIS_SEARCH_GITHUB_CODE_ENABLED` | `false` | 是否允许 GitHub Code Search |
| `PRAXIS_SEARCH_EXA_ENABLED` | `true` | 是否允许 Exa 搜索 |
| `PRAXIS_SEARCH_OPENCLI_ENABLED` | `true` | 是否允许 OpenCLI 平台搜索 |
| `PRAXIS_SEARCH_BILI_ENABLED` | `true` | 是否允许 Bilibili CLI 搜索 |
| `PRAXIS_SEARCH_LAST30DAYS_ENABLED` | `false` | 是否允许 deep-research 路由提示 last30days |
| `PRAXIS_SEARCH_AUDIT_LOG` | `~/.praxis-search-hub/audit.jsonl` | 审计日志路径 |
| `PRAXIS_SEARCH_MAX_LIMIT` | `10` | 单次搜索最大结果数 |

## 输出约定

- 返回 JSON，包含 `ok`、`channel`、`query`、`skipped`、`reason`、`results`。
- 禁用渠道必须返回 `skipped=true`，不得绕过。
- 不输出 token、cookie、Authorization header。

## 与 Agent-Reach 的关系

- Agent-Reach 是多平台访问层。
- praxis-search-hub 是个人风控网关。
- 对 B站、小红书、今日头条、Reddit、Twitter、Exa 等渠道，praxis-search-hub 调用 Agent-Reach 生态命令，例如 `mcporter`、`opencli`、`bili`。
- `doctor` 会检查 `<SKILLS_DIR>/agent-reach/SKILL.md` 和相关 CLI 是否存在。新电脑缺失时返回跳过和恢复建议。
- 对 GitHub，praxis-search-hub 默认直接管控 GitHub Search API 是否允许。

## 与 last30days 的关系

- last30days 是研究型 skill，会自己跑近 30 天调研流程。
- praxis-search-hub 不替代 last30days，但可以作为日报/自动化任务的安全搜索入口。
- 若 GitHub flagged，last30days 不应被自动化日报调用来绕过 GitHub 搜索限制。
- `deep-research` 只检测并提示 last30days 路由，默认不自动执行。这样新电脑只有 praxis-search-hub 时也能安全降级。

## 新电脑恢复

### 快速恢复（一条命令）

```bash
bash skills/praxis-search-hub/setup.sh
```

脚本会逐项检查并提示缺失依赖的恢复方式。

### 只装 praxis-search-hub 时的降级行为

| 命令 | 无依赖 | 只装 gh | 装齐 Agent-Reach |
|------|--------|---------|-----------------|
| `status` | ✅ | ✅ | ✅ |
| `doctor` | ✅ | ✅ | ✅ |
| `ratelimit` | ✅ | ✅ | ✅ |
| `gh-suggest` | ✅ | ✅ | ✅ |
| `fetch` | ✅ 内置 | ✅ | ✅ |
| `web` | ✅ 内置 DDG 兜底 | ✅ | ✅ Exa 优先 |
| `gh-lookup` | ❌ skipped | ✅ | ✅ |
| `social *` | ❌ skipped | ❌ skipped | ✅ |
| `deep-research` | ❌ skipped | ❌ skipped | ❌ (需 last30days) |

内置能力（零依赖，只需 Python + 网络）：
- `web` 搜索：自动路由到最佳免费 API
  - 含 "github/repo/stars/framework" → GitHub 未认证 API（60/hr，Core API，安全）
  - 含 "npm/package/module" → npm registry 搜索
  - 其他 → GitHub API → npm → DuckDuckGo HTML 降级链
- `fetch` 抓取：Jina Reader → 直接 HTTP 抓取 + HTML 解析
- `gh-suggest`：生成搜索链接和命令，纯本地计算
- `gh-lookup`：单仓库查询（需 gh CLI，走 Core API 5000/hr）

规则：外部工具不可用时优先走内置兜底；完全无法兜底时返回 `skipped=true` + 恢复路径。

## 能力层级（开源裁剪依据）

每个命令标记了层级，`praxis-open-source-prop` 读取 `tiers` 命令自动裁剪：

```bash
python3 scripts/safe_search.py tiers   # 查看层级
```

| 层级 | 含义 | 命令数 | 开源策略 |
|------|------|--------|---------|
| **CORE** | Python 标准库，零依赖 | 10 | 全部保留 |
| **ENHANCED** | 可选 CLI 工具 | 2 | 保留，缺失时自动降级 |
| **ADVANCED** | 外部 skill 或认证 | 3 | 移除或 stub |

裁剪时：保留 CORE + ENHANCED（graceful degradation），移除 ADVANCED。

## 禁止事项

- 不要在 flagged 期间通过 `gh search`、网页 code search、第三方批量搜索绕过 GitHub 限制。
- 不要把 GitHub PAT、cookies、session、邮箱验证码写入日志。
- 不要自动执行写操作、fork sync、PR、issue、评论。

## 参考项目

本 skill 的设计参考了以下开源项目：

| 项目 | 参考内容 | 链接 |
|------|----------|------|
| **fomo-researcher** | 语义记忆、研究目录、跨源综合 | [razpetel/fomo-researcher](https://github.com/razpetel/fomo-researcher) |
| **deep-research-claude** | 四管道架构、对抗性验证、仓库级智能 | [dbc-oduffy/deep-research-claude](https://github.com/dbc-oduffy/deep-research-claude) |
| **research-ai-skills** | 证据账本、信任分级 A-D、压缩边界 | [siosio34/research-ai-skills](https://github.com/siosio34/research-ai-skills) |
| **smart-search** | 一次性门控、互补工具角色、策略审查 | [JiangHe12/smart-search](https://github.com/JiangHe12/smart-search) |
| **fathomx** | 智能路由、认识论标记、Rust 引擎 | [Runa798/fathomx](https://github.com/Runa798/fathomx) |
| **mindgap** | 复合记忆架构、知识图谱、跨会话累积 | [grburgess/mindgap](https://github.com/grburgess/mindgap) |
| **claude-code-deep-research-v2** | AggAgent、BATS 预算感知、Co-Scientist | [jamoeight/claude-code-deep-research-v2](https://github.com/jamoeight/claude-code-deep-research-v2) |
| **GPT Researcher** | Planner/Executor/Publisher 三阶段 | [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) |
| **STORM** | 多视角模拟对话、DSPy 集成 | [stanford-oval/storm](https://github.com/stanford-oval/storm) |
| **Exa** | 语义搜索 API、MCP 集成 | [exa.ai](https://exa.ai) |
| **Tavily** | Agent 原生搜索、Research 端点 | [tavily.com](https://tavily.com) |
| **Jina Reader** | URL→Markdown、免费搜索 | [jina-ai/reader](https://github.com/jina-ai/reader) |

### 模块 → 参考映射

| 模块 | 主要参考 |
|------|---------|
| `lib/catalog.py` | fomo-researcher（语义记忆）、mindgap（知识图谱）、research-catalogue（git as memory） |
| `lib/evidence.py` | research-ai-skills（证据账本）、fathomx（认识论标记）、Claude-Code-Deep-Research（验证门控） |
| `lib/gate.py` | smart-search（一次性门控）、deep-research-claude（PreToolUse 路由）、fathomx（智能路由） |
| `lib/research.py` | deep-research-claude（四管道）、GPT Researcher（planner/executor）、fomo-researcher（跨源综合） |
| 主文件限流 | GitHub API best practices（ETag、rate limit headers） |
| 内置搜索 | GitHub unauthenticated API（60/hr）、npm registry、DuckDuckGo HTML |
