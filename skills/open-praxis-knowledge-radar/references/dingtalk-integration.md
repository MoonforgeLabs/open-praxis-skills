# 钉钉集成详解

## 配置钉钉

```bash
# 交互式配置
python3 scripts/setup_dingtalk.py

# 直接传参
python3 scripts/setup_dingtalk.py --app-key YOUR_KEY --app-secret YOUR_SECRET

# 列出可用群
python3 scripts/setup_dingtalk.py --list-groups
```

配置文件：`~/.praxis-skills/data/knowledge-radar/dingtalk-config.json`

## 消息拉取

```bash
# 增量拉取（推荐）
python3 scripts/dingtalk_fetch.py --incremental

# 指定时间范围
python3 scripts/dingtalk_fetch.py --since 2h

# 干运行（只提取不入库）
python3 scripts/dingtalk_fetch.py --dry-run

# JSON 输出
python3 scripts/dingtalk_fetch.py --json
```

## 增量模式

增量模式记录上次拉取时间，下次从该时间点继续拉取，确保不遗漏消息。

状态文件：`~/.praxis-skills/data/knowledge-radar/fetch_state.json`

```json
{
  "last_fetch_time": "2026-06-27 19:04:22",
  "updated_at": "2026-06-27T19:04:22.811388+08:00"
}
```

## 去重机制

基于 URL 去重，已入库的 URL 不会重复入库。

- 精确匹配完整 URL
- 匹配基础 URL（去除查询参数）
- 实时更新已存在 URL 集合

## 摘要提取

自动从消息内容中提取标题和摘要：

1. 从 `[分享]` 前缀后提取标题
2. 从消息内容中提取摘要
3. 去除来源标识（如 "- 今日头条"）
4. 清理多余空白

## 群昵称

优先使用群昵称（memberGroupNick），其次使用成员昵称（memberNick）。

## 用户名脱敏

入库时对用户名进行脱敏处理：
- 保留最后一个字符
- 其余用 `*` 替换
- 示例：`尹德雨` → `**雨`
