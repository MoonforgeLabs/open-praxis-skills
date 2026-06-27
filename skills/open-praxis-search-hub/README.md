# praxis-search-hub

统一搜索网关，支持风险控制、审计和降级。

## 架构

```
praxis-search-hub/
├── scripts/
│   ├── safe_search.py          # CLI 入口
│   └── lib/
│       ├── core/               # 核心基础设施
│       │   ├── constants.py    # 常量和配置
│       │   ├── env.py          # 环境变量工具
│       │   ├── audit.py        # 审计日志
│       │   ├── rate_limiter.py # GitHub 限流器
│       │   └── http.py         # HTTP 工具
│       ├── engines/            # 内置搜索引擎（零依赖）
│       │   └── __init__.py     # GitHub/npm/HN/Reddit/DDG
│       ├── channels/           # 渠道适配（可选依赖）
│       │   └── __init__.py     # web/social/gh-lookup/deep-research
│       ├── research/           # 研究能力
│       │   ├── catalog.py      # 研究记忆
│       │   ├── evidence.py     # 证据分级
│       │   ├── gate.py         # 策略分析
│       │   └── orchestrator.py # 多源研究编排
│       └── system/             # 系统诊断
│           └── __init__.py     # status/doctor/backends/tiers
├── config/                     # 配置文件
├── setup.sh                    # 安装脚本
└── README.md                   # 本文档
```

## 快速开始

### 最小安装（零依赖）

```bash
# 克隆仓库
git clone https://github.com/alex/praxis-search-hub.git
cd praxis-search-hub

# 直接使用（核心功能）
python3 scripts/safe_search.py web "query"
python3 scripts/safe_search.py gh-lookup owner/repo
python3 scripts/safe_search.py gh-suggest "query"
```

### 完整安装（所有功能）

```bash
# 安装依赖
./setup.sh

# 配置插件
./scripts/setup_plugins.sh
```

## 功能

### 核心功能（零依赖）

| 命令 | 说明 | 示例 |
|------|------|------|
| `web` | Web 搜索（Exa + 内置 fallback） | `safe_search.py web "AI agent"` |
| `fetch` | URL 内容提取 | `safe_search.py fetch "https://..."` |
| `gh-suggest` | 生成 GitHub 搜索链接（零 API） | `safe_search.py gh-suggest "query"` |
| `gh-lookup` | GitHub 仓库详情（Core API） | `safe_search.py gh-lookup owner/repo` |
| `anysearch` | 垂直领域搜索 | `safe_search.py anysearch "AAPL" --domain finance` |

### 扩展功能（可选依赖）

| 命令 | 依赖 | 说明 |
|------|------|------|
| `social` | agent-reach | B站/小红书/头条搜索 |
| `deep-research` | last30days | 深度研究 |
| `github-repos` | GitHub Token | GitHub 仓库搜索（认证） |
| `github-code` | GitHub Token | GitHub 代码搜索（认证） |

### 系统命令

| 命令 | 说明 |
|------|------|
| `status` | 显示网关状态 |
| `doctor` | 依赖健康检查 |
| `ratelimit` | 限流器状态 |
| `backends` | 显示活动后端 |
| `tiers` | 显示能力层级 |

## 安全性

### GitHub 风控保护

- ✅ 默认禁用 GitHub Search API
- ✅ gh-lookup 使用 Core API（5000/hr）
- ✅ gh-suggest 零 API 消耗
- ✅ Exa 搜索国内可访问

### 能力层级

| 层级 | 说明 | 开源策略 |
|------|------|----------|
| **CORE** | 零依赖 | 直接开源 |
| **ENHANCED** | 可选 CLI | 开源，文档说明依赖 |
| **ADVANCED** | 外部 skill | 移除或 stub |

## 配置

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PRAXIS_SEARCH_GITHUB_ENABLED` | `false` | 启用 GitHub 仓库搜索 |
| `PRAXIS_SEARCH_GITHUB_CODE_ENABLED` | `false` | 启用 GitHub 代码搜索 |
| `PRAXIS_SEARCH_EXA_ENABLED` | `true` | 启用 Exa 搜索 |
| `PRAXIS_SEARCH_OPENCLI_ENABLED` | `true` | 启用 OpenCLI |
| `PRAXIS_SEARCH_BILI_ENABLED` | `true` | 启用 B站搜索 |
| `PRAXIS_SEARCH_MAX_LIMIT` | `10` | 最大结果数 |

### 配置文件

- `~/.praxis-search-hub/ratelimit.json` - 限流器状态
- `~/.praxis-search-hub/audit.jsonl` - 审计日志

## 开发

### 添加新搜索引擎

1. 在 `lib/engines/` 中添加实现
2. 在 `lib/channels/` 中添加适配器
3. 在 `safe_search.py` 中添加命令

### 添加新渠道

1. 在 `lib/channels/` 中添加实现
2. 更新 `CAPABILITY_TIERS`
3. 添加依赖检查

## 测试

```bash
# 运行所有测试
./scripts/test_all.sh

# 测试特定功能
python3 scripts/safe_search.py status
python3 scripts/safe_search.py web "test"
python3 scripts/safe_search.py anysearch "test" --domain finance
```

## 许可证

MIT License
