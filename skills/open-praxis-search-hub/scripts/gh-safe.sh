#!/bin/bash
# GitHub 安全 wrapper - 过滤危险的 GitHub 搜索命令
# 只允许使用 Core API (5000/hr)，禁止 Search API (30/min)

set -e

GH_CMD="/opt/homebrew/bin/gh"

# 检查是否是危险的搜索命令
is_dangerous() {
    local cmd="$1"
    if [[ "$cmd" == *"search repos"* ]] || [[ "$cmd" == *"search code"* ]]; then
        return 0  # 危险
    fi
    return 1  # 安全
}

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: gh-safe.sh <gh-command> [args...]"
    echo ""
    echo "安全命令 (Core API, 5000/hr):"
    echo "  gh-safe.sh repo view owner/repo"
    echo "  gh-safe.sh api /repos/owner/repo"
    echo "  gh-safe.sh issue list -R owner/repo"
    echo ""
    echo "危险命令 (Search API, 30/min, 已禁用):"
    echo "  gh-safe.sh search repos \"query\"  ❌"
    echo "  gh-safe.sh search code \"query\"   ❌"
    exit 1
fi

# 检查是否是危险命令
if is_dangerous "$*"; then
    echo "❌ 错误: GitHub Search API 已禁用，防止触发风控"
    echo ""
    echo "请使用安全的替代方案："
    echo "  1. safe-search gh-lookup owner/repo  (Core API, 5000/hr)"
    echo "  2. safe-search gh-suggest \"query\"   (零 API)"
    echo "  3. safe-search web \"query\"          (Exa 搜索)"
    exit 1
fi

# 执行安全的命令
exec "$GH_CMD" "$@"
