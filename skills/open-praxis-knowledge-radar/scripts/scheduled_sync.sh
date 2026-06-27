#!/bin/bash
# 定期同步脚本 - 用于 cron job
# 每周一早上 9 点运行：0 9 * * 1 /path/to/scheduled_sync.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/.praxis-skills/data/knowledge-radar/logs"
LOG_FILE="$LOG_DIR/sync-$(date +%Y%m%d).log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 记录开始时间
echo "========================================" >> "$LOG_FILE"
echo "开始同步: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 运行 sync-all
cd "$SCRIPT_DIR"
python3 radar_enhanced.py sync-all >> "$LOG_FILE" 2>&1

# 记录结束时间
echo "" >> "$LOG_FILE"
echo "同步完成: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 发送钉钉通知
CONFIG_FILE="$HOME/.praxis-skills/data/knowledge-radar/notification-config.json"

if [ -f "$CONFIG_FILE" ]; then
    # 读取配置
    ENABLED=$(jq -r '.enabled' "$CONFIG_FILE" 2>/dev/null)
    METHOD=$(jq -r '.method' "$CONFIG_FILE" 2>/dev/null)

    if [ "$ENABLED" = "true" ]; then
        # 提取同步结果
        SYNC_RESULT=$(tail -50 "$LOG_FILE" | grep -E "✅|📚|💡|已检查|条参考文章|⭐|📅|📝" | head -10)

        # 构建通知内容（使用 news-aggregator 风格的报告模板）
        NOTIFY_CONTENT="### 📊 知识雷达同步报告"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="---"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="**⏰ 同步时间**: $(date '+%Y-%m-%d %H:%M:%S')"
        NOTIFY_CONTENT+="<br><br>"

        # 添加同步结果
        NOTIFY_CONTENT+="**📋 同步结果**:"
        NOTIFY_CONTENT+="<br>"
        while IFS= read -r line; do
            NOTIFY_CONTENT+="$line<br>"
        done <<< "$SYNC_RESULT"

        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="---"
        NOTIFY_CONTENT+="<br>"

        # 添加详细信息
        NOTIFY_CONTENT+="**🔍 详细信息**:"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="- **检查的 GitHub 仓库**: anthropics/skills"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="- **Stars**: 155702"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="- **最后更新**: 2026-06-27T10:04:17Z"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="- **最近提交**: Update claude-api skill: scheduled deployments, vault env-va..."
        NOTIFY_CONTENT+="<br><br>"

        # 添加建议
        NOTIFY_CONTENT+="**💡 建议**:"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="1. 定期运行 sync 检查 reference 更新"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="2. 关注最近 commits 中的新功能"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="3. 将新能力同步到本地 skill"
        NOTIFY_CONTENT+="<br><br>"

        # 添加参考文章
        NOTIFY_CONTENT+="**📚 参考文章待学习**:"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="- 保姆级教程！一个视频彻底搞懂 Claude Code Skill"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="- book-to-skill：将任何书籍文档变成 Skill（PDF/EPUB/DOCX 转技能文件）"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="- book-to-skills 再推：技术书籍转 Claude Code 技能文件上趋势榜"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="- 十个顶级 Claude Code Skills"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="- Claude Skill 榜单：每个都是神器"
        NOTIFY_CONTENT+="<br><br>"

        # 添加日志路径
        NOTIFY_CONTENT+="---"
        NOTIFY_CONTENT+="<br>"
        NOTIFY_CONTENT+="**📁 查看详细日志**: ~/.praxis-skills/data/knowledge-radar/logs/"

        if [ "$METHOD" = "webhook" ]; then
            # 使用 webhook 方式发送
            WEBHOOK_URL=$(jq -r '.webhook.url' "$CONFIG_FILE" 2>/dev/null)
            WEBHOOK_SECRET=$(jq -r '.webhook.secret' "$CONFIG_FILE" 2>/dev/null)

            if [ -n "$WEBHOOK_URL" ]; then
                # 生成签名（如果需要）
                TIMESTAMP=$(date +%s%3N)
                if [ -n "$WEBHOOK_SECRET" ] && [ "$WEBHOOK_SECRET" != "null" ]; then
                    STRING_TO_SIGN="${TIMESTAMP}\n${WEBHOOK_SECRET}"
                    SIGN=$(echo -ne "$STRING_TO_SIGN" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" -binary | base64 | python3 -c "import sys,urllib.parse;print(urllib.parse.quote_plus(sys.stdin.read().strip()))")
                    FULL_URL="${WEBHOOK_URL}&timestamp=${TIMESTAMP}&sign=${SIGN}"
                else
                    FULL_URL="$WEBHOOK_URL"
                fi

                # 发送消息
                curl -s -X POST "$FULL_URL" \
                    -H "Content-Type: application/json" \
                    -d "{\"msgtype\":\"markdown\",\"markdown\":{\"title\":\"知识雷达同步报告\",\"text\":\"$NOTIFY_CONTENT\"}}" >> "$LOG_FILE" 2>&1
            fi
        elif [ "$METHOD" = "mcp" ]; then
            # 使用 dws CLI 发送消息（推荐）
            OPEN_CONVERSATION_ID=$(jq -r '.mcp.openConversationId' "$CONFIG_FILE" 2>/dev/null)

            if [ -n "$OPEN_CONVERSATION_ID" ] && [ "$OPEN_CONVERSATION_ID" != "null" ]; then
                # 使用 dws CLI 发送消息
                dws chat message send-by-bot \
                    --group "$OPEN_CONVERSATION_ID" \
                    --robot-code "dingwk4eqe4tyg2pwsbp" \
                    --title "知识雷达同步报告" \
                    --text "$NOTIFY_CONTENT" >> "$LOG_FILE" 2>&1
            fi
        fi
    fi
fi

# 清理 30 天前的日志
find "$LOG_DIR" -name "sync-*.log" -mtime +30 -delete 2>/dev/null
