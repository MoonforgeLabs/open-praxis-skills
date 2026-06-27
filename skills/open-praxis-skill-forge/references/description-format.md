# Description Format (SDO)

Source: obra/superpowers writing-skills

## Core Rule

**Describe symptoms and trigger conditions. Do NOT describe the workflow.**

If the description summarizes what the skill does, the agent will follow the description as a shortcut and skip reading the full SKILL.md.

## Format

```yaml
description: Use when [specific triggering conditions and symptoms]
```

- Start with "Use when..." — focuses on trigger, not action
- Third person (injected into system prompt)
- Max 1,536 chars (Claude Code truncation); aim for 100-200 chars
- `name` uses only lowercase, digits, hyphens

## Examples

```yaml
# WRONG — summarizes workflow (agent will shortcut)
description: Use when executing plans - dispatches subagent per task with code review between tasks

# WRONG — too vague
description: For async testing

# RIGHT — only trigger conditions
description: Use when executing implementation plans with independent tasks in the current session

# RIGHT — specific symptoms + trigger
description: Use when tests have race conditions, timing dependencies, or pass/fail inconsistently
```

## The "before X" Pattern

Many superpowers skills add "before X" to specify timing:

- "before proposing fixes"
- "before writing implementation code"
- "before committing or creating PRs"
- "before implementing suggestions"

This ensures the skill fires at the right moment in the workflow.

## Real Examples from superpowers

| Skill | Description |
|-------|-------------|
| brainstorming | You MUST use this before any creative work... |
| systematic-debugging | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| verification-before-completion | Use when about to claim work is complete... requires running verification commands and confirming output before making any success claims |
| test-driven-development | Use when implementing any feature or bugfix, before writing implementation code |
| requesting-code-review | Use when completing tasks, implementing major features, or before merging |
| receiving-code-review | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable |

## Exception: Gate Skills

For mandatory prerequisite skills (like brainstorming), use stronger language:

```yaml
description: You MUST use this before any creative work - creating features, building components...
```

This overrides the "Use when" convention for skills that must always run first.
