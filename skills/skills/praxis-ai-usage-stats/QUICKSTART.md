# 🚀 快速开始指南

## 安装完成！

你的 `praxis-ai-usage-stats` 已经升级完成，吸收了所有优秀 skill 的优点！

## ✅ 已完成的功能

### 1. 核心基础设施
- ✅ SQLite 持久化存储 (`~/.praxis-ai-usage-stats/usage.db`)
- ✅ PostToolUse hook 实时捕获
- ✅ 自动清理机制（90天）

### 2. 数据解析
- ✅ Claude Code JSONL 增强解析
- ✅ Token 统计（input/output/cache）
- ✅ 成本估算（按模型费率）
- ✅ 触发提示词捕获
- ✅ 会话追踪

### 3. 分析功能
- ✅ 成功/失败启发式判断
- ✅ 健康评分（0-100分）
- ✅ 多 Runtime 统一视图
- ✅ 按类型/Runtime/模型/项目分组

### 4. 输出格式
- ✅ Markdown 终端报告
- ✅ JSON 数据导出
- ✅ Web 交互式仪表盘

## 📊 使用方法

### 基本用法

```bash
# 查看今天的统计
python3 scripts/usage_stats.py today

# 查看最近 7 天（默认）
python3 scripts/usage_stats.py

# 查看最近 30 天
python3 scripts/usage_stats.py month

# 查看全部历史
python3 scripts/usage_stats.py --all-time
```

### 过滤查询

```bash
# 只看 Claude Code
python3 scripts/usage_stats.py --runtime claude

# 只看 Skill 调用
python3 scripts/usage_stats.py --kind skill

# 按项目过滤
python3 scripts/usage_stats.py --project myCode

# 组合过滤
python3 scripts/usage_stats.py --runtime claude --kind skill --days 14
```

### 输出格式

```bash
# JSON 输出
python3 scripts/usage_stats.py --format json

# 保存报告
python3 scripts/usage_stats.py --save

# 自定义输出目录
python3 scripts/usage_stats.py --save --output-dir ./reports
```

### Web 仪表盘

```bash
# 启动 Web 仪表盘
python3 scripts/usage_stats.py --web

# 自定义端口
python3 scripts/usage_stats.py --web --port 9090
```

访问 http://localhost:8080 查看交互式仪表盘。

### 数据库管理

```bash
# 迁移旧日志
python3 scripts/usage_stats.py --migrate

# 清理旧记录
python3 scripts/usage_stats.py --cleanup

# 自定义清理天数
python3 scripts/usage_stats.py --cleanup --cleanup-days 30
```

## 🎯 Hook 管理

### 查看状态

```bash
python3 scripts/hook_install.py status
```

### 重新安装

```bash
python3 scripts/hook_install.py uninstall
python3 scripts/hook_install.py install
```

## 📈 报告解读

### 健康评分

- **70-100分**: 🟢 优秀 - 使用模式健康
- **40-69分**: 🟡 良好 - 有改进空间
- **0-39分**: 🔴 需改进 - 使用模式需优化

评分组成：
- 成功率评分（0-40）: 基于成功/失败比例
- 使用频率评分（0-30）: 基于日均使用次数
- 多样性评分（0-30）: 基于使用的 Runtime 数量

### 成功率判断

- ✅ **likely_solved**: 用户有后续消息且没有修正词
- ❌ **likely_failed**: 用户中断、错误过多、或有修正词
- ❓ **unknown**: 无后续消息，无法判断

### Token 统计

- **tokens_in**: 输入 token 数量
- **tokens_out**: 输出 token 数量
- **cache_read**: 缓存读取 token
- **cache_creation**: 缓存创建 token

### 成本估算

根据模型费率自动计算：
- Claude 3.5 Sonnet: $3/$15 per 1M tokens (input/output)
- Claude 3 Opus: $15/$75 per 1M tokens
- GPT-4: $30/$60 per 1M tokens

## 🔧 配置

### 模型费率

编辑 `scripts/hook_collect.py`：

```python
MODEL_RATES = {
    "claude-3-5-sonnet": {"input": 3.0, "output": 15.0, "cache_read": 0.3},
    "claude-3-opus": {"input": 15.0, "output": 75.0, "cache_read": 1.5},
    "gpt-4": {"input": 30.0, "output": 60.0, "cache_read": 0.0},
    # 添加更多模型...
}
```

### 数据库路径

编辑 `scripts/db.py`：

```python
DB_PATH = Path.home() / ".praxis-ai-usage-stats" / "usage.db"
```

## 📁 目录结构

```
~/.praxis-ai-usage-stats/
├── usage.db           # SQLite 数据库
├── events.jsonl       # 降级事件日志（当数据库不可用时）
└── reports/           # 保存的报告
    ├── usage-2026-06-25_120000.md
    ├── usage-2026-06-25_120000.json
    └── usage-2026-06-25_120000-full.json
```

## 🎨 Web 仪表盘功能

### 统计卡片
- 📈 总事件数
- 🔤 总 Token
- 💰 总成本
- ✅ 成功率
- 📊 日均使用
- 🎯 健康评分

### 图表
- 📈 使用趋势（事件数 + Token）
- 🍩 类型分布（skill/agent/tool）
- 🖥️ Runtime 分布
- 🤖 模型分布
- 🏆 Top Skills
- 📁 项目分布

### 事件列表
- 最近 50 条事件详情
- 时间、Runtime、类型、名称、Token、成本、结果

### 自动刷新
- 每 5 分钟自动更新数据
- 手动刷新按钮

## 🆚 对比原版

| 功能 | 原版 | 新版 |
|------|------|------|
| 实时捕获 | ❌ | ✅ |
| SQLite 存储 | ❌ | ✅ |
| Token 统计 | ❌ | ✅ |
| 成本估算 | ❌ | ✅ |
| 成功/失败判断 | ❌ | ✅ |
| 健康评分 | ❌ | ✅ |
| Web 仪表盘 | ❌ | ✅ |
| 自动清理 | ❌ | ✅ |
| 触发提示词 | ❌ | ✅ |
| 会话追踪 | ❌ | ✅ |

## 🐛 故障排除

### Hook 不工作

```bash
# 检查状态
python3 scripts/hook_install.py status

# 重新安装
python3 scripts/hook_install.py uninstall
python3 scripts/hook_install.py install
```

### 数据库问题

```bash
# 检查数据库
ls -la ~/.praxis-ai-usage-stats/

# 重新初始化
rm ~/.praxis-ai-usage-stats/usage.db
python3 scripts/usage_stats.py --migrate
```

### 权限问题

```bash
# 确保脚本可执行
chmod +x scripts/hook_collect.py
chmod +x scripts/usage_stats.py
```

## 📚 更多信息

- 详细文档: [SKILL.md](SKILL.md)
- 设计原则: [references/design-principles.md](references/design-principles.md)
- 安装指南: [references/install-guide.md](references/install-guide.md)

## 🎉 开始使用

现在你可以：

1. **查看统计**: `python3 scripts/usage_stats.py today`
2. **启动仪表盘**: `python3 scripts/usage_stats.py --web`
3. **查看历史**: `python3 scripts/usage_stats.py --all-time`
4. **导出数据**: `python3 scripts/usage_stats.py --save --format json`

享受你的 AI 使用统计吧！🚀
