# 安全研究工作流

完全免费、国内可用、**不触发 GitHub 风控**的研究工作流。

## 安全保证

✅ **所有操作都排除 GitHub Search API**
✅ **gh-lookup 使用 Core API (5000/hr，安全)**
✅ **Exa 搜索国内可访问**
✅ **Ollama 本地分析，完全免费**
✅ **AnySearch 垂直搜索，零风控**

## 快速开始

```bash
# 搜索项目（Exa，安全）
research "DeerFlow 字节跳动"

# 查看 GitHub 详情（Core API，安全）
research --github bytedance/deer-flow

# 完整流程（搜索 + Ollama 分析，安全）
research "MoneyPrinterTurbo" --full

# 垂直搜索（金融/学术/代码等）
research "AAPL" --domain finance
research "machine learning" --domain academic
research "react hooks" --domain code
```

## 命令说明

### 搜索（Exa，国内可访问）

```bash
# 搜索技术文章和项目
research "AI agent framework"
research "短视频制作工具"
research "字节跳动开源项目"
```

### 查看 GitHub 详情（Core API，5000/hr，安全）

```bash
# 已知仓库名时直接查看
research --github bytedance/deer-flow
research --github harry0703/MoneyPrinterTurbo
```

### 完整流程（搜索 + Ollama 分析）

```bash
# 自动搜索并用本地 LLM 分析
research "DeerFlow" --full
```

## 底层命令

### praxis-search-hub

```bash
# Exa 语义搜索
safe-search web "查询内容" --limit 5

# GitHub 仓库详情（安全，不触发风控）
safe-search gh-lookup owner/repo

# GitHub 搜索建议（零 API 消耗）
safe-search gh-suggest "查询内容"
```

### Ollama 本地 LLM

```bash
# 直接调用 Ollama 分析
curl -s http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:14b",
    "messages": [{"role": "user", "content": "分析这个项目..."}],
    "max_tokens": 500
  }'
```

## 安全性

| 方式 | API | 配额 | 风控风险 |
|------|-----|------|----------|
| `web` (Exa) | Exa | 按套餐 | ✅ 无 |
| `gh-lookup` | Core API | 5000/hr | ✅ 无 |
| `gh-suggest` | 无 | 无限 | ✅ 无 |
| Ollama | 本地 | 无限 | ✅ 无 |

## 工作流程

```
头条/雪球看到项目名
        ↓
research "项目名" (Exa 搜索)
        ↓
research --github owner/repo (查看 GitHub 详情)
        ↓
research "项目名" --full (Ollama 分析)
        ↓
决定是否深入学习
```

## 配置

### Ollama 模型

```bash
# 查看可用模型
curl -s http://localhost:11434/api/tags | python3 -m json.tool

# 使用其他模型
export OLLAMA_MODEL=deepseek-r1:14b
```

### Exa API

Exa 通过 mcporter 调用，无需额外配置。

## 故障排除

### Ollama 未运行

```bash
# 启动 Ollama
ollama serve

# 检查状态
curl -s http://localhost:11434/api/tags
```

### Exa 搜索失败

```bash
# 检查 mcporter
mcporter call "exa.web_search_exa(query: 'test', numResults: 1)"
```

### GitHub 限流

```bash
# 查看限流状态
safe-search ratelimit show

# 重置限流
safe-search ratelimit reset
```
