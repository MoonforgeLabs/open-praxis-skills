#!/usr/bin/env bash
set -euo pipefail

# bump-version.sh — Sync version across all declaration files.
# Usage:
#   bash scripts/bump-version.sh <skill-dir> <new-version>
#   bash scripts/bump-version.sh skills/praxis-translate 1.2.0
#   bash scripts/bump-version.sh --check skills/praxis-translate  # check for drift

REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
CHECK_ONLY=false

[[ "${1:-}" == "--check" ]] && CHECK_ONLY=true && shift

SKILL_DIR="${1:-}"
NEW_VERSION="${2:-}"

if [ -z "$SKILL_DIR" ]; then
    echo "Usage: bash bump-version.sh <skill-dir> <new-version>"
    echo "       bash bump-version.sh --check <skill-dir>"
    exit 1
fi

SKILL_DIR="$REPO/$SKILL_DIR"
SKILL_NAME="$(basename "$SKILL_DIR")"

if [ ! -d "$SKILL_DIR" ]; then
    echo "❌ Skill directory not found: $SKILL_DIR"
    exit 1
fi

# Files that may contain version declarations
VERSION_FILES=(
    "$SKILL_DIR/SKILL.md"
    "$SKILL_DIR/README.md"
    "$SKILL_DIR/references/vendor-manifest.yaml"
)

# Extract current versions
echo "=== Version Check: $SKILL_NAME ==="
echo ""

ALL_VERSIONS=""
for f in "${VERSION_FILES[@]}"; do
    [ -f "$f" ] || continue
    versions=$(grep -oE 'version:\s*[0-9]+\.[0-9]+\.[0-9]+' "$f" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | sort -u || true)
    if [ -n "$versions" ]; then
        echo "$(basename "$f"): $versions"
        ALL_VERSIONS="$ALL_VERSIONS
$versions"
    fi
done

# Check for drift
UNIQUE_VERSIONS=$(echo "$ALL_VERSIONS" | sort -u | grep -v '^$' || true)
VERSION_COUNT=$(echo "$UNIQUE_VERSIONS" | wc -l | tr -d ' ')

if [ "$VERSION_COUNT" -gt 1 ]; then
    echo ""
    echo "⚠️  Version drift detected!"
    echo "   Versions found: $(echo "$UNIQUE_VERSIONS" | tr '\n' ', ')"
    if [ "$CHECK_ONLY" = true ]; then
        exit 1
    fi
fi

if [ "$CHECK_ONLY" = true ]; then
    if [ -z "$UNIQUE_VERSIONS" ]; then
        echo "No version declarations found."
    else
        echo "✅ No drift."
    fi
    exit 0
fi

# Bump version
if [ -z "$NEW_VERSION" ]; then
    echo "Error: specify new version (e.g., 1.2.0)"
    exit 1
fi

echo ""
echo "Bumping to $NEW_VERSION..."

for f in "${VERSION_FILES[@]}"; do
    [ -f "$f" ] || continue
    if grep -q 'version:' "$f" 2>/dev/null; then
        sed -i '' "s/version:\s*[0-9]\+\.[0-9]\+\.[0-9]\+/version: $NEW_VERSION/g" "$f"
        echo "  ✅ $(basename "$f")"
    fi
done

echo ""
echo "🎉 Version bumped to $NEW_VERSION"
