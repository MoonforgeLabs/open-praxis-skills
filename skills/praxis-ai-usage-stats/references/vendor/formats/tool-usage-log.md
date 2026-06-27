# tool-usage.log 格式

来源: Claude Code PreToolUse hook (`log-tool-usage.sh`)

## 格式

TSV（Tab 分隔），每行一个事件：

```
timestamp\ttype\tname\tproject\targs
```

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| timestamp | ISO 8601 | 事件时间，如 `2026-06-25T14:30:00+08:00` |
| type | string | `skill` / `agent` / `tool` |
| name | string | 工具/技能/agent 名称 |
| project | string | 项目目录名（basename of session_cwd） |
| args | string | 截断到 80 字符的参数摘要 |

## 分类逻辑

```bash
case "$tool_name" in
  Skill)    type="skill";  name=tool_input.skill ;;
  Agent)    type="agent";  name=tool_input.subagent_type 或 description ;;
  *)        type="tool";   name=tool_name ;;
esac
```

## 兼容性注意

- 如 Claude Code 改变 hook payload 结构（tool_input 字段名），需更新 parser
- jq 依赖：hook 脚本使用 jq 解析 JSON
