# Alex Safe Search — 快速入门

## 30 秒安装

```bash
# 1. 克隆（或下载）skill
git clone https://github.com/MoonforgeLabs/praxis-skills.git /tmp/praxis-skills

# 2. 复制到 Claude Code skills 目录
cp -r /tmp/praxis-skills/skills/praxis-search-hub ~/.claude/skills/

# 3. 验证
python3 ~/.claude/skills/praxis-search-hub/scripts/safe_search.py doctor
```

## 最低要求

- Python 3.10+（macOS/Linux 自带）
- 网络连接
- **不需要 pip install 任何东西**

## 5 种用法

```bash
# 1. 搜索网页（自动选最佳免费 API）
python3 scripts/safe_search.py web "AI agent framework"

# 2. 多源研究（自动去重 + 证据分级）
python3 scripts/safe_search.py research "MCP server" --max-sources 5

# 3. 生成 GitHub 搜索方案（零 API 消耗）
python3 scripts/safe_search.py gh-suggest "react state management"

# 4. 查看搜索历史
python3 scripts/safe_search.py catalog list

# 5. 抓取网页内容
python3 scripts/safe_search.py fetch "https://example.com"
```

## 增强安装（可选）

```bash
# 装 gh CLI → 解锁 gh-lookup 单仓库查询
brew install gh  # 或 https://cli.github.com

# 装 Agent-Reach → 解锁 Exa 语义搜索 + 社交媒体搜索
bash setup.sh --layer 2
```

## Windows 注意

限流功能依赖 `fcntl`（Unix-only），Windows 上会自动降级。其他功能正常。

## 完整文档

见 [SKILL.md](./SKILL.md)
