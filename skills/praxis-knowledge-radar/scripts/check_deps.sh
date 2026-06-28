#!/bin/bash
# 检查底层工具的版本和更新

echo "=== 底层工具版本检查 ==="
echo ""

# 检查 agent-reach
echo "1. agent-reach:"
if command -v agent-reach &> /dev/null; then
    VERSION=$(agent-reach --version 2>&1 | head -1)
    echo "   ✅ 已安装: $VERSION"
else
    echo "   ❌ 未安装"
fi

# 检查 last30days
echo ""
echo "2. last30days:"
if [ -f "$HOME/.agents/skills/last30days/scripts/last30days.py" ]; then
    VERSION=$(grep -o "version.*" "$HOME/.agents/skills/last30days/SKILL.md" 2>/dev/null | head -1)
    echo "   ✅ 已安装: $VERSION"
else
    echo "   ❌ 未安装"
fi

# 检查 anysearch-skill
echo ""
echo "3. anysearch-skill:"
if [ -f "$HOME/.agents/skills/anysearch-skill/scripts/anysearch_cli.py" ]; then
    VERSION=$(grep -o "version.*" "$HOME/.agents/skills/anysearch-skill/SKILL.md" 2>/dev/null | head -1)
    echo "   ✅ 已安装: $VERSION"
else
    echo "   ❌ 未安装"
fi

# 检查 praxis-search-hub
echo ""
echo "4. praxis-search-hub:"
if [ -f "$HOME/Documents/myCode/skills/praxis-skills/skills/praxis-search-hub/scripts/safe_search.py" ]; then
    echo "   ✅ 已安装"
else
    echo "   ❌ 未安装"
fi

# 检查 mcporter
echo ""
echo "5. mcporter:"
if command -v mcporter &> /dev/null; then
    VERSION=$(mcporter --version 2>&1 | head -1)
    echo "   ✅ 已安装: $VERSION"
else
    echo "   ❌ 未安装"
fi

# 检查 opencli
echo ""
echo "6. opencli:"
if command -v opencli &> /dev/null; then
    VERSION=$(opencli --version 2>&1 | head -1)
    echo "   ✅ 已安装: $VERSION"
else
    echo "   ❌ 未安装"
fi

# 检查 bili
echo ""
echo "7. bili:"
if command -v bili &> /dev/null; then
    VERSION=$(bili --version 2>&1 | head -1)
    echo "   ✅ 已安装: $VERSION"
else
    echo "   ❌ 未安装"
fi

# 检查 gh
echo ""
echo "8. gh (GitHub CLI):"
if command -v gh &> /dev/null; then
    VERSION=$(gh --version 2>&1 | head -1)
    echo "   ✅ 已安装: $VERSION"
else
    echo "   ❌ 未安装"
fi
