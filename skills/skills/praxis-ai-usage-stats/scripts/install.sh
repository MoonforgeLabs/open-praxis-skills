#!/bin/bash
# praxis-ai-usage-stats 安装脚本
# 使用软连接方式安装到 Claude Code 和 Codex

set -e

SKILL_NAME="praxis-ai-usage-stats"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "📦 安装 $SKILL_NAME"
echo "   源目录: $SKILL_DIR"
echo ""

# Claude Code 安装
echo "=== Claude Code ==="
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
CLAUDE_SKILL_LINK="$CLAUDE_SKILLS_DIR/$SKILL_NAME"

if [ -L "$CLAUDE_SKILL_LINK" ]; then
    echo "✅ 软连接已存在: $CLAUDE_SKILL_LINK"
elif [ -d "$CLAUDE_SKILL_LINK" ]; then
    echo "⚠️  目录已存在，删除并创建软连接..."
    rm -rf "$CLAUDE_SKILL_LINK"
    ln -s "$SKILL_DIR" "$CLAUDE_SKILL_LINK"
    echo "✅ 已创建软连接: $CLAUDE_SKILL_LINK"
else
    mkdir -p "$CLAUDE_SKILLS_DIR"
    ln -s "$SKILL_DIR" "$CLAUDE_SKILL_LINK"
    echo "✅ 已创建软连接: $CLAUDE_SKILL_LINK"
fi

# Codex 安装
echo ""
echo "=== Codex ==="
CODEX_SKILLS_DIR="$HOME/.codex/skills"
CODEX_SKILL_LINK="$CODEX_SKILLS_DIR/$SKILL_NAME"

if [ -L "$CODEX_SKILL_LINK" ]; then
    echo "✅ 软连接已存在: $CODEX_SKILL_LINK"
elif [ -d "$CODEX_SKILL_LINK" ]; then
    echo "⚠️  目录已存在，删除并创建软连接..."
    rm -rf "$CODEX_SKILL_LINK"
    ln -s "$SKILL_DIR" "$CODEX_SKILL_LINK"
    echo "✅ 已创建软连接: $CODEX_SKILL_LINK"
else
    mkdir -p "$CODEX_SKILLS_DIR"
    ln -s "$SKILL_DIR" "$CODEX_SKILL_LINK"
    echo "✅ 已创建软连接: $CODEX_SKILL_LINK"
fi

# 创建 Codex hooks 配置
echo ""
echo "=== Codex Hooks 配置 ==="
CODEX_HOOKS_DIR="$CODEX_SKILL_LINK/hooks"
CODEX_HOOKS_FILE="$CODEX_HOOKS_DIR/hooks.json"

mkdir -p "$CODEX_HOOKS_DIR"

if [ ! -f "$CODEX_HOOKS_FILE" ]; then
    cat > "$CODEX_HOOKS_FILE" << 'EOF'
{
    "hooks": {
        "PostToolUse": [
            {
                "matcher": "Skill|Bash|Read|Write|Edit|Agent",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python3 /Users/alex/.codex/skills/praxis-ai-usage-stats/scripts/hook_collect.py || true",
                        "async": false
                    }
                ]
            }
        ]
    }
}
EOF
    echo "✅ 已创建 Codex hooks 配置: $CODEX_HOOKS_FILE"
else
    echo "✅ Codex hooks 配置已存在: $CODEX_HOOKS_FILE"
fi

# OpenHuman 安装
echo ""
echo "=== OpenHuman ==="
OPENHUMAN_SKILLS_DIR="$HOME/.openhuman/skills"
OPENHUMAN_SKILL_LINK="$OPENHUMAN_SKILLS_DIR/$SKILL_NAME"

if [ -L "$OPENHUMAN_SKILL_LINK" ]; then
    echo "✅ 软连接已存在: $OPENHUMAN_SKILL_LINK"
elif [ -d "$OPENHUMAN_SKILL_LINK" ]; then
    echo "⚠️  目录已存在，删除并创建软连接..."
    rm -rf "$OPENHUMAN_SKILL_LINK"
    ln -s "$SKILL_DIR" "$OPENHUMAN_SKILL_LINK"
    echo "✅ 已创建软连接: $OPENHUMAN_SKILL_LINK"
else
    mkdir -p "$OPENHUMAN_SKILLS_DIR"
    ln -s "$SKILL_DIR" "$OPENHUMAN_SKILL_LINK"
    echo "✅ 已创建软连接: $OPENHUMAN_SKILL_LINK"
fi

# 设置执行权限
echo ""
echo "=== 设置执行权限 ==="
chmod +x "$SKILL_DIR/scripts/"*.py
echo "✅ 已设置脚本执行权限"

# 验证安装
echo ""
echo "=== 验证安装 ==="
echo "Claude Code:"
ls -lh "$CLAUDE_SKILL_LINK"
echo ""
echo "Codex:"
ls -lh "$CODEX_SKILL_LINK"
echo ""
echo "OpenHuman:"
ls -lh "$OPENHUMAN_SKILL_LINK"
echo ""

echo "🎉 安装完成！"
echo ""
echo "使用方法："
echo "  python3 ~/.claude/skills/$SKILL_NAME/scripts/usage_stats.py today"
echo "  python3 ~/.claude/skills/$SKILL_NAME/scripts/generate_report.py --open"
echo "  python3 ~/.claude/skills/$SKILL_NAME/scripts/auto_cleanup.py"
