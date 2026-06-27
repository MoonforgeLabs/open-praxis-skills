# Hook Patterns

Source: hesreallyhim/awesome-claude-code

## What Hooks Are

Hooks are scripts that run at specific points in Claude Code's agent lifecycle: PreToolUse (before a tool runs) and PostToolUse (after a tool runs). They can approve, block, modify, or react to tool calls.

## Hook Categories

### Safety & Guard

| Pattern | What it does | Trigger |
|---------|-------------|---------|
| AST command approval | Auto-approve safe commands, prompt for dangerous ones | PreToolUse: Bash |
| TDD Guard | Block file writes that violate TDD discipline | PreToolUse: Write/Edit |
| Prompt injection scanner | Detect injection attacks, secret leaks, data exfiltration | PostToolUse: all tools |

### Code Quality

| Pattern | What it does | Trigger |
|---------|-------------|---------|
| Type check on write | Run tsc/pyright after file writes | PostToolUse: Write |
| Lint auto-fix | Run ESLint --fix on modified files | PostToolUse: Write |
| Format on save | Run Prettier on modified files | PostToolUse: Write |

### Communication

| Pattern | What it does | Trigger |
|---------|-------------|---------|
| Desktop notification | Alert when task completes or input needed | PostToolUse: various |
| Sub-agent communication | Enable agents to message each other | PostToolUse: Agent |

## Design Rules

1. **Safe defaults**: Hook should fail open (allow) if it errors, not fail closed (block)
2. **Explicit disable**: Provide a clear way to disable the hook
3. **Context-aware**: Read the tool input/output, don't just react to the tool name
4. **Document side effects**: If the hook writes files, runs commands, or modifies state, document it
5. **Performance**: Use caching (SHA256 config hash) to avoid re-validating unchanged configs

## Implementation Pattern

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 <skill_dir>/scripts/lint_check.py",
            "async": false
          }
        ]
      }
    ]
  }
}
```

## Performance Optimization

TypeScript Quality Hooks pattern: cache config hash, skip validation if unchanged:

```python
import hashlib
config_hash = hashlib.sha256(config_content.encode()).hexdigest()
if config_hash == last_hash:
    return  # skip, <5ms
```
