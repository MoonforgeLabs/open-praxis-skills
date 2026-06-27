#!/usr/bin/env bash
set -euo pipefail

# link-skills.sh — Symlink skills from repo to agent directories.
# Usage:
#   bash scripts/link-skills.sh                      # link all skills
#   bash scripts/link-skills.sh praxis-translate       # link single skill
#   bash scripts/link-skills.sh --dry-run            # preview only

REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
SKILL_NAME="${1:-}"
DRY_RUN=false

[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# Target directories
TARGETS=(
    "$HOME/.claude/skills"
    "$HOME/.codex/skills"
    "$HOME/.agents/skills"
)

link_skill() {
    local src="$1"
    local name
    name="$(basename "$src")"

    for dest_dir in "${TARGETS[@]}"; do
        [ -d "$dest_dir" ] || continue
        local link="$dest_dir/$name"

        if [ "$DRY_RUN" = true ]; then
            echo "  [dry-run] $name → $dest_dir"
            continue
        fi

        if [ -L "$link" ]; then
            local current
            current="$(readlink "$link")"
            if [ "$current" = "$src" ]; then
                echo "  ✅ $name → $dest_dir (already linked)"
                continue
            else
                rm "$link"
            fi
        elif [ -d "$link" ]; then
            echo "  ⚠️  $name exists at $dest_dir (not a symlink), skipping"
            continue
        fi

        ln -s "$src" "$link"
        echo "  ✅ $name → $dest_dir"
    done
}

echo "📦 Linking skills..."
echo ""

if [ -n "$SKILL_NAME" ] && [ "$SKILL_NAME" != "--dry-run" ]; then
    skill_dir="$REPO/skills/$SKILL_NAME"
    if [ ! -d "$skill_dir" ]; then
        echo "❌ Skill not found: $SKILL_NAME"
        echo "   Available: $(ls "$REPO/skills/" | tr '\n' ' ')"
        exit 1
    fi
    link_skill "$skill_dir"
else
    for skill_dir in "$REPO"/skills/*/; do
        [ -d "$skill_dir" ] || continue
        [ -f "$skill_dir/SKILL.md" ] || continue
        link_skill "$skill_dir"
    done
fi

echo ""
echo "🎉 Done!"
