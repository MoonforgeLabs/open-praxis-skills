#!/usr/bin/env bash
set -euo pipefail

# check-naming.sh — Verify naming consistency across 3 channels.
# Usage: bash scripts/check-naming.sh [myCode-dir]
# Default myCode-dir: three levels up from this script

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MYCODE_DIR="${1:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"

ALEX_SKILLS="$MYCODE_DIR/skills/praxis-skills/skills"
ORG_SKILLS="$MYCODE_DIR/org/skills"
PUBLIC_SKILLS="$MYCODE_DIR/public/skills"

echo "=== Three-Channel Naming Check ==="
echo ""

# Check 1: org skills have praxis-org- prefix
if [ -d "$ORG_SKILLS" ]; then
  echo "--- org/skills/ (expect praxis-org-* prefix) ---"
  for d in "$ORG_SKILLS"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    if [[ "$name" != praxis-org-* ]]; then
      echo "❌ $name — missing praxis-org- prefix"
    else
      echo "✅ $name"
    fi
  done
  echo ""
fi

# Check 2: public skills have praxis-pub- prefix
if [ -d "$PUBLIC_SKILLS" ]; then
  echo "--- public/skills/ (expect praxis-pub-* prefix) ---"
  for d in "$PUBLIC_SKILLS"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    if [[ "$name" != praxis-pub-* ]]; then
      echo "❌ $name — missing praxis-pub- prefix"
    else
      echo "✅ $name"
    fi
  done
  echo ""
fi

# Check 3: frontmatter name matches directory name
echo "--- Frontmatter name vs directory name ---"
for base_dir in "$ORG_SKILLS" "$PUBLIC_SKILLS"; do
  [ -d "$base_dir" ] || continue
  for d in "$base_dir"/*/; do
    [ -d "$d" ] || continue
    dir_name=$(basename "$d")
    skill_md="$d/SKILL.md"
    [ -f "$skill_md" ] || continue
    fm_name=$(awk '/^---$/{n++; next} n==1 && /^name:/{sub(/^name: */, ""); print; exit}' "$skill_md")
    if [ "$dir_name" != "$fm_name" ]; then
      echo "❌ $dir_name — frontmatter name='$fm_name' (mismatch)"
    else
      echo "✅ $dir_name"
    fi
  done
done
echo ""

# Check 4: cross-skill references match channel prefix
echo "--- Cross-skill reference consistency ---"
for base_dir in "$ORG_SKILLS" "$PUBLIC_SKILLS"; do
  [ -d "$base_dir" ] || continue
  channel="org"
  [[ "$base_dir" == *public* ]] && channel="pub"

  for d in "$base_dir"/*/; do
    [ -d "$d" ] || continue
    dir_name=$(basename "$d")
    skill_md="$d/SKILL.md"
    [ -f "$skill_md" ] || continue

    body=$(awk 'BEGIN{n=0} /^---$/{n++; if(n==2) next} n>=2{print}' "$skill_md" 2>/dev/null || true)

    # Find /praxis- references that don't match the channel
    wrong_refs=$(echo "$body" | grep -oE '/praxis-[a-z]+(-[a-z]+)*' 2>/dev/null \
      | grep -v "/praxis-${channel}-" \
      | sort -u || true)

    if [ -n "$wrong_refs" ]; then
      echo "⚠️  $dir_name — has refs to other channel:"
      echo "$wrong_refs" | sed 's/^/     /'
    else
      echo "✅ $dir_name — all refs use praxis-${channel}- prefix"
    fi
  done
done
echo ""

echo "=== Check complete ==="
