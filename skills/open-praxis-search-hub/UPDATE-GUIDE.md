# praxis-search-hub 更新指南

## 底层工具版本

| 工具 | 锁定版本 | 用途 | 更新影响 |
|------|----------|------|----------|
| agent-reach | v1.5.0 | 社交媒体搜索 | 命令行参数变化 |
| last30days | 3.8.3 | 深度研究 | 脚本参数变化 |
| anysearch-skill | 2.1.0 | 垂直搜索 | API 变化 |
| mcporter | 0.9.0 | MCP 工具管理 | 接口变化 |
| opencli | 1.8.4 | 开放平台 CLI | 命令行参数变化 |
| bili | 0.6.2 | B站 CLI | 命令行参数变化 |

## 版本检查

```bash
# 检查所有底层工具版本
./scripts/check_versions.sh
```

## 更新流程

### 1. 检查更新

```bash
# 检查 agent-reach 更新
agent-reach check-update

# 检查 last30days 更新
cd ~/.agents/skills/last30days && git pull

# 检查 anysearch-skill 更新
cd ~/.agents/skills/anysearch-skill && git pull
```

### 2. 测试兼容性

```bash
# 测试 agent-reach
agent-reach doctor

# 测试 last30days
python3 ~/.agents/skills/last30days/scripts/last30days.py --diagnose

# 测试 anysearch-skill
python3 ~/.agents/skills/anysearch-skill/scripts/anysearch_cli.py search "test"
```

### 3. 更新 praxis-search-hub

如果底层工具的接口发生变化，需要更新 praxis-search-hub 的调用代码：

```bash
# 检查调用代码
grep -n "agent-reach\|last30days\|anysearch" scripts/safe_search.py

# 更新调用逻辑
# ...
```

### 4. 验证更新

```bash
# 测试所有功能
./scripts/test_all.sh

# 测试特定功能
python3 scripts/safe_search.py web "test"
python3 scripts/safe_search.py social bilibili "test"
python3 scripts/safe_search.py anysearch "test" --domain finance
python3 scripts/safe_search.py deep-research "test" --use-llm
```

## 更新策略

### 保守策略（推荐）

- 锁定版本，不自动更新
- 定期手动检查更新
- 测试兼容性后再更新

### 激进策略

- 自动更新底层工具
- 每次调用前检查版本
- 自动适配接口变化

## 常见问题

### Q: 底层工具更新后 praxis-search-hub 不工作了？

A: 检查版本是否匹配：
```bash
./scripts/check_versions.sh
```

### Q: 如何回滚底层工具？

A: 使用 git 回滚：
```bash
cd ~/.agents/skills/last30days
git checkout v3.8.3
```

### Q: 如何报告兼容性问题？

A: 在 praxis-search-hub 的 issue 中报告，包含：
- 底层工具版本
- 错误信息
- 复现步骤
