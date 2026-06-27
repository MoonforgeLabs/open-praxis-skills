#!/usr/bin/env bash
# praxis-skills → org-praxis-skills + open-praxis-skills 同步脚本
# 只同步 release-manifest.json 中 approved 的 skill
#
# 用法:
#   bash scripts/sync-repos.sh              # 同步全部（仅 approved）
#   bash scripts/sync-repos.sh --check      # 只检查不同步
#   bash scripts/sync-repos.sh --org        # 只同步 org
#   bash scripts/sync-repos.sh --open       # 只同步 open
#   bash scripts/sync-repos.sh --all        # 强制同步全部（危险！）
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

PRAXIS_SKILLS_DIR="/Users/alex/Documents/myCode/skills/praxis-skills"
ORG_DIR="/Users/alex/Documents/myCode/org/org-praxis-skills"
OPEN_DIR="/Users/alex/Documents/myCode/open/open-praxis-skills"
MANIFEST="$PRAXIS_SKILLS_DIR/release-manifest.json"

CHECK_ONLY=false
SYNC_ORG=true
SYNC_OPEN=true
SYNC_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --check) CHECK_ONLY=true; shift ;;
        --org)   SYNC_OPEN=false; shift ;;
        --open)  SYNC_ORG=false; shift ;;
        --all)   SYNC_ALL=true; shift ;;
        *)       shift ;;
    esac
done

# 获取 approved skills 列表
if [ "$SYNC_ALL" = true ]; then
    APPROVED_SKILLS=$(ls "$PRAXIS_SKILLS_DIR/skills/" | tr '\n' ' ')
    echo -e "${YELLOW}⚠️  强制同步全部 skill（忽略 manifest）${NC}"
else
    if [ ! -f "$MANIFEST" ]; then
        echo -e "${RED}❌ release-manifest.json 不存在${NC}"
        echo "   创建文件或使用 --all 强制同步"
        exit 1
    fi
    APPROVED_SKILLS=$(python3 -c "
import json
with open('$MANIFEST') as f:
    d = json.load(f)
for name in sorted(d.get('approved', {}).keys()):
    print(name)
")
    if [ -z "$APPROVED_SKILLS" ]; then
        echo -e "${YELLOW}⚠️  没有 approved 的 skill${NC}"
        exit 0
    fi
fi

ALEX_COMMIT=$(cd "$PRAXIS_SKILLS_DIR" && git log --oneline -1 2>/dev/null)
ALEX_SHORT=$(cd "$PRAXIS_SKILLS_DIR" && git log --format='%h' -1 2>/dev/null)

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   praxis-skills 仓库同步（仅 approved skills）         ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "  源: praxis-skills ($ALEX_SHORT)"
echo "  同步 skills:"
for s in $APPROVED_SKILLS; do
    echo "    → $s"
done
echo ""

sync_repo() {
    local name="$1" dir="$2" remote="$3"
    if [ ! -d "$dir" ]; then
        echo -e "  ${RED}✗${NC} $name 目录不存在: $dir"
        return 1
    fi

    echo -e "  ${BLUE}$name${NC}"

    if $CHECK_ONLY; then
        local target_short=$(cd "$dir" && git log --format='%h' -1 2>/dev/null)
        if [ "$ALEX_SHORT" = "$target_short" ]; then
            echo -e "    ${GREEN}✓ 已同步${NC}"
        else
            echo -e "    ${YELLOW}↑ 需要同步${NC}"
        fi
        return 0
    fi

    # 同步：只复制 approved 的 skill
    mkdir -p "$dir/skills"
    for skill in $APPROVED_SKILLS; do
        src="$PRAXIS_SKILLS_DIR/skills/$skill"
        dst="$dir/skills/$skill"
        if [ -d "$src" ]; then
            rsync -av --delete \
                --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
                --exclude='private/' --exclude='node_modules/' \
                "$src/" "$dst/" >/dev/null 2>&1
        fi
    done

    # 删除下游中不在 approved 列表的 skill
    for existing in "$dir/skills"/*/; do
        [ -d "$existing" ] || continue
        name=$(basename "$existing")
        found=false
        for skill in $APPROVED_SKILLS; do
            if [ "$name" = "$skill" ]; then found=true; break; fi
        done
        if [ "$found" = false ]; then
            echo -e "    ${YELLOW}删除未批准: $name${NC}"
            rm -rf "$existing"
        fi
    done

    # 同步公开文档
    cp "$PRAXIS_SKILLS_DIR/README.md" "$dir/" 2>/dev/null || true
    cp "$PRAXIS_SKILLS_DIR/DESIGN_PHILOSOPHY.md" "$dir/" 2>/dev/null || true
    cp "$PRAXIS_SKILLS_DIR/CONTRIBUTING.md" "$dir/" 2>/dev/null || true
    cp "$PRAXIS_SKILLS_DIR/package.json" "$dir/" 2>/dev/null || true
    cp "$PRAXIS_SKILLS_DIR/release-manifest.json" "$dir/" 2>/dev/null || true
    rsync -av --delete "$PRAXIS_SKILLS_DIR/docs/" "$dir/docs/" >/dev/null 2>&1

    # 提交
    cd "$dir"
    if git diff --quiet 2>/dev/null && [ -z "$(git status --porcelain)" ]; then
        echo -e "    ${GREEN}✓ 无变化${NC}"
    else
        git add -A
        git commit -m "sync: approved skills from praxis-skills $ALEX_SHORT

Skills: $(echo $APPROVED_SKILLS | tr '\n' ', ')

Co-Authored-By: Claude <noreply@anthropic.com>" 2>/dev/null

        if [ -n "$remote" ]; then
            git push "$remote" main 2>/dev/null && echo -e "    ${GREEN}✅ 已推送${NC}" || echo -e "    ${YELLOW}⚠️  推送失败${NC}"
        fi
    fi
}

if $SYNC_ORG; then
    sync_repo "org-praxis-skills (小米内部)" "$ORG_DIR" "origin"
    echo ""
fi

if $SYNC_OPEN; then
    sync_repo "open-praxis-skills (开源)" "$OPEN_DIR" "origin"
fi

echo ""
echo "══════════════════════════════════════════════════════"
echo ""
