#!/bin/bash
# praxis-skill-forge 通用安装脚本
# 使用软连接方式安装 skill 到 Claude Code、Codex、OpenHuman

set -e

# 使用方法
if [ $# -eq 0 ]; then
    echo "使用方法: $0 <skill-name> [skill-dir]"
    echo ""
    echo "示例:"
    echo "  $0 praxis-ai-usage-stats"
    echo "  $0 praxis-diagram /path/to/skill/dir"
    exit 1
fi

SKILL_NAME="$1"
SKILL_DIR="${2:-}"

# 如果没有指定目录，尝试在 praxis-skills 仓库中查找
if [ -z "$SKILL_DIR" ]; then
    PRAXIS_SKILLS_DIR="${PRAXIS_SKILLS_DIR:-/Users/alex/Documents/myCode/skills/praxis-skills}"
    SKILL_DIR="$PRAXIS_SKILLS_DIR/skills/$SKILL_NAME"
fi

if [ ! -d "$SKILL_DIR" ]; then
    echo "❌ 错误: Skill 目录不存在: $SKILL_DIR"
    exit 1
fi

echo "📦 安装 skill: $SKILL_NAME"
echo "   源目录: $SKILL_DIR"
echo ""

# 安装到各个 runtime
RUNTIMES=(
    "claude:$HOME/.claude/skills"
    "codex:$HOME/.codex/skills"
    "openhuman:$HOME/.openhuman/skills"
)

for runtime_info in "${RUNTIMES[@]}"; do
    runtime_name="${runtime_info%%:*}"
    runtime_dir="${runtime_info#*:}"
    skill_link="$runtime_dir/$SKILL_NAME"

    # 首字母大写
    runtime_name_display="$(echo ${runtime_name} | awk '{print toupper(substr($0,1,1)) substr($0,2)}')"
    echo "=== $runtime_name_display ==="

    # 创建目录（如果不存在）
    mkdir -p "$runtime_dir"

    # 检查是否已存在
    if [ -L "$skill_link" ]; then
        # 检查软连接是否指向正确位置
        current_target=$(readlink "$skill_link")
        if [ "$current_target" = "$SKILL_DIR" ]; then
            echo "✅ 软连接已存在且指向正确: $skill_link"
        else
            echo "⚠️  软连接指向错误位置，重新创建..."
            rm "$skill_link"
            ln -s "$SKILL_DIR" "$skill_link"
            echo "✅ 已重新创建软连接: $skill_link"
        fi
    elif [ -d "$skill_link" ]; then
        echo "⚠️  目录已存在，删除并创建软连接..."
        rm -rf "$skill_link"
        ln -s "$SKILL_DIR" "$skill_link"
        echo "✅ 已创建软连接: $skill_link"
    else
        ln -s "$SKILL_DIR" "$skill_link"
        echo "✅ 已创建软连接: $skill_link"
    fi

    echo ""
done

# 设置执行权限
echo "=== 设置执行权限 ==="
if [ -d "$SKILL_DIR/scripts" ]; then
    chmod +x "$SKILL_DIR/scripts/"*.py 2>/dev/null || true
    chmod +x "$SKILL_DIR/scripts/"*.sh 2>/dev/null || true
    echo "✅ 已设置脚本执行权限"
else
    echo "⚠️  没有 scripts 目录"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "软连接位置:"
for runtime_info in "${RUNTIMES[@]}"; do
    runtime_name="${runtime_info%%:*}"
    runtime_dir="${runtime_info#*:}"
    skill_link="$runtime_dir/$SKILL_NAME"
    if [ -L "$skill_link" ]; then
        # 首字母大写
        runtime_name_display="$(echo ${runtime_name} | awk '{print toupper(substr($0,1,1)) substr($0,2)}')"
        echo "  $runtime_name_display: $skill_link -> $(readlink "$skill_link")"
    fi
done
