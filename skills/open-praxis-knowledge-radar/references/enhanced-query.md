# 增强查询系统详解

## 查看所有主线状态

```bash
python3 scripts/radar_enhanced.py status
```

显示所有主线任务的优先级、状态、任务数量和下一步。

## 查看指定主线详情

```bash
python3 scripts/radar_enhanced.py status <area>
```

示例：
```bash
python3 scripts/radar_enhanced.py status code-understanding
```

显示：
- 描述、优先级、状态
- 下一步（可执行项）
- 依赖（需要安装/配置什么）
- 竞品（需要研究什么）
- 历史参考（链接和笔记）

## 查看下一步行动

```bash
# 所有主线
python3 scripts/radar_enhanced.py next

# 指定主线
python3 scripts/radar_enhanced.py next ai-os
```

## 查看参考资料

```bash
python3 scripts/radar_enhanced.py refs skill-ecosystem
```

显示指定主线的所有历史参考。

## 查看依赖

```bash
# 所有主线
python3 scripts/radar_enhanced.py deps

# 指定主线
python3 scripts/radar_enhanced.py deps code-understanding
```

## 查看竞品

```bash
# 所有主线
python3 scripts/radar_enhanced.py competitors

# 指定主线
python3 scripts/radar_enhanced.py competitors search-skills
```

## 生成总结报告

```bash
python3 scripts/radar_enhanced.py summary
```

显示：
- 总任务数和主线数
- 优先级分布
- 状态分布
- P0 优先级任务
- 所有待执行的下一步行动

## 能力同步

### 检查单个任务

```bash
python3 scripts/radar_enhanced.py sync <area>
```

示例：
```bash
python3 scripts/radar_enhanced.py sync skill-creation
```

功能：
- 检查 GitHub 仓库的最新状态（stars、最后更新、最近提交）
- 检查本地 skill 的文件变化
- 对比已记录的 `reference_state`，发现新能力
- 生成同步报告和建议

### 批量同步所有 learned 任务

```bash
python3 scripts/radar_enhanced.py sync-all
```

自动检查所有 `status=learned` 的主线任务，批量生成同步报告。

### 批量同步 + 钉钉通知

```bash
python3 scripts/radar_enhanced.py sync-all --notify
```

同步完成后自动发送钉钉消息通知。

## Reference State 结构

在 `tasks.jsonl` 中，`reference_state` 字段记录每个参考来源的状态：

```json
{
  "reference_state": {
    "praxis-skill-forge": {
      "last_checked": "2026-06-27",
      "version": "1.0",
      "capabilities": ["validate", "package", "install", "eval", "description-improve"]
    },
    "anthropics/skills": {
      "last_checked": "2026-06-27",
      "stars": 155646,
      "last_updated": "2026-06-27T06:09:11Z",
      "capabilities": ["create", "validate", "package"]
    }
  }
}
```

## 定期扫描

### 设置 Cron Job

```bash
# 交互式设置（推荐）
bash scripts/setup_cron.sh

# 或手动添加（每周一早上 9 点）
0 9 * * 1 /path/to/scheduled_sync.sh
```

### 手动运行

```bash
bash scripts/scheduled_sync.sh
```

日志位置：`~/.praxis-skills/data/knowledge-radar/logs/sync-*.log`

## 钉钉通知配置

### 首次配置

```bash
python3 scripts/dingtalk_notify.py setup
```

按提示输入：
- Webhook URL（从钉钉群机器人获取）
- Secret（可选，加签模式）

### 测试配置

```bash
python3 scripts/dingtalk_notify.py test
```

### 手动发送消息

```bash
python3 scripts/dingtalk_notify.py send --title "标题" --content "内容"
```

## 关注点

- GitHub 仓库的最近 commits（新功能、bug 修复）
- Stars 增长（项目热度）
- 本地 skill 的文件变化（手动更新）
