#!/usr/bin/env bash
set -euo pipefail

# audit-deps.sh — Scan all skills and produce a dependency readiness matrix.
# Usage: bash scripts/audit-deps.sh [skills-dir]
# Default skills-dir: skills/ in the repo root
#
# Scoring: only counts ACTUAL invocations (slash commands, path refs, install cmds).
# Mere mentions of "praxis-skills" in prose are excluded.

REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
SKILLS_DIR="${1:-$REPO/skills}"

if [ ! -d "$SKILLS_DIR" ]; then
  echo "Error: skills directory not found: $SKILLS_DIR" >&2
  exit 1
fi

printf "| %-35s | %-4s | %-14s | %-10s | %-14s | %-7s |\n" "Skill" "Tier" "Cross-skill" "CLI deps" "Private paths" "Ready?"
printf "|%s|\n" "---------------------------------------------------------------------------------------------------------"

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_md="$skill_dir/SKILL.md"
  [ -f "$skill_md" ] || continue

  skill_name="$(basename "$skill_dir")"

  # Extract body only (skip frontmatter between first pair of ---)
  body=$(awk 'BEGIN{n=0} /^---$/{n++; if(n==2) next} n>=2{print}' "$skill_md" 2>/dev/null || true)

  # Count ACTUAL cross-skill invocations:
  #   /praxis-xxx        (slash command invocation)
  #   ../praxis-xxx/     (relative path reference)
  #   praxis-xxx/SKILL.md (file path reference)
  # Exclude: bare mentions like "praxis-skills repository" or description text
  cross_skill=$(echo "$body" | grep -oE '/praxis-[a-z]+(-[a-z]+)*' 2>/dev/null \
    | sed 's|^/||' \
    | grep -v "^${skill_name}$" \
    | sort -u \
    | wc -l | tr -d ' ' || true)
  cross_skill=${cross_skill:-0}

  # Count external tool dependencies (install commands or prerequisite checks)
  cli_deps=$(echo "$body" | grep -cE 'brew install|pip install|cargo install|npm install|which [a-z]|command -v [a-z]' 2>/dev/null || true)
  cli_deps=${cli_deps:-0}
  cli_deps=$(echo "$cli_deps" | tr -d '[:space:]')

  # Count private/local path references
  private_paths=$(echo "$body" | grep -cE '/Users/alex|~/.claude/|PRAXIS_SKILLS_DIR|praxis-local-configs|praxis-learning[^-]' 2>/dev/null || true)
  private_paths=${private_paths:-0}
  private_paths=$(echo "$private_paths" | tr -d '[:space:]')

  # Determine tier
  if [ "$cross_skill" -eq 0 ] && [ "$cli_deps" -eq 0 ] && [ "$private_paths" -eq 0 ]; then
    tier="A"
    ready="✅"
  elif [ "$cross_skill" -eq 0 ] && [ "$private_paths" -eq 0 ]; then
    tier="B"
    ready="⚠️"
  elif [ "$private_paths" -gt 0 ] && [ "$cross_skill" -gt 3 ]; then
    tier="D"
    ready="❌"
  else
    tier="C"
    ready="⚠️"
  fi

  printf "| %-35s | %-4s | %-14s | %-10s | %-14s | %-7s |\n" \
    "$skill_name" "$tier" "${cross_skill} refs" "$cli_deps" "$private_paths" "$ready"
done
