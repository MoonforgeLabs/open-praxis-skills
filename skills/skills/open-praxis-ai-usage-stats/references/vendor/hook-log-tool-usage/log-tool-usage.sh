#!/bin/bash
# PreToolUse hook: log Skill/Agent/Workflow/MCP calls to unified tool-usage.log
# TSV format: timestamp  type  name  project  args

LOG="$HOME/.claude/tool-usage.log"
payload=$(cat)

tool_name=$(jq -r '.tool_name // ""' <<< "$payload")
project=$(jq -r '.session_cwd // ""' <<< "$payload" | xargs basename 2>/dev/null || echo "unknown")

case "$tool_name" in
  Skill)
    type="skill"
    name=$(jq -r '.tool_input.skill // ""' <<< "$payload")
    args=$(jq -r '.tool_input.args // ""' <<< "$payload" | cut -c1-80)
    ;;
  Agent)
    type="agent"
    name=$(jq -r '.tool_input.subagent_type // .tool_input.description // ""' <<< "$payload")
    args=$(jq -r '.tool_input.prompt // ""' <<< "$payload" | cut -c1-80)
    ;;
  Workflow)
    type="workflow"
    name=$(jq -r '.tool_input.name // .tool_input.title // "inline"' <<< "$payload")
    args=$(jq -r '.tool_input.description // ""' <<< "$payload" | cut -c1-80)
    ;;
  mcp__*)
    type="mcp"
    name="${tool_name#mcp__}"
    args=$(jq -r '.tool_input | to_entries[:2] | map(.key+"="+(.value|tostring)[:30]) | join(" ")' <<< "$payload" 2>/dev/null)
    ;;
  *)
    exit 0
    ;;
esac

printf '%s\t%s\t%s\t%s\t%s\n' "$(date +%Y-%m-%dT%H:%M:%S)" "$type" "$name" "$project" "$args" >> "$LOG"
