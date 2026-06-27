# 自动捕获详解

## 设置 Cron Job

```bash
# 交互式设置（推荐）
bash scripts/setup_auto_capture.sh

# 手动添加（每 30 分钟）
*/30 * * * * /bin/bash /path/to/auto_capture.sh --notify
```

## 自动捕获脚本

```bash
# 运行自动捕获
bash scripts/auto_capture.sh

# 带钉钉通知
bash scripts/auto_capture.sh --notify
```

## 配置详情

| 配置项 | 值 | 说明 |
|--------|-----|------|
| 时间范围 | 增量模式 | 从上次拉取时间开始 |
| 条数限制 | 100 条 | 每次最多拉取 100 条消息 |
| 运行频率 | 每 30 分钟 | cron job 配置 |
| 去重机制 | URL 去重 | 已入库的不会重复 |

## 工作流程

```
钉钉群消息（每 30 分钟检查一次）
    ↓
增量拉取新消息（从上次时间点）
    ↓
提取消息中的 URL
    ↓
从消息内容提取标题和摘要
    ↓
基于 URL 去重
    ↓
自动归类（area + tags）
    ↓
入库到 tasks.jsonl
    ↓
更新拉取时间戳
    ↓
（可选）发送钉钉通知
```

## 管理 Cron Job

```bash
# 查看 cron job
crontab -l

# 编辑 cron job
crontab -e

# 删除 cron job
crontab -l | grep -v auto_capture.sh | crontab -
```

## 日志

日志位置：`~/.praxis-skills/data/knowledge-radar/logs/`

- 自动捕获日志：`auto-capture-*.log`
- Cron 日志：`cron.log`

## 关机/睡眠行为

- **睡眠期间**：cron job 不执行
- **唤醒后**：从上次时间点继续拉取
- **关机期间**：cron job 不执行
- **开机后**：从上次时间点继续拉取

**保证不遗漏**：增量模式确保从上次位置继续拉取。
