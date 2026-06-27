# open-praxis-skills

Open source skills for AI coding agents.

## Skills

| Skill | Trigger | What it does | Dependency |
|-------|---------|--------------|------------|
| `praxis-ai-usage-stats` | "使用统计", "usage stats", "工具统计" | 统计所有 AI agent runtime（Claude Code、Codex、OpenHuman 等）的 skill/agent/tool 使用情况。支持实时捕获、SQLite 持久化、Token 统计、成本估算、成功/失败判断、Web 仪表盘 | None |

## Installation

```bash
# Clone the repository
git clone https://github.com/MoonforgeLabs/open-praxis-skills.git
cd open-praxis-skills

# Install praxis-ai-usage-stats
cd praxis-ai-usage-stats
python3 scripts/install.py
```

## Usage

```bash
# View usage stats
python3 scripts/usage_stats.py

# Generate report
python3 scripts/generate_report.py

# Open web dashboard
open web/index.html
```

## Features

- ✅ **实时捕获**: PostToolUse hook 自动捕获 Claude Code 调用
- ✅ **SQLite 持久化**: 数据存储在本地数据库，支持快速查询
- ✅ **多 Runtime 支持**: Claude Code、Codex、OpenHuman
- ✅ **Token 统计**: input/output/cache token 详细统计
- ✅ **成本估算**: 根据模型费率自动计算成本
- ✅ **成功/失败判断**: 启发式推断 skill 执行结果
- ✅ **健康评分**: 综合评估使用健康度

## License

MIT
