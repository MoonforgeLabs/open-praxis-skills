#!/bin/bash
# 检查底层工具的 GitHub 仓库更新

echo "=== 底层工具更新检查 ==="
echo ""

# 检查 agent-reach 更新
echo "1. agent-reach:"
REPO="Panniantong/Agent-Reach"
if command -v gh &> /dev/null; then
    INFO=$(gh api repos/$REPO --jq '.pushed_at, .stargazers_count' 2>/dev/null)
    if [ $? -eq 0 ]; then
        PUSHED_AT=$(echo "$INFO" | sed -n '1p')
        STARS=$(echo "$INFO" | sed -n '2p')
        echo "   ⭐ Stars: $STARS"
        echo "   📅 最后更新: $PUSHED_AT"
    else
        echo "   ⚠️ 无法获取信息"
    fi
else
    echo "   ❌ 需要 gh CLI"
fi

# 检查 last30days 更新
echo ""
echo "2. last30days:"
REPO="anthropics/last30days"
if command -v gh &> /dev/null; then
    INFO=$(gh api repos/$REPO --jq '.pushed_at, .stargazers_count' 2>/dev/null)
    if [ $? -eq 0 ]; then
        PUSHED_AT=$(echo "$INFO" | sed -n '1p')
        STARS=$(echo "$INFO" | sed -n '2p')
        echo "   ⭐ Stars: $STARS"
        echo "   📅 最后更新: $PUSHED_AT"
    else
        echo "   ⚠️ 无法获取信息"
    fi
else
    echo "   ❌ 需要 gh CLI"
fi

# 检查 anysearch-skill 更新
echo ""
echo "3. anysearch-skill:"
REPO="anthropics/anysearch-skill"
if command -v gh &> /dev/null; then
    INFO=$(gh api repos/$REPO --jq '.pushed_at, .stargazers_count' 2>/dev/null)
    if [ $? -eq 0 ]; then
        PUSHED_AT=$(echo "$INFO" | sed -n '1p')
        STARS=$(echo "$INFO" | sed -n '2p')
        echo "   ⭐ Stars: $STARS"
        echo "   📅 最后更新: $PUSHED_AT"
    else
        echo "   ⚠️ 无法获取信息"
    fi
else
    echo "   ❌ 需要 gh CLI"
fi

# 检查 praxis-search-hub 更新
echo ""
echo "4. praxis-search-hub (本地):"
LOCAL_PATH="$HOME/Documents/myCode/skills/praxis-skills/skills/praxis-search-hub"
if [ -d "$LOCAL_PATH" ]; then
    cd "$LOCAL_PATH"
    LAST_COMMIT=$(git log -1 --format="%ai %s" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "   📅 最后提交: $LAST_COMMIT"
    else
        echo "   ⚠️ 无法获取 git 信息"
    fi
else
    echo "   ❌ 目录不存在"
fi
