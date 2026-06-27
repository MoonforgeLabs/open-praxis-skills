# 知识雷达配置指南

## 1. 钉钉 MCP 配置（✅ 已完成）

### 配置状态

- ✅ 钉钉 MCP 已安装
- ✅ 应用凭证已配置
- ✅ Claude Code MCP 已配置

### 可用工具

钉钉 MCP 提供以下 13 个工具：

| 工具 | 功能 |
|------|------|
| `currentDateTime` | 获取当前日期和时间 |
| `searchUser` | 搜索钉钉通讯录用户 |
| `getUserDetailByUserId` | 查询用户详情 |
| `getUserIdByMobile` | 根据手机号获取用户ID |
| `getUserIdByUnionId` | 根据unionId获取用户ID |
| `getDepartmentUsersByDepId` | 获取部门成员 |
| `sendDINGMessageByRobot` | 发送DING消息（高优先级） |
| `recallDINGMessage` | 撤回DING消息 |
| `sendMessageToGroupByRobot` | 向群聊发送消息 |
| `recallGroupMessageByRobot` | 撤回群消息 |
| `batchSendMessageToUsersByRobot` | 批量发送消息给用户 |
| `batchRecallToUsersMessageByRobot` | 批量撤回消息 |
| `sendMessageToGroupByCustomRobot` | 使用自定义机器人发送消息 |

### 配置文件位置

- **环境变量**: `~/.praxis-skills/data/knowledge-radar/dingtalk-mcp.env`
- **Claude Code MCP**: `~/.claude/mcp.json`
- **启动脚本**: `~/.praxis-skills/data/knowledge-radar/start_dingtalk_mcp.sh`

### 测试连接

```bash
# 加载环境变量
source ~/.praxis-skills/data/knowledge-radar/dingtalk-mcp.env

# 启动 MCP server 测试
npx dingtalk-mcp
```

### 使用示例

在 Claude Code 中，你可以直接说：
- "搜索钉钉用户张三"
- "给张三发消息说明天开会"
- "在群里通知一下项目进度"

---

## 2. 钉钉 Webhook 配置（简单，只发消息）

### 获取钉钉机器人 Webhook

1. 打开钉钉群 → 群设置 → 智能群助手
2. 添加机器人 → 自定义
3. 设置机器人名称（如"知识雷达"）
4. 安全设置选择"加签"（推荐）
5. 复制 Webhook URL 和 Secret

### 配置命令

```bash
# 方式1：命令行参数配置（推荐）
python3 scripts/dingtalk_notify.py setup \
  --webhook "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN" \
  --secret "SECxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 方式2：交互式配置（需要终端）
python3 scripts/dingtalk_notify.py setup

# 测试配置
python3 scripts/dingtalk_notify.py test
```

### 手动发送消息

```bash
python3 scripts/dingtalk_notify.py send \
  --title "测试标题" \
  --content "测试内容"
```

## 2. 定期扫描配置

### 设置 Cron Job

```bash
# 交互式设置（推荐）
bash scripts/setup_cron.sh

# 或手动编辑 crontab
crontab -e
```

### Cron 示例

```bash
# 每周一早上 9 点（已配置）
0 9 * * 1 /Users/alex/Documents/myCode/skills/praxis-skills/skills/praxis-knowledge-radar/scripts/scheduled_sync.sh

# 每天早上 9 点
0 9 * * * /Users/alex/Documents/myCode/skills/praxis-skills/skills/praxis-knowledge-radar/scripts/scheduled_sync.sh

# 每周一和周四早上 9 点
0 9 * * 1,4 /Users/alex/Documents/myCode/skills/praxis-skills/skills/praxis-knowledge-radar/scripts/scheduled_sync.sh
```

### 手动运行

```bash
# 运行定期同步脚本
bash scripts/scheduled_sync.sh

# 或直接运行 sync-all
python3 scripts/radar_enhanced.py sync-all --notify
```

### 查看日志

```bash
# 查看最新日志
tail -f ~/.praxis-skills/data/knowledge-radar/logs/sync-*.log

# 查看特定日期的日志
cat ~/.praxis-skills/data/knowledge-radar/logs/sync-20260627.log
```

### 配置钉钉通知

#### 方式 1: Webhook（推荐，简单）

```bash
# 运行配置脚本
bash scripts/setup_notification.sh

# 选择 Webhook 方式，输入群机器人的 Webhook URL
```

#### 方式 2: MCP（需要 openConversationId）

```bash
# 运行配置脚本
bash scripts/setup_notification.sh

# 选择 MCP 方式，输入群的 openConversationId
```

#### 配置文件

通知配置保存在：`~/.praxis-skills/data/knowledge-radar/notification-config.json`

```json
{
  "enabled": true,
  "method": "webhook",
  "webhook": {
    "url": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
    "secret": "YOUR_SECRET"
  },
  "mcp": {
    "openConversationId": ""
  }
}
```

#### 测试通知

```bash
# 运行定期同步脚本（会发送通知）
bash scripts/scheduled_sync.sh

# 查看日志确认通知是否发送成功
tail -20 ~/.praxis-skills/data/knowledge-radar/logs/sync-*.log
```

## 3. 使用流程

### 首次配置

```bash
# 1. 配置钉钉通知
python3 scripts/dingtalk_notify.py setup --webhook "YOUR_WEBHOOK" --secret "YOUR_SECRET"

# 2. 测试钉钉配置
python3 scripts/dingtalk_notify.py test

# 3. 设置定期扫描
bash scripts/setup_cron.sh
```

### 日常使用

```bash
# 手动检查单个任务
python3 scripts/radar_enhanced.py sync skill-creation

# 手动批量检查（不发通知）
python3 scripts/radar_enhanced.py sync-all

# 手动批量检查（发通知）
python3 scripts/radar_enhanced.py sync-all --notify
```

### 自动流程

设置 cron job 后，系统会：
1. 每周一早上 9 点自动运行 sync-all
2. 检查所有 learned 任务的 reference 更新
3. 发送钉钉消息通知扫描结果
4. 记录日志到 `~/.praxis-skills/data/knowledge-radar/logs/`

## 4. 配置文件位置

- **钉钉配置**: `~/.praxis-skills/data/knowledge-radar/dingtalk-config.json`
- **任务数据**: `~/.praxis-skills/data/knowledge-radar/tasks.jsonl`
- **同步日志**: `~/.praxis-skills/data/knowledge-radar/logs/sync-*.log`

## 5. 故障排除

### 钉钉消息发送失败

```bash
# 检查配置
python3 scripts/dingtalk_notify.py test

# 查看配置文件
cat ~/.praxis-skills/data/knowledge-radar/dingtalk-config.json
```

### Cron Job 不执行

```bash
# 查看 crontab
crontab -l

# 手动运行测试
bash scripts/scheduled_sync.sh

# 查看系统日志
grep CRON /var/log/system.log
```

### 权限问题

```bash
# 确保脚本有执行权限
chmod +x scripts/scheduled_sync.sh
chmod +x scripts/setup_cron.sh
```
