#!/bin/bash
# 设置 cron job 定期同步

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/scheduled_sync.sh"

echo "🔧 设置定期同步 cron job"
echo "=" * 50

# 检查是否已存在
if crontab -l 2>/dev/null | grep -q "scheduled_sync.sh"; then
    echo "⚠️  已存在定期同步任务："
    crontab -l | grep "scheduled_sync.sh"
    echo ""
    read -p "是否更新？(y/n): " update
    if [ "$update" != "y" ]; then
        echo "取消更新"
        exit 0
    fi
    # 删除旧任务
    crontab -l | grep -v "scheduled_sync.sh" | crontab -
fi

# 显示选项
echo ""
echo "请选择同步频率："
echo "1) 每周一早上 9 点（推荐）"
echo "2) 每天早上 9 点"
echo "3) 每周一和周四早上 9 点"
echo "4) 自定义"
echo ""
read -p "请选择 (1-4): " choice

case $choice in
    1)
        CRON="0 9 * * 1"
        DESC="每周一早上 9 点"
        ;;
    2)
        CRON="0 9 * * *"
        DESC="每天早上 9 点"
        ;;
    3)
        CRON="0 9 * * 1,4"
        DESC="每周一和周四早上 9 点"
        ;;
    4)
        read -p "请输入 cron 表达式: " CRON
        DESC="自定义: $CRON"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

# 添加到 crontab
(crontab -l 2>/dev/null; echo "$CRON $SYNC_SCRIPT # 知识雷达定期同步 - $DESC") | crontab -

echo ""
echo "✅ Cron job 已设置"
echo "   频率: $DESC"
echo "   脚本: $SYNC_SCRIPT"
echo ""
echo "📋 当前 crontab："
crontab -l | grep "scheduled_sync.sh"
echo ""
echo "💡 手动测试: $SYNC_SCRIPT"
echo "📝 查看日志: tail -f ~/.praxis-skills/data/knowledge-radar/logs/sync-*.log"
