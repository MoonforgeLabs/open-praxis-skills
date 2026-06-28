#!/bin/bash
# 钉钉 MCP 配置脚本

echo "🔧 钉钉 MCP 配置指南"
echo "=================================================="
echo ""
echo "📋 步骤 1: 创建钉钉开放平台应用"
echo "--------------------------------------------------"
echo "1. 访问: https://open-dev.dingtalk.com/"
echo "2. 登录你的钉钉账号"
echo "3. 点击「创建应用」→「企业内部应用」"
echo "4. 填写应用信息:"
echo "   - 应用名称: 知识雷达 (或你喜欢的名字)"
echo "   - 应用描述: 知识管理助手"
echo ""
echo "📋 步骤 2: 获取应用凭证"
echo "--------------------------------------------------"
echo "1. 在应用详情页，找到「凭证与基础信息」"
echo "2. 复制「AppKey」和「AppSecret」"
echo ""
echo "📋 步骤 3: 配置权限"
echo "--------------------------------------------------"
echo "1. 在应用详情页，点击「权限管理」"
echo "2. 添加以下权限:"
echo "   - 企业会话: 读取消息"
echo "   - 通讯录: 读取成员信息"
echo "   - 群会话: 读取群消息"
echo ""
echo "📋 步骤 4: 配置环境变量"
echo "--------------------------------------------------"
echo ""

# 创建 .env 文件
ENV_FILE="$HOME/.praxis-skills/data/knowledge-radar/dingtalk-mcp.env"

if [ -f "$ENV_FILE" ]; then
    echo "⚠️  已存在配置文件: $ENV_FILE"
    read -p "是否覆盖？(y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "取消配置"
        exit 0
    fi
fi

read -p "请输入 AppKey (Client_ID): " app_key
read -p "请输入 AppSecret (Client_Secret): " app_secret

if [ -z "$app_key" ] || [ -z "$app_secret" ]; then
    echo "❌ AppKey 和 AppSecret 不能为空"
    exit 1
fi

# 保存配置
cat > "$ENV_FILE" << EOF
# 钉钉 MCP 配置
DINGTALK_Client_ID=$app_key
DINGTALK_Client_Secret=$app_secret
EOF

echo ""
echo "✅ 配置已保存到: $ENV_FILE"
echo ""

# 测试配置
echo "📋 步骤 5: 测试连接"
echo "--------------------------------------------------"
echo "运行以下命令测试:"
echo ""
echo "  # 加载环境变量"
echo "  source $ENV_FILE"
echo ""
echo "  # 启动 MCP server 测试"
echo "  npx dingtalk-mcp"
echo ""

# 创建启动脚本
START_SCRIPT="$HOME/.praxis-skills/data/knowledge-radar/start_dingtalk_mcp.sh"
cat > "$START_SCRIPT" << 'EOF'
#!/bin/bash
# 启动钉钉 MCP Server

ENV_FILE="$HOME/.praxis-skills/data/knowledge-radar/dingtalk-mcp.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ 配置文件不存在: $ENV_FILE"
    echo "请先运行: bash scripts/setup_dingtalk_mcp.sh"
    exit 1
fi

# 加载环境变量
source "$ENV_FILE"

# 启动 MCP server
echo "🚀 启动钉钉 MCP Server..."
npx dingtalk-mcp
EOF

chmod +x "$START_SCRIPT"

echo "✅ 启动脚本已创建: $START_SCRIPT"
echo ""
echo "🎉 配置完成！"
echo ""
echo "下一步:"
echo "1. 测试连接: $START_SCRIPT"
echo "2. 在 Claude Code 中配置 MCP (可选)"
echo ""
