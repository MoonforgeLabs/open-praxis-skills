# 快速开始指南

5 分钟上手 praxis-knowledge-radar。

## 📋 前置条件

- Python 3.10+
- Claude Code 或其他 AI agent

## 🚀 快速安装

```bash
# 1. 克隆仓库（如果还没有）
git clone <your-repo-url>
cd praxis-skills/skills/praxis-knowledge-radar

# 2. 验证安装
python3 scripts/radar_enhanced.py status
```

看到主线任务列表表示安装成功。

---

## 📝 场景 1: 记录一个想法

**触发词**: "记录这个"、"加入雷达"、"reading list"

```bash
# 添加一个 URL
python3 scripts/radar.py add \
  --title "文章标题" \
  --area "ai-os" \
  --source url \
  --references "https://example.com/article" \
  --status inbox

# 添加一个想法（无 URL）
python3 scripts/radar.py add \
  --title "学习 Rust 所有权" \
  --area "code-understanding" \
  --source manual \
  --status inbox
```

**查看已添加的条目**:
```bash
python3 scripts/radar.py list --status inbox
```

---

## 📚 场景 2: 开始学习

**触发词**: "学习这个"、"开始学习"

```bash
# 1. 查看待学习的条目
python3 scripts/radar.py list --status inbox

# 2. 开始学习（更新状态）
python3 scripts/radar.py update --id <id> --status learning

# 3. 学完后记录笔记
python3 scripts/radar.py update --id <id> \
  --status learned \
  --notes "学到的关键点..."
```

**查看学习进度**:
```bash
python3 scripts/knowledge_ops.py progress
```

---

## 🔄 场景 3: 检查更新

**触发词**: "检查更新"、"同步"

```bash
# 检查单个任务的 reference 更新
python3 scripts/radar_enhanced.py sync skill-creation

# 批量检查所有 learned 任务
python3 scripts/radar_enhanced.py sync-all
```

---

## 📊 场景 4: 查看报告

**触发词**: "还有哪些没学"、"学习进度"

```bash
# 查看所有任务状态
python3 scripts/radar_enhanced.py status

# 查看总结报告
python3 scripts/radar_enhanced.py summary

# 查看学习进度
python3 scripts/knowledge_ops.py progress
```

---

## ⚙️ 场景 5: 配置通知插件（可选）

> **注意**: 通知功能是可选的。钉钉（DingTalk）相关配置仅适用于中国大陆地区用户，其他地区请根据自身需求替换为 Slack、飞书等通知渠道。

**触发词**: "配置通知"、"设置通知"

```bash
# 1. 配置通知 MCP（可选，钉钉示例）
#    如果不需要通知功能，可跳过此步骤
bash scripts/setup_dingtalk_mcp.sh

# 2. 配置通知目标
bash scripts/setup_notification.sh

# 3. 测试通知
bash scripts/scheduled_sync.sh
```

---

## 🔧 常用命令速查

### 知识捕获

```bash
# 添加 URL
python3 scripts/radar.py add --title "标题" --area "ai-os" --source url --references "https://..."

# 添加想法
python3 scripts/radar.py add --title "标题" --area "ai-os" --source manual

# 批量导入
python3 scripts/import-mapping.py
```

### 状态管理

```bash
# 查看所有任务
python3 scripts/radar.py list

# 按状态查看
python3 scripts/radar.py list --status inbox
python3 scripts/radar.py list --status learning
python3 scripts/radar.py list --status learned

# 更新状态
python3 scripts/radar.py update --id <id> --status learning
python3 scripts/radar.py update --id <id> --status learned --notes "笔记..."
```

### 主线任务

```bash
# 查看所有主线
python3 scripts/radar_enhanced.py status

# 查看特定主线
python3 scripts/radar_enhanced.py status skill-creation

# 查看下一步
python3 scripts/radar_enhanced.py next
```

### 知识运维

```bash
# 间隔重复
python3 scripts/knowledge_ops.py review

# 知识 Lint
python3 scripts/knowledge_ops.py lint

# 去重检查
python3 scripts/knowledge_ops.py dedup

# 学习进度
python3 scripts/knowledge_ops.py progress
```

### 能力同步

```bash
# 检查单个任务
python3 scripts/radar_enhanced.py sync <area>

# 批量检查
python3 scripts/radar_enhanced.py sync-all

# 带通知的批量检查（需先配置通知插件，见场景 5）
python3 scripts/radar_enhanced.py sync-all --notify
```

---

## 📁 数据存储

| 文件 | 用途 |
|------|------|
| `~/.praxis-skills/data/knowledge-radar/tasks.jsonl` | 所有任务数据 |
| `~/.praxis-skills/data/knowledge-radar/logs/` | 同步日志 |
| `~/.praxis-skills/data/knowledge-radar/notification-config.json` | 通知配置（可选） |
| `~/.praxis-skills/data/knowledge-radar/dingtalk-mcp.env` | 钉钉配置（可选，仅限中国大陆地区） |

---

## 🆘 常见问题

### Q: 如何查看所有任务？
```bash
python3 scripts/radar.py list
```

### Q: 如何删除任务？
```bash
python3 scripts/radar.py update --id <id> --status archived
```

### Q: 如何导出任务？
```bash
python3 scripts/radar.py export-md
```

### Q: 如何重置数据？
```bash
# 备份
cp ~/.praxis-skills/data/knowledge-radar/tasks.jsonl ~/.praxis-skills/data/knowledge-radar/tasks.jsonl.bak

# 清空
> ~/.praxis-skills/data/knowledge-radar/tasks.jsonl
```

---

## 📖 进阶使用

完成快速开始后，可以查看完整文档：

- **SKILL.md** - 完整功能说明
- **SETUP.md** - 详细配置指南
- **references/** - 参考资料

---

## 💡 提示

1. **先从 inbox 开始**: 所有新条目都先进入 inbox，然后逐步处理
2. **定期同步**: 每周运行一次 `sync-all` 检查更新
3. **使用触发词**: 在 Claude Code 中直接说触发词即可
4. **查看进度**: 使用 `progress` 命令查看学习完成度

---

**5 分钟上手完成！** 🎉
