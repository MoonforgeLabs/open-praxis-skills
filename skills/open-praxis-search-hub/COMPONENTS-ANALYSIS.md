# praxis-search-hub 组件分析

## 安全保证

✅ **所有操作都排除 GitHub Search API**
✅ **gh-lookup 使用 Core API (5000/hr，安全)**
✅ **Exa 搜索国内可访问**
✅ **Ollama 本地分析，完全免费**

## 组件总览

| 组件 | 触发方式 | API | 风控风险 | 结果存储 |
|------|----------|-----|----------|----------|
| Exa 搜索 | `praxis-search web` | Exa (mcporter) | ✅ 无 | 终端 |
| gh-lookup | `praxis-search gh-lookup` | Core API (5000/hr) | ✅ 无 | 终端 |
| gh-suggest | `praxis-search gh-suggest` | 无 (本地计算) | ✅ 无 | 终端 |
| last30days | `praxis-search deep-research --use-llm` | **已排除 GitHub** | ✅ 无 | 终端 |
| agent-reach | mcporter 调用 | 各平台 API | ✅ 无 | 终端 |
| **AnySearch** | `praxis-search anysearch` | AnySearch API | ✅ 无 | 终端 |

## AnySearch 垂直搜索

### 支持的领域

| 领域 | 命令 | 说明 |
|------|------|------|
| **finance** | `praxis-search anysearch "AAPL" --domain finance` | 金融搜索 |
| **academic** | `praxis-search anysearch "machine learning" --domain academic` | 学术搜索 |
| **code** | `praxis-search anysearch "react hooks" --domain code` | 代码搜索 |
| **legal** | `praxis-search anysearch "patent" --domain legal` | 法律搜索 |
| **health** | `praxis-search anysearch "diabetes" --domain health` | 健康搜索 |
| **security** | `praxis-search anysearch "CVE" --domain security` | 安全搜索 |
| **travel** | `praxis-search anysearch "Paris" --domain travel` | 旅行搜索 |
| **film** | `praxis-search anysearch "Inception" --domain film` | 电影搜索 |
| **gaming** | `praxis-search anysearch "Minecraft" --domain gaming` | 游戏搜索 |

### 使用示例

```bash
# 金融搜索
praxis-search anysearch "AAPL" --domain finance

# 学术搜索
praxis-search anysearch "transformer architecture" --domain academic

# 代码搜索
praxis-search anysearch "python asyncio" --domain code

# 通过 research.sh 使用
research "AAPL" --domain finance
```

### 优势

- ✅ **零风控**：不调用 GitHub API
- ✅ **垂直搜索**：16 个专业领域
- ✅ **零配置**：匿名可用
- ✅ **国内可访问**：无网络限制

## GitHub 风控保护

### 已禁用的命令

| 命令 | API | 风控风险 | 替代方案 |
|------|-----|----------|----------|
| `gh search repos` | Search API (30/min) | ⚠️ 有风险 | `safe-search gh-lookup` |
| `gh search code` | Search API (30/min) | ⚠️ 有风险 | `safe-search web` |
| `gh search issues` | Search API (30/min) | ⚠️ 有风险 | `safe-search gh-lookup` |
| `gh search prs` | Search API (30/min) | ⚠️ 有风险 | `safe-search gh-lookup` |

### 安全的 GitHub 命令

| 命令 | API | 风控风险 |
|------|-----|----------|
| `gh repo view` | Core API (5000/hr) | ✅ 无 |
| `gh api` | Core API (5000/hr) | ✅ 无 |
| `gh issue list` | Core API (5000/hr) | ✅ 无 |
| `gh pr list` | Core API (5000/hr) | ✅ 无 |

## 详细分析

### 1. Exa 搜索 (web)

**触发方式**:
```bash
safe-search web "查询内容" --limit 5
```

**工作原理**:
- 通过 mcporter 调用 Exa API
- 语义搜索，理解查询意图
- 返回相关文章和项目

**API 消耗**:
- Exa API 配额（按套餐）

**风控风险**: ✅ 无
- 不涉及 GitHub API
- 国内可访问

**结果存储**:
- 仅返回到终端
- 不持久化存储

---

### 2. gh-lookup

**触发方式**:
```bash
safe-search gh-lookup owner/repo
```

**工作原理**:
- 使用 GitHub Core API (`/repos/{owner}/{repo}`)
- 查询单个仓库的详细信息
- 不走 Search API

**API 消耗**:
- GitHub Core API: 5000 次/小时
- 每次查询消耗 1 次

**风控风险**: ✅ 无
- Core API 配额宽松
- 不触发 Search API 限流

**结果存储**:
- 仅返回到终端
- 不持久化存储

