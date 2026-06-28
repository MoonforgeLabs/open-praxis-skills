#!/bin/bash
# 知识雷达清理脚本 - 清理报告、日志和限制大小
# 用法: bash cleanup.sh [--dry-run]

set -e

DATA_DIR="$HOME/.praxis-skills/data/knowledge-radar"
REPORT_DIR="$DATA_DIR/reports"
LOG_DIR="$DATA_DIR/logs"
TASKS_FILE="$DATA_DIR/tasks.jsonl"

DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    echo "🔍 干运行模式（不实际删除）"
fi

echo "========================================="
echo "🧹 知识雷达清理工具"
echo "========================================="
echo ""

# 显示当前状态
echo "📊 当前存储状态："
echo "   整个目录: $(du -sh "$DATA_DIR" 2>/dev/null | cut -f1)"
echo "   任务文件: $(du -h "$TASKS_FILE" 2>/dev/null | cut -f1) ($(wc -l < "$TASKS_FILE" 2>/dev/null || echo 0) 条记录)"
echo "   报告目录: $(du -sh "$REPORT_DIR" 2>/dev/null | cut -f1) ($(ls "$REPORT_DIR"/report-* 2>/dev/null | wc -l | tr -d ' ') 个文件)"
echo "   日志目录: $(du -sh "$LOG_DIR" 2>/dev/null | cut -f1) ($(ls "$LOG_DIR"/*.log 2>/dev/null | wc -l | tr -d ' ') 个文件)"
echo ""

# 1. 清理超过 7 天的报告
echo "🗑️  清理超过 7 天的报告..."
OLD_REPORTS=$(find "$REPORT_DIR" -name "report-*" -mtime +7 2>/dev/null)
if [ -n "$OLD_REPORTS" ]; then
    echo "   找到 $(echo "$OLD_REPORTS" | wc -l | tr -d ' ') 个旧报告"
    if [ "$DRY_RUN" = false ]; then
        echo "$OLD_REPORTS" | xargs rm -f
        echo "   ✅ 已删除"
    else
        echo "   [dry-run] 将删除: $(echo "$OLD_REPORTS" | head -3)"
    fi
else
    echo "   ✅ 没有需要清理的报告"
fi

# 2. 清理超过 30 天的日志
echo ""
echo "🗑️  清理超过 30 天的日志..."
OLD_LOGS=$(find "$LOG_DIR" -name "*.log" -mtime +30 2>/dev/null)
if [ -n "$OLD_LOGS" ]; then
    echo "   找到 $(echo "$OLD_LOGS" | wc -l | tr -d ' ') 个旧日志"
    if [ "$DRY_RUN" = false ]; then
        echo "$OLD_LOGS" | xargs rm -f
        echo "   ✅ 已删除"
    else
        echo "   [dry-run] 将删除: $(echo "$OLD_LOGS" | head -3)"
    fi
else
    echo "   ✅ 没有需要清理的日志"
fi

# 3. 限制报告目录大小（最多 10MB）
echo ""
echo "📏 检查报告目录大小..."
REPORT_SIZE=$(du -sm "$REPORT_DIR" 2>/dev/null | cut -f1)
if [ "$REPORT_SIZE" -gt 10 ]; then
    echo "   ⚠️  报告目录 ${REPORT_SIZE}MB，超过 10MB 限制"
    if [ "$DRY_RUN" = false ]; then
        echo "   🔄 清理旧报告直到小于 5MB..."
        while [ "$(du -sm "$REPORT_DIR" 2>/dev/null | cut -f1)" -gt 5 ]; do
            OLDEST=$(ls -t "$REPORT_DIR"/report-*.html 2>/dev/null | tail -1)
            if [ -n "$OLDEST" ]; then
                rm -f "$OLDEST"
                echo "   删除: $(basename "$OLDEST")"
            else
                break
            fi
        done
        echo "   ✅ 清理完成，当前大小: $(du -sh "$REPORT_DIR" 2>/dev/null | cut -f1)"
    else
        echo "   [dry-run] 将清理旧报告直到小于 5MB"
    fi
else
    echo "   ✅ 报告目录 ${REPORT_SIZE}MB，未超过 10MB 限制"
fi

# 4. 限制日志目录大小（最多 5MB）
echo ""
echo "📏 检查日志目录大小..."
LOG_SIZE=$(du -sm "$LOG_DIR" 2>/dev/null | cut -f1)
if [ "$LOG_SIZE" -gt 5 ]; then
    echo "   ⚠️  日志目录 ${LOG_SIZE}MB，超过 5MB 限制"
    if [ "$DRY_RUN" = false ]; then
        echo "   🔄 清理旧日志直到小于 2MB..."
        while [ "$(du -sm "$LOG_DIR" 2>/dev/null | cut -f1)" -gt 2 ]; do
            OLDEST=$(ls -t "$LOG_DIR"/*.log 2>/dev/null | tail -1)
            if [ -n "$OLDEST" ]; then
                rm -f "$OLDEST"
                echo "   删除: $(basename "$OLDEST")"
            else
                break
            fi
        done
        echo "   ✅ 清理完成，当前大小: $(du -sh "$LOG_DIR" 2>/dev/null | cut -f1)"
    else
        echo "   [dry-run] 将清理旧日志直到小于 2MB"
    fi
else
    echo "   ✅ 日志目录 ${LOG_SIZE}MB，未超过 5MB 限制"
fi

# 5. 显示清理后的状态
echo ""
echo "========================================="
echo "📊 清理后存储状态："
echo "   整个目录: $(du -sh "$DATA_DIR" 2>/dev/null | cut -f1)"
echo "   任务文件: $(du -h "$TASKS_FILE" 2>/dev/null | cut -f1) ($(wc -l < "$TASKS_FILE" 2>/dev/null || echo 0) 条记录)"
echo "   报告目录: $(du -sh "$REPORT_DIR" 2>/dev/null | cut -f1) ($(ls "$REPORT_DIR"/report-* 2>/dev/null | wc -l | tr -d ' ') 个文件)"
echo "   日志目录: $(du -sh "$LOG_DIR" 2>/dev/null | cut -f1) ($(ls "$LOG_DIR"/*.log 2>/dev/null | wc -l | tr -d ' ') 个文件)"
echo "========================================="
