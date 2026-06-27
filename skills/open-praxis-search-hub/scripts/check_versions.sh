#!/bin/bash
# 检查底层工具版本

echo "=== 底层工具版本检查 ==="
echo ""

# 锁定版本
AGENT_REACH_LOCK="v1.5.0"
LAST30DAYS_LOCK="3.8.3"
ANYSEARCH_LOCK="2.1.0"
MCPORTER_LOCK="0.9.0"
OPENCLI_LOCK="1.8.4"
BILI_LOCK="0.6.2"

# 检查 agent-reach
echo "1. agent-reach (锁定: $AGENT_REACH_LOCK):"
if command -v agent-reach &> /dev/null; then
    CURRENT=$(agent-reach --version 2>&1 | grep -o "v[0-9.]*")
    if [ "$CURRENT" = "$AGENT_REACH_LOCK" ]; then
        echo "   ✅ 版本匹配: $CURRENT"
    else
        echo "   ⚠️ 版本不匹配: 当前 $CURRENT, 锁定 $AGENT_REACH_LOCK"
    fi
else
    echo "   ❌ 未安装"
fi

# 检查 last30days
echo ""
echo "2. last30days (锁定: $LAST30DAYS_LOCK):"
if [ -f "$HOME/.agents/skills/last30days/SKILL.md" ]; then
    CURRENT=$(grep 'version:' "$HOME/.agents/skills/last30days/SKILL.md" | head -1 | sed 's/.*"\([0-9.]*\)".*/\1/')
    if [ "$CURRENT" = "$LAST30DAYS_LOCK" ]; then
        echo "   ✅ 版本匹配: $CURRENT"
    else
        echo "   ⚠️ 版本不匹配: 当前 $CURRENT, 锁定 $LAST30DAYS_LOCK"
    fi
else
    echo "   ❌ 未安装"
fi

# 检查 anysearch-skill
echo ""
echo "3. anysearch-skill (锁定: $ANYSEARCH_LOCK):"
if [ -f "$HOME/.agents/skills/anysearch-skill/SKILL.md" ]; then
    CURRENT=$(grep "version:" "$HOME/.agents/skills/anysearch-skill/SKILL.md" | grep -o "[0-9.]*")
    if [ "$CURRENT" = "$ANYSEARCH_LOCK" ]; then
        echo "   ✅ 版本匹配: $CURRENT"
    else
        echo "   ⚠️ 版本不匹配: 当前 $CURRENT, 锁定 $ANYSEARCH_LOCK"
    fi
else
    echo "   ❌ 未安装"
fi

# 检查 mcporter
echo ""
echo "4. mcporter (锁定: $MCPORTER_LOCK):"
if command -v mcporter &> /dev/null; then
    CURRENT=$(mcporter --version 2>&1 | grep -o "[0-9.]*")
    if [ "$CURRENT" = "$MCPORTER_LOCK" ]; then
        echo "   ✅ 版本匹配: $CURRENT"
    else
        echo "   ⚠️ 版本不匹配: 当前 $CURRENT, 锁定 $MCPORTER_LOCK"
    fi
else
    echo "   ❌ 未安装"
fi

# 检查 opencli
echo ""
echo "5. opencli (锁定: $OPENCLI_LOCK):"
if command -v opencli &> /dev/null; then
    CURRENT=$(opencli --version 2>&1 | grep -o "[0-9.]*")
    if [ "$CURRENT" = "$OPENCLI_LOCK" ]; then
        echo "   ✅ 版本匹配: $CURRENT"
    else
        echo "   ⚠️ 版本不匹配: 当前 $CURRENT, 锁定 $OPENCLI_LOCK"
    fi
else
    echo "   ❌ 未安装"
fi

# 检查 bili
echo ""
echo "6. bili (锁定: $BILI_LOCK):"
if command -v bili &> /dev/null; then
    CURRENT=$(bili --version 2>&1 | grep -o "[0-9.]*")
    if [ "$CURRENT" = "$BILI_LOCK" ]; then
        echo "   ✅ 版本匹配: $CURRENT"
    else
        echo "   ⚠️ 版本不匹配: 当前 $CURRENT, 锁定 $BILI_LOCK"
    fi
else
    echo "   ❌ 未安装"
fi
