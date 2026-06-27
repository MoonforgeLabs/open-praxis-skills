#!/usr/bin/env bash
# praxis-search-hub — Dependency Update Script
# 检查并更新所有外部依赖
#
# 用法:
#   bash update-deps.sh            # 检查 + 更新全部
#   bash update-deps.sh --check    # 只检查不更新
#   bash update-deps.sh --tier ENHANCED  # 只更新指定层级
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
CHECK_ONLY=false
TARGET_TIER="ADVANCED"

while [[ $# -gt 0 ]]; do
    case $1 in
        --check) CHECK_ONLY=true; shift ;;
        --tier)  TARGET_TIER="$2"; shift 2 ;;
        *)       shift ;;
    esac
done

TIER_ORDER=("CORE" "ENHANCED" "ADVANCED")
tier_index() { for i in "${!TIER_ORDER[@]}"; do [[ "${TIER_ORDER[$i]}" == "$1" ]] && echo "$i" && return; done; echo 99; }
TARGET_IDX=$(tier_index "$TARGET_TIER")
should_run() { [[ $(tier_index "$1") -le "$TARGET_IDX" ]]; }

UPDATED=0
SKIPPED=0
ERRORS=0

check_update() {
    local name="$1" tier="$2" current="$3" latest="$4" update_cmd="$5"
    if ! should_run "$tier"; then return; fi

    if [ "$current" = "$latest" ] || [ -z "$latest" ] || [ "$latest" = "?" ]; then
        echo -e "  ${GREEN}✓${NC} $name $current (最新)"
        SKIPPED=$((SKIPPED+1))
    else
        echo -e "  ${YELLOW}↑${NC} $name $current → $latest"
        if ! $CHECK_ONLY; then
            echo -e "    ${BLUE}更新中...${NC}"
            if eval "$update_cmd" 2>/dev/null; then
                echo -e "    ${GREEN}✅ 更新成功${NC}"
                UPDATED=$((UPDATED+1))
            else
                echo -e "    ${RED}❌ 更新失败${NC}"
                ERRORS=$((ERRORS+1))
            fi
        fi
    fi
}

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   praxis-search-hub 依赖更新                      ║"
echo "║   模式: $(if $CHECK_ONLY; then echo '只检查'; else echo '检查 + 更新'; fi)                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ━━━ CORE ━━━
if should_run "CORE"; then
    echo "── 🟢 CORE ──"
    PY_CUR=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>/dev/null || echo "?")
    echo -e "  ${GREEN}✓${NC} python3 $PY_CUR (系统管理)"
    echo ""
fi

# ━━━ ENHANCED ━━━
if should_run "ENHANCED"; then
    echo "── 🟡 ENHANCED ──"

    # gh CLI
    GH_CUR=$(gh --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "?")
    GH_LATEST=$(brew info gh 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "?")
    check_update "gh CLI" "ENHANCED" "$GH_CUR" "$GH_LATEST" "brew upgrade gh"

    # mcporter
    MCP_CUR=$(mcporter --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "?")
    MCP_LATEST=$(npm info mcporter version 2>/dev/null || echo "?")
    check_update "mcporter" "ENHANCED" "$MCP_CUR" "$MCP_LATEST" "npm update -g mcporter"

    # opencli
    OCLI_CUR=$(opencli --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "?")
    OCLI_LATEST=$(npm info opencli version 2>/dev/null || echo "?")
    check_update "opencli" "ENHANCED" "$OCLI_CUR" "$OCLI_LATEST" "npm update -g opencli"

    # agent-reach (CLI via pipx, skill via skills.sh)
    AR_CUR=$(agent-reach --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "?")
    AR_LATEST=$(pip index versions agent-reach 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "?")
    check_update "agent-reach CLI" "ENHANCED" "$AR_CUR" "$AR_LATEST" "pipx upgrade agent-reach"
    # agent-reach skill files
    AR_SKILL_DIR="$HOME/.agents/skills/agent-reach"
    if [ -d "$AR_SKILL_DIR" ] && ! $CHECK_ONLY; then
        echo -e "    ${BLUE}更新 agent-reach skill files...${NC}"
        npx skills update agent-reach -y 2>/dev/null && echo -e "    ${GREEN}✅ skill 更新成功${NC}" || echo -e "    ${YELLOW}⚠️  skill 更新跳过${NC}"
    fi
    echo ""
fi

# ━━━ ADVANCED ━━━
if should_run "ADVANCED"; then
    echo "── 🔴 ADVANCED ──"

    # last30days (skills.sh managed)
    L30_DIR="$HOME/.agents/skills/last30days"
    if [ -d "$L30_DIR" ]; then
        L30_VER=$(grep 'version:' "$L30_DIR/SKILL.md" 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "?")
        L30_LATEST=$(gh api repos/mvanhorn/last30days-skill/releases/latest --jq '.tag_name' 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "?")
        if [ "$L30_VER" = "$L30_LATEST" ] || [ "$L30_LATEST" = "?" ]; then
            echo -e "  ${GREEN}✓${NC} last30days $L30_VER (最新)"
        else
            echo -e "  ${YELLOW}↑${NC} last30days $L30_VER → $L30_LATEST"
            if ! $CHECK_ONLY; then
                echo -e "    ${BLUE}通过 skills.sh 更新...${NC}"
                if npx skills update last30days -y 2>/dev/null; then
                    echo -e "    ${GREEN}✅ 更新成功${NC}"
                    UPDATED=$((UPDATED+1))
                else
                    echo -e "    ${RED}❌ 更新失败${NC}"
                    ERRORS=$((ERRORS+1))
                fi
            fi
        fi
    else
        echo -e "  ${RED}✗${NC} last30days 未安装"
    fi

    # praxis-search-hub 自身
    SAFE_DIR="$(cd "$(dirname "$0")" && pwd)"
    if [ -d "$SAFE_DIR/../../.git" ]; then
        SAFE_CUR=$(cd "$SAFE_DIR/../.." && git log --oneline -1 2>/dev/null | cut -c1-8 || echo "?")
        echo -e "  ${GREEN}✓${NC} praxis-search-hub $SAFE_CUR (本地)"
    fi
    echo ""
fi

# ━━━ Summary ━━━
echo "══════════════════════════════════════════════════"
echo -e "  更新: ${GREEN}$UPDATED${NC}  跳过: $SKIPPED  失败: ${RED}$ERRORS${NC}"
echo ""
