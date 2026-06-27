#!/usr/bin/env bash
set -euo pipefail

# doctor.sh — Diagnose installed skills for drift, missing files, and health issues.
# Usage:
#   bash scripts/doctor.sh                    # check all installed skills
#   bash scripts/doctor.sh praxis-translate     # check single skill
#   bash scripts/doctor.sh --fix              # auto-fix what's possible

REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
FIX_MODE=false
SKILL_NAME="${1:-}"

[[ "${1:-}" == "--fix" ]] && FIX_MODE=true && SKILL_NAME="${2:-}"

# Installed skill directories to check
INSTALL_DIRS=(
    "$HOME/.claude/skills"
    "$HOME/.codex/skills"
    "$HOME/.agents/skills"
)

TOTAL_CHECKS=0
TOTAL_ISSUES=0

check_skill() {
    local name="$1"
    local installed_path="$2"
    local source_path="$REPO/skills/$name"

    local issues=0

    # Check 1: Source exists
    if [ ! -d "$source_path" ]; then
        echo "  ⚠️  Source not found: $source_path (orphaned install)"
        issues=$((issues + 1))
    fi

    # Check 2: SKILL.md exists
    if [ ! -f "$installed_path/SKILL.md" ]; then
        echo "  ❌ Missing SKILL.md"
        issues=$((issues + 1))
    fi

    # Check 3: Symlink target exists (if symlink)
    if [ -L "$installed_path" ]; then
        local target
        target="$(readlink "$installed_path")"
        if [ ! -e "$target" ]; then
            echo "  ❌ Broken symlink → $target"
            issues=$((issues + 1))
            if [ "$FIX_MODE" = true ] && [ -d "$source_path" ]; then
                rm "$installed_path"
                ln -s "$source_path" "$installed_path"
                echo "  🔧 Fixed: re-linked to $source_path"
            fi
        fi
    fi

    # Check 4: Content drift (if source exists)
    if [ -d "$source_path" ] && [ -f "$installed_path/SKILL.md" ] && [ -f "$source_path/SKILL.md" ]; then
        if [ -L "$installed_path" ]; then
            # Symlinked — no drift possible
            :
        else
            local installed_hash source_hash
            installed_hash=$(md5 -q "$installed_path/SKILL.md" 2>/dev/null || md5sum "$installed_path/SKILL.md" | cut -d' ' -f1)
            source_hash=$(md5 -q "$source_path/SKILL.md" 2>/dev/null || md5sum "$source_path/SKILL.md" | cut -d' ' -f1)
            if [ "$installed_hash" != "$source_hash" ]; then
                echo "  ⚠️  SKILL.md drift (installed ≠ source)"
                issues=$((issues + 1))
                if [ "$FIX_MODE" = true ]; then
                    cp "$source_path/SKILL.md" "$installed_path/SKILL.md"
                    echo "  🔧 Fixed: synced SKILL.md from source"
                fi
            fi
        fi
    fi

    # Check 5: Missing scripts
    if [ -d "$source_path/scripts" ]; then
        for script in "$source_path/scripts/"*.py "$source_path/scripts/"*.sh; do
            [ -f "$script" ] || continue
            local script_name
            script_name="$(basename "$script")"
            if [ ! -f "$installed_path/scripts/$script_name" ]; then
                echo "  ⚠️  Missing script: scripts/$script_name"
                issues=$((issues + 1))
                if [ "$FIX_MODE" = true ]; then
                    mkdir -p "$installed_path/scripts"
                    cp "$script" "$installed_path/scripts/"
                    echo "  🔧 Fixed: copied scripts/$script_name"
                fi
            fi
        done
    fi

    # Check 6: Missing references
    if [ -d "$source_path/references" ]; then
        local ref_count installed_ref_count
        ref_count=$(find "$source_path/references" -name "*.md" | wc -l | tr -d ' ')
        if [ -d "$installed_path/references" ]; then
            installed_ref_count=$(find "$installed_path/references" -name "*.md" | wc -l | tr -d ' ')
        else
            installed_ref_count=0
        fi
        if [ "$installed_ref_count" -lt "$ref_count" ]; then
            echo "  ⚠️  References incomplete: $installed_ref_count/$ref_count files"
            issues=$((issues + 1))
            if [ "$FIX_MODE" = true ]; then
                mkdir -p "$installed_path/references"
                cp -r "$source_path/references/"*.md "$installed_path/references/" 2>/dev/null || true
                echo "  🔧 Fixed: synced references"
            fi
        fi
    fi

    # Check 7: name field matches directory
    if [ -f "$installed_path/SKILL.md" ]; then
        local fm_name
        fm_name=$(grep '^name:' "$installed_path/SKILL.md" | head -1 | sed 's/name:\s*//')
        if [ "$fm_name" != "$name" ]; then
            echo "  ⚠️  name field '$fm_name' ≠ directory '$name'"
            issues=$((issues + 1))
        fi
    fi

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    TOTAL_ISSUES=$((TOTAL_ISSUES + issues))

    if [ "$issues" -eq 0 ]; then
        echo "  ✅ Healthy"
    fi
}

echo "=== Skill Doctor ==="
echo ""

if [ -n "$SKILL_NAME" ]; then
    # Check single skill
    found=false
    for install_dir in "${INSTALL_DIRS[@]}"; do
        if [ -d "$install_dir/$SKILL_NAME" ]; then
            echo "📦 $SKILL_NAME"
            check_skill "$SKILL_NAME" "$install_dir/$SKILL_NAME"
            found=true
            break
        fi
    done
    if [ "$found" = false ]; then
        echo "❌ $SKILL_NAME not found in any install directory"
    fi
else
    # Check all installed skills
    for install_dir in "${INSTALL_DIRS[@]}"; do
        [ -d "$install_dir" ] || continue
        for skill_dir in "$install_dir"/*/; do
            [ -d "$skill_dir" ] || continue
            name="$(basename "$skill_dir")"
            [[ "$name" == .* ]] && continue  # skip hidden
            echo "📦 $name"
            check_skill "$name" "$skill_dir"
        done
    done
fi

echo ""
echo "=== Summary ==="
echo "Checked: $TOTAL_CHECKS skills"
echo "Issues:  $TOTAL_ISSUES"

if [ "$TOTAL_ISSUES" -eq 0 ]; then
    echo "✅ All healthy"
else
    echo "⚠️  Run with --fix to auto-repair"
fi
