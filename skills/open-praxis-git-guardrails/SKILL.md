---
name: open-praxis-git-guardrails
description: Design or review guardrails that prevent dangerous git operations such as accidental push, reset --hard, clean, branch deletion, or force pushes in agentic coding workflows.
---

# Alex Git Guardrails

Use this to plan safe git behavior for Codex, Claude Code, or local automation.

## Guardrail Checklist

- Identify destructive commands to block or require confirmation.
- Decide which repos need stricter rules.
- Preserve emergency override path.
- Avoid committing secrets or local auth state.
- Test hooks or wrappers in dry-run mode first.

Inspired by `mattpocock/skills` `git-guardrails-claude-code` under MIT License.
