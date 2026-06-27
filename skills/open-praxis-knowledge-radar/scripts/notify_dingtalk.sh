#!/bin/bash
# 钉钉通知脚本 - 使用 MCP 发送消息

# 加载环境变量
source "$HOME/.praxis-skills/data/knowledge-radar/dingtalk-mcp.env"

# 获取参数
TITLE="${1:-知识雷达通知}"
CONTENT="${2:-测试消息}"

# 构建 JSON 请求
REQUEST=$(cat <<EOF
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "sendMessageToGroupByCustomRobot",
    "arguments": {
      "markdown": {
        "title": "$TITLE",
        "text": "$CONTENT"
      }
    }
  }
}
EOF
)

# 发送消息
echo "$REQUEST" | npx dingtalk-mcp 2>/dev/null | grep -v "found mcp\|Loaded\|Tools:\|No token\|DingTalk\|连接方式\|启动"
