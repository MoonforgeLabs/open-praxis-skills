#!/bin/bash
# 设置自动捕获 cron job
# 用法: bash setup_auto_capture.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_CAPTURE_SCRIPT="$SCRIPT_DIR/auto_capture.sh"

echo "========================================="
echo "📡 设置知识雷达自动捕获"
echo "========================================="
echo ""
echo "自动捕获将定期运行，从钉钉群拉取消息并入库。"
echo ""

# 检查是否已存在
if crontab -l 2>/dev/null | grep -q "auto_capture.sh"; then
    echo "⚠️  已存在自动捕获 cron job："
    crontab -l | grep "auto_capture.sh"
    echo ""
    read -p "是否更新？(y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 0
    fi
    # 移除旧的
    crontab -l | grep -v "auto_capture.sh" | crontab -
fi

echo "请选择捕获频率："
echo "  1) 每 30 分钟（推荐）"
echo "  2) 每 1 小时"
echo "  3) 每 2 小时"
echo "  4) 每天早上 9 点"
echo ""
read -p "请选择 (1-4): " choice

case $choice in
    1)
        CRON="*/30 * * * *"
        DESC="每 30 分钟"
        ;;
    2)
        CRON="0 * * * *"
        DESC="每 1 小时"
        ;;
    3)
        CRON="0 */2 * * *"
        DESC="每 2 小时"
        ;;
    4)
        CRON="0 9 * * *"
        DESC="每天早上 9 点"
        ;;
    *)
        echo "无效选择，使用默认：每 30 分钟"
        CRON="*/30 * * * *"
        DESC="每 30 分钟"
        ;;
esac

echo ""
read -p "是否启用钉钉通知？(y/n): " -n 1 -r
echo ""
NOTIFY_FLAG=""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    NOTIFY_FLAG=" --notify"
fi

# 添加 cron job
(crontab -l 2>/dev/null; echo "$CRON /bin/bash $AUTO_CAPTURE_SCRIPT$NOTIFY_FLAG >> $HOME/.praxis-skills/data/knowledge-radar/logs/cron.log 2>&1") | crontab -

echo ""
echo "✅ 自动捕获已设置！"
echo ""
echo "📋 配置详情："
echo "   频率: $DESC"
echo "   脚本: $AUTO_CAPTURE_SCRIPT"
echo "   通知: $(if [ -n "$NOTIFY_FLAG" ]; then echo "已启用"; else echo "未启用"; fi)"
echo "   日志: ~/.praxis-skills/data/knowledge-radar/logs/"
echo ""
echo "🔧 管理命令："
echo "   查看 cron: crontab -l"
echo "   编辑 cron: crontab -e"
echo "   删除 cron: crontab -l | grep -v auto_capture.sh | crontab -"
echo ""
echo "🧪 测试运行："
echo "   bash $AUTO_CAPTURE_SCRIPT --notify"
