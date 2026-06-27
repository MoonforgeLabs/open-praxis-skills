#!/bin/bash
# 测试钉钉 MCP 功能

echo "🧪 测试钉钉 MCP 功能"
echo "=================================================="
echo ""

# 加载环境变量
ENV_FILE="$HOME/.praxis-skills/data/knowledge-radar/dingtalk-mcp.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ 配置文件不存在: $ENV_FILE"
    exit 1
fi

source "$ENV_FILE"

# 测试 1: 获取当前时间
echo "📋 测试 1: 获取当前时间"
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"currentDateTime","arguments":{}}}' | npx dingtalk-mcp 2>/dev/null | jq -r '.result.content[0].text' 2>/dev/null || echo "测试失败"
echo ""

# 测试 2: 搜索用户（测试用，搜索一个常见名字）
echo "📋 测试 2: 搜索钉钉用户"
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"searchUser","arguments":{"queryWord":"张三","size":3}}}' | npx dingtalk-mcp 2>/dev/null | jq -r '.result.content[0].text' 2>/dev/null || echo "测试失败"
echo ""

# 测试 3: 列出所有工具
echo "📋 测试 3: 列出所有可用工具"
echo '{"jsonrpc":"2.0","id":3,"method":"tools/list"}' | npx dingtalk-mcp 2>/dev/null | jq -r '.result.tools[].name' 2>/dev/null || echo "测试失败"
echo ""

echo "✅ 测试完成"
