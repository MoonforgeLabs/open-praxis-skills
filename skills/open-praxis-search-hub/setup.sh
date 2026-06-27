#!/usr/bin/env bash
# praxis-search-hub — Tiered Install Script
# 与 CAPABILITY_TIERS 对齐：CORE / ENHANCED / ADVANCED
#
# 用法:
#   bash setup.sh                  # 安装全部 (CORE + ENHANCED + ADVANCED)
#   bash setup.sh --tier CORE      # 只装核心层
#   bash setup.sh --tier ENHANCED  # 装到增强层
#   bash setup.sh --tier ADVANCED  # 装全部
#   bash setup.sh --check          # 只检查不安装
#   bash setup.sh --check --tier CORE
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
CHECK_ONLY=false
TARGET_TIER="ADVANCED"

while [[ $# -gt 0 ]]; do
    case $1 in
        --check)  CHECK_ONLY=true; shift ;;
        --tier)   TARGET_TIER="$2"; shift 2 ;;
        *)        shift ;;
    esac
done

TIER_ORDER=("CORE" "ENHANCED" "ADVANCED")
tier_index() { for i in "${!TIER_ORDER[@]}"; do [[ "${TIER_ORDER[$i]}" == "$1" ]] && echo "$i" && return; done; echo 99; }
TARGET_IDX=$(tier_index "$TARGET_TIER")

log_ok()   { echo -e "  ${GREEN}✅${NC} $1"; }
log_fail() { echo -e "  ${RED}❌${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}⚠️${NC}  $1"; }
log_info() { echo -e "  ${BLUE}📦${NC} $1"; }
log_skip() { echo -e "  ${YELLOW}⏭${NC}  $1"; }

should_run() { [[ $(tier_index "$1") -le "$TARGET_IDX" ]]; }

try_install() {
    local name="$1" check="$2" install="$3"
    if eval "$check" &>/dev/null; then log_ok "$name"; return 0; fi
    if $CHECK_ONLY; then log_fail "$name 未安装"; return 1; fi
    log_info "安装 $name..."
    if eval "$install" 2>/dev/null; then log_ok "$name 安装成功"; return 0; fi
    log_fail "$name 安装失败"; return 1
}

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   praxis-search-hub Setup                        ║"
echo "║   Target tier: $TARGET_TIER                              ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

MISSING=0

# ━━━ CORE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if should_run "CORE"; then
    echo "── 🟢 CORE (零依赖，开源版保留) ──"

    # Python
    if command -v python3 &>/dev/null; then
        PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
            log_ok "python3 $PY_VER"
        else
            log_fail "python3 $PY_VER (需要 3.10+)"; exit 1
        fi
    else
        log_fail "python3 未安装"; exit 1
    fi

    # fcntl
    python3 -c "import fcntl" 2>/dev/null && log_ok "fcntl (限流)" || log_warn "fcntl 不可用 (Windows)，限流降级"

    # 网络连通性
    python3 -c "
import urllib.request
tests = [('GitHub API', 'https://api.github.com/zen'), ('npm', 'https://registry.npmjs.org/-/v1/search?text=test&size=1')]
for name, url in tests:
    try:
        urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'test'}), timeout=8)
        print(f'  ✅ {name} 连通')
    except: print(f'  ⚠️  {name} 不通')
" 2>/dev/null || true
fi

# ━━━ ENHANCED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if should_run "ENHANCED"; then
    echo ""
    echo "── 🟡 ENHANCED (可选 CLI，缺失自动降级) ──"

    # gh CLI
    try_install "gh CLI" "command -v gh" \
        "(brew install gh 2>/dev/null || (curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg 2>/dev/null && echo 'deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main' | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null && sudo apt update && sudo apt install -y gh))" || MISSING=$((MISSING+1))

    # Node.js
    if command -v node &>/dev/null; then
        log_ok "Node.js $(node --version)"
    else
        log_fail "Node.js 未安装 (mcporter/opencli 需要)"
        $CHECK_ONLY || echo "     macOS: brew install node | Linux: sudo apt install nodejs npm"
        MISSING=$((MISSING+1))
    fi

    # npm tools
    if command -v node &>/dev/null; then
        try_install "mcporter" "command -v mcporter" "npm install -g mcporter" || MISSING=$((MISSING+1))
        try_install "opencli" "command -v opencli" "npm install -g opencli" || MISSING=$((MISSING+1))
    fi

    # pipx + agent-reach
    try_install "pipx" "command -v pipx" \
        "(python3 -m pip install --user pipx 2>/dev/null || brew install pipx 2>/dev/null)" || true

    if command -v pipx &>/dev/null; then
        try_install "agent-reach" "command -v agent-reach" "pipx install agent-reach" || MISSING=$((MISSING+1))
        if command -v bili &>/dev/null; then log_ok "bili"; else log_warn "bili 未找到"; fi
    else
        log_fail "pipx 不可用，跳过 agent-reach"; MISSING=$((MISSING+1))
    fi

    # skill 文件
    [ -f "$HOME/.agents/skills/agent-reach/SKILL.md" ] && log_ok "agent-reach skill" || { log_warn "agent-reach skill 缺失"; MISSING=$((MISSING+1)); }
fi

# ━━━ ADVANCED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if should_run "ADVANCED"; then
    echo ""
    echo "── 🔴 ADVANCED (外部 skill，开源版移除) ──"

    if [ -f "$HOME/.agents/skills/last30days/SKILL.md" ]; then
        log_ok "last30days skill"
        [ -f "$HOME/.agents/skills/last30days/scripts/last30days.py" ] && log_ok "last30days.py CLI" || log_warn "last30days.py 未找到"
    else
        log_warn "last30days 未安装"
        if ! $CHECK_ONLY; then
            echo "     安装: git clone https://github.com/mvanhorn/last30days-skill ~/.agents/skills/last30days"
        fi
        MISSING=$((MISSING+1))
    fi

    # 环境变量
    [ -n "${GITHUB_TOKEN:-}" ] && log_ok "GITHUB_TOKEN" || log_warn "GITHUB_TOKEN 未设置 (GitHub 认证搜索不可用)"
    [ -n "${EXA_API_KEY:-}" ] && log_ok "EXA_API_KEY" || log_warn "EXA_API_KEY 未设置 (Exa 需要 mcporter 配置)"
fi

# ━━━ Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "══════════════════════════════════════════════════"
if [ "$MISSING" -eq 0 ]; then
    echo -e "  ${GREEN}🎉 $TARGET_TIER 层全部依赖已就绪！${NC}"
else
    echo -e "  ${YELLOW}⚠️  $MISSING 个依赖缺失${NC}"
fi
echo ""
echo "  验证: python3 scripts/safe_search.py doctor"
echo "  后端: python3 scripts/safe_search.py backends"
echo "  层级: python3 scripts/safe_search.py tiers"
echo ""
