#!/bin/bash
# 配置钉钉通知

echo "🔧 配置钉钉通知"
echo "=================================================="
echo ""
echo "请选择通知方式："
echo "1) Webhook 方式（简单，只需群机器人 Webhook URL）"
echo "2) MCP 方式（需要群的 openConversationId）"
echo ""
read -p "请选择 (1/2): " choice

CONFIG_FILE="$HOME/.praxis-skills/data/knowledge-radar/notification-config.json"

case $choice in
    1)
        echo ""
        echo "📋 Webhook 方式配置"
        echo "--------------------------------------------------"
        echo "请在钉钉群中添加自定义机器人，获取 Webhook URL"
        echo ""
        read -p "请输入 Webhook URL: " webhook_url
        read -p "请输入 Secret（可选，直接回车跳过）: " webhook_secret

        if [ -z "$webhook_url" ]; then
            echo "❌ Webhook URL 不能为空"
            exit 1
        fi

        # 保存配置
        cat > "$CONFIG_FILE" <<EOF
{
  "enabled": true,
  "method": "webhook",
  "webhook": {
    "url": "$webhook_url",
    "secret": "$webhook_secret"
  },
  "mcp": {
    "openConversationId": ""
  }
}
EOF

        echo ""
        echo "✅ Webhook 配置已保存"
        ;;

    2)
        echo ""
        echo "📋 MCP 方式配置"
        echo "--------------------------------------------------"
        echo "需要获取群的 openConversationId"
        echo ""
        echo "获取方式："
        echo "1. 在钉钉群中发送一条消息"
        echo "2. 使用钉钉开放平台 API 获取群会话 ID"
        echo ""
        read -p "请输入群的 openConversationId: " open_conversation_id

        if [ -z "$open_conversation_id" ]; then
            echo "❌ openConversationId 不能为空"
            exit 1
        fi

        # 保存配置
        cat > "$CONFIG_FILE" <<EOF
{
  "enabled": true,
  "method": "mcp",
  "webhook": {
    "url": "",
    "secret": ""
  },
  "mcp": {
    "openConversationId": "$open_conversation_id"
  }
}
EOF

        echo ""
        echo "✅ MCP 配置已保存"
        ;;

    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "📋 配置文件: $CONFIG_FILE"
echo ""
echo "测试通知："
echo "  bash scripts/scheduled_sync.sh"
echo ""