---

### 3. gh-suggest

**触发方式**:
```bash
safe-search gh-suggest "查询内容"
```

**工作原理**:
- 纯本地计算
- 生成 GitHub 搜索链接和 gh 命令
- 不调用任何 API

**API 消耗**:
- 无

**风控风险**: ✅ 无
- 不调用任何 API
- 最安全的方式

**结果存储**:
- 仅返回到终端
- 不持久化存储

---

### 4. last30days

**触发方式**:
```bash
safe-search deep-research --use-llm "查询内容"
```

**工作原理**:
- 调用 last30days 脚本
- 使用 GitHub Search API 搜索 Issues/PRs
- 使用 Ollama 进行 LLM 分析

**API 消耗**:
- GitHub Search API: 30 次/分钟
- 每次搜索消耗 1 次配额

**风控风险**: ⚠️ 有风险
- 使用 Search API（30/min 限制）
- 频繁调用可能触发风控

**结果存储**:
- 仅返回到终端
- 不持久化存储

**安全建议**:
- 优先使用 Exa 搜索
- 避免频繁调用
- 配置 `EXCLUDE_SOURCES=github` 可禁用 GitHub 搜索

---

### 5. agent-reach

**触发方式**:
```bash
mcporter call "agent-reach.xxx(query: ...)"
```

**工作原理**:
- 通过 mcporter 调用 agent-reach
- 访问各平台 API（B站、小红书、头条等）
- 统一搜索入口

**API 消耗**:
- 各平台 API 配额

**风控风险**: ✅ 无
- 不涉及 GitHub API
- 各平台独立风控

**结果存储**:
- 仅返回到终端
- 不持久化存储

---

## 内化搜索（内置能力）

praxis-search-hub 有一些内置的搜索能力，不需要外部依赖：

### 1. web 搜索（内置 DDG 兜底）

```bash
safe-search web "查询内容"
```

- 无依赖时使用 DuckDuckGo HTML
- 国内可访问
- 结果质量一般

### 2. fetch 抓取

```bash
safe-search fetch "URL"
```

- 使用 Jina Reader 或直接 HTTP 抓取
- 将网页转为 Markdown
- 国内可访问

### 3. gh-lookup（内置）

```bash
safe-search gh-lookup owner/repo
```

- 使用 gh CLI
- 走 Core API（5000/hr）
- 安全无风险

---

## 搜索结果存储

### 当前状态

所有搜索结果**仅返回到终端**，不持久化存储。

### 可选的存储方式

1. **重定向到文件**:
```bash
safe-search web "查询" > results.json
```

2. **使用 research.sh 脚本**:
```bash
research "查询" --full 2>&1 | tee results.txt
```

3. **集成到 knowledge-radar**:
```bash
# 未来可以集成
python3 scripts/radar.py add --title "..." --source "exa" --references "..."
```

---

## GitHub 风控总结

### 安全的操作

| 操作 | API | 配额 | 风控风险 |
|------|-----|------|----------|
| `gh-lookup` | Core API | 5000/hr | ✅ 无 |
| `gh-suggest` | 无 | 无限 | ✅ 无 |
| `web` (Exa) | Exa | 按套餐 | ✅ 无 |
| `fetch` | HTTP | 无限 | ✅ 无 |

### 有风险的操作

| 操作 | API | 配额 | 风控风险 |
|------|-----|------|----------|
| `last30days` GitHub | Search API | 30/min | ⚠️ 有风险 |
| `last30days` grounding | Brave/Exa | 按套餐 | ✅ 无 |

---

## 推荐使用方式

### 日常研究（安全）

```bash
# 1. Exa 搜索
safe-search web "项目名"

# 2. 查看 GitHub 详情
safe-search gh-lookup owner/repo

# 3. 生成搜索链接
safe-search gh-suggest "查询内容"
```

### 深度研究（谨慎）

```bash
# 使用 last30days，但限制 GitHub 搜索
EXCLUDE_SOURCES=github safe-search deep-research --use-llm "查询内容"
```

### 完全安全

```bash
# 使用 research.sh 脚本
research "查询" --full
```

---

## 配置建议

### 禁用 GitHub 搜索（last30days）

```bash
# ~/.config/last30days/.env
EXCLUDE_SOURCES=github
```

### 限制 GitHub API 调用

```bash
# 查看限流状态
safe-search ratelimit show

# 重置限流
safe-search ratelimit reset
```

### 使用本地 LLM

```bash
# ~/.config/last30days/.env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENROUTER_API_KEY=ollama
OPENROUTER_BASE_URL=http://localhost:11434/v1/chat/completions
LAST30DAYS_MODEL=qwen2.5:14b
```
