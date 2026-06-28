# open-praxis-skills

Open source skills for AI coding agents.

## Skills

| Skill | Trigger | What it does | Dependency |
|-------|---------|--------------|------------|
| `praxis-ai-usage-stats` | "使用统计", "usage stats", "工具统计" | 统计所有 AI agent runtime（Claude Code、Codex、OpenHuman 等）的 skill/agent/tool 使用情况。支持实时捕获、SQLite 持久化、Token 统计、成本估算、成功/失败判断、Web 仪表盘 | None |
| `praxis-knowledge-radar` | "记录这个", "加入雷达", "reading list", "学习队列" | 个人知识线索追踪器：文章/链接输入 → 归类入库 → 状态流转 → 同步检查。支持手动输入、外部消息自动订阅（可选）、URL 自动抓取 | None |

## Installation

```bash
# Clone the repository
git clone https://github.com/MoonforgeLabs/open-praxis-skills.git
cd open-praxis-skills
```

### Install praxis-ai-usage-stats

```bash
cd skills/praxis-ai-usage-stats
python3 scripts/install.py
```

### Install praxis-knowledge-radar

```bash
# No installation needed - use scripts directly
cd skills/praxis-knowledge-radar

# Add a knowledge item
python3 scripts/radar.py add --title "学习主题" --area "ai-os" --source manual

# Check status
python3 scripts/radar_enhanced.py status
```

## Usage

### praxis-ai-usage-stats

```bash
# View usage stats
python3 scripts/usage_stats.py

# Generate report
python3 scripts/generate_report.py

# Open web dashboard
open web/index.html
```

### praxis-knowledge-radar

```bash
# Add a knowledge item
python3 scripts/radar.py add --title "文章标题" --area "ai-os" --source manual --references "https://..."

# List items
python3 scripts/radar.py list --status inbox,next

# Update status
python3 scripts/radar.py update --id <id> --status learning

# View enhanced status
python3 scripts/radar_enhanced.py status
```

## Features

### praxis-ai-usage-stats
- ✅ **实时捕获**: PostToolUse hook 自动捕获 Claude Code 调用
- ✅ **SQLite 持久化**: 数据存储在本地数据库，支持快速查询
- ✅ **多 Runtime 支持**: Claude Code、Codex、OpenHuman
- ✅ **Token 统计**: input/output/cache token 详细统计
- ✅ **成本估算**: 根据模型费率自动计算成本
- ✅ **成功/失败判断**: 启发式推断 skill 执行结果
- ✅ **健康评分**: 综合评估使用健康度

### praxis-knowledge-radar
- ✅ **多源输入**: 手动输入、URL 自动抓取、外部消息订阅
- ✅ **自动归类**: 根据内容自动猜测 area 分类
- ✅ **状态流转**: inbox → next → active → learning → learned → applied
- ✅ **能力同步**: 检查 GitHub 仓库更新、本地文件变化
- ✅ **知识运维**: 间隔重复、Lint 检查、内容分级、去重
- ✅ **可选通知**: 支持钉钉等通知插件（区域特定功能）

## License

MIT
