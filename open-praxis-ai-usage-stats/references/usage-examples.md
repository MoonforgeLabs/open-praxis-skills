# Usage Examples — Detailed Reference

Referenced from SKILL.md. Contains extended command examples and filtering options.

## 时间范围

```bash
python3 scripts/usage_stats.py today      # 今天
python3 scripts/usage_stats.py week       # 最近 7 天（默认）
python3 scripts/usage_stats.py month      # 最近 30 天
python3 scripts/usage_stats.py --days 14  # 最近 14 天
python3 scripts/usage_stats.py --all-time # 全部历史
```

## 过滤选项

```bash
# 按 Runtime 过滤
python3 scripts/usage_stats.py --runtime claude
python3 scripts/usage_stats.py --runtime codex
python3 scripts/usage_stats.py --runtime openhuman

# 按类型过滤
python3 scripts/usage_stats.py --kind skill
python3 scripts/usage_stats.py --kind agent
python3 scripts/usage_stats.py --kind tool

# 按项目过滤
python3 scripts/usage_stats.py --project myCode

# 按名称过滤
python3 scripts/usage_stats.py --name praxis-translate

# 组合过滤
python3 scripts/usage_stats.py --runtime claude --kind skill --days 7
```

## 输出控制

```bash
# JSON 输出
python3 scripts/usage_stats.py --format json
python3 scripts/usage_stats.py --json

# 保存报告到文件
python3 scripts/usage_stats.py --save
python3 scripts/usage_stats.py --save --output-dir ./reports

# 自定义排行榜条数
python3 scripts/usage_stats.py --limit 20
```

## Web 仪表盘

```bash
# 启动 Web 仪表盘（默认端口 8080）
python3 scripts/usage_stats.py --web

# 自定义端口
python3 scripts/usage_stats.py --web --port 9090
```

访问 http://localhost:8080 查看交互式仪表盘。

### 仪表盘功能

- 📊 实时统计卡片: 总事件数、Token、成本、成功率、健康评分
- 📈 使用趋势图: 每日事件数和 Token 使用趋势
- 🍩 分布图表: 类型、Runtime、模型、项目分布
- 🏆 排行榜: Top Skills、Top Tools
- 📋 事件列表: 最近 50 条事件详情
- 🔄 自动刷新: 每 5 分钟自动更新数据
- 📱 响应式设计: 支持移动端访问

## 数据库管理

```bash
# 迁移旧日志
python3 scripts/usage_stats.py --migrate

# 清理旧记录（默认 90 天）
python3 scripts/usage_stats.py --cleanup
python3 scripts/usage_stats.py --cleanup --cleanup-days 30
```

## 安装选项

```bash
# 安装到所有 runtime（默认）
python3 scripts/install.py

# 只安装到 Claude Code
python3 scripts/install.py --claude

# 只安装到 Codex
python3 scripts/install.py --codex

# 只安装到 OpenHuman
python3 scripts/install.py --openhuman

# 检查依赖状态
python3 scripts/install.py --check
```

## 手动记录

对于不支持 hook 的 runtime，可以手动记录：

```bash
python3 scripts/log_usage.py --kind skill --name <name> --context "简短描述"
python3 scripts/log_usage.py --kind agent --name <name> --context "简短描述"
python3 scripts/log_usage.py --kind tool --name <name> --context "简短描述"
```

## Hook 管理

```bash
# 检查 hook 状态
python3 scripts/hook_install.py status

# 重新安装 hook
python3 scripts/hook_install.py uninstall
python3 scripts/hook_install.py install
```

## 报告内容

### 总体统计
- 总事件数、总 Token 使用量、总成本估算
- 唯一会话数、唯一项目数

### 健康评分（0-100）
- 成功率评分（0-40）: 基于成功/失败比例
- 使用频率评分（0-30）: 基于日均使用次数
- 多样性评分（0-30）: 基于使用的 Runtime 数量

### 分类统计
- 按类型 (skill/agent/tool)
- 按 Runtime、按模型、按项目

### 排行榜
- Top Skills、Top Agents、Top Tools

### 成功率
- ✅ 成功 (likely_solved)
- ❌ 失败 (likely_failed)
- ❓ 未知 (unknown)
