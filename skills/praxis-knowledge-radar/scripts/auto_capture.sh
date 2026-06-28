#!/bin/bash
# 自动捕获钉钉群消息并入库
# 用法: bash auto_capture.sh [--notify]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/.praxis-skills/data/knowledge-radar/logs"
LOG_FILE="$LOG_DIR/auto-capture-$(date +%Y%m%d-%H%M%S).log"
NOTIFY=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --notify)
            NOTIFY=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

mkdir -p "$LOG_DIR"

echo "========================================" | tee -a "$LOG_FILE"
echo "自动捕获开始: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 增量拉取消息（从上次拉取时间开始）
echo "" | tee -a "$LOG_FILE"
echo "📥 拉取钉钉群消息..." | tee -a "$LOG_FILE"
cd "$SCRIPT_DIR"
python3 dingtalk_fetch.py --incremental --since 24h 2>&1 | tee -a "$LOG_FILE"

# 获取统计信息
TOTAL=$(tail -3 "$LOG_FILE" | grep -o '入库完成: [0-9]*' | grep -o '[0-9]*' || echo "0")
echo "" | tee -a "$LOG_FILE"
echo "✅ 本次捕获: $TOTAL 个 URL" | tee -a "$LOG_FILE"

# 钉钉通知
if [ "$NOTIFY" = true ] && [ "$TOTAL" -gt 0 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "📤 发送钉钉通知..." | tee -a "$LOG_FILE"
    python3 dingtalk_notify.py send \
        --title "📡 知识雷达自动捕获" \
        --content "✅ 本次自动捕获 $TOTAL 个 URL，请查看任务列表。" \
        2>&1 | tee -a "$LOG_FILE" || true
fi

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "自动捕获完成: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 清理超过 30 天的日志
find "$LOG_DIR" -name "auto-capture-*.log" -mtime +30 -delete 2>/dev/null || true

# 清理超过 7 天的报告（保留最近 7 天）
REPORT_DIR="$HOME/.praxis-skills/data/knowledge-radar/reports"
find "$REPORT_DIR" -name "report-*.html" -mtime +7 -delete 2>/dev/null || true
find "$REPORT_DIR" -name "report-*.md" -mtime +7 -delete 2>/dev/null || true

# 限制报告目录大小（最多 10MB）
REPORT_SIZE=$(du -sm "$REPORT_DIR" 2>/dev/null | cut -f1)
if [ "$REPORT_SIZE" -gt 10 ]; then
    echo "⚠️  报告目录超过 10MB，清理旧报告..." | tee -a "$LOG_FILE"
    # 删除最旧的报告，直到大小小于 5MB
    while [ "$(du -sm "$REPORT_DIR" 2>/dev/null | cut -f1)" -gt 5 ]; do
        OLDEST=$(ls -t "$REPORT_DIR"/report-*.html 2>/dev/null | tail -1)
        if [ -n "$OLDEST" ]; then
            rm -f "$OLDEST"
        else
            break
        fi
    done
fi
