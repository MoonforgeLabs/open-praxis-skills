# App Automation Patterns

Source: ComposioHQ/awesome-claude-skills

## Architecture Layers

```
MCP for access → Tools for actions → Skills for behavior
```

- **MCP**: Provides connection to external services (auth, API calls)
- **Tools**: Individual operations (create_issue, send_message, list_files)
- **Skills**: Workflow orchestration — which tools to call, in what order, with what guardrails

## Pattern A: MCP-Backed Automation

For skills that connect to external services via MCP:

```yaml
---
name: slack-automation
description: Use when managing Slack channels, messages, or workflows
---
# Slack Automation

## Available Tools
- `slack_send_message` — Send a message to a channel
- `slack_list_channels` — List available channels
- `slack_create_channel` — Create a new channel

## Workflows
### Send a message
1. Call `slack_list_channels` to find the target channel
2. Call `slack_send_message` with channel_id and text
3. Confirm delivery

## Pitfalls
- Channel names are case-sensitive
- Bot must be invited to the channel first
```

**Key rules**:
- Skill contains NO scripts — pure instruction about tool usage
- Auth handled by MCP layer (OAuth, API key in MCP config)
- Skill defines workflow; MCP provides connection

## Pattern B: Self-Contained Scripts

For skills that bundle their own logic:

```
skill-name/
├── SKILL.md              # Workflow instructions
├── scripts/              # Executable scripts (Python/Bash)
├── references/           # Domain knowledge
└── assets/               # Templates, examples
```

**Key rules**:
- Scripts are **black boxes** — called, not read into context
- SKILL.md references scripts by name: `Run python3 scripts/analyze.py`
- Scripts handle their own error messages and output format
- Large scripts should NOT be read into context (pollutes context window)

## Script-as-Black-Box Pattern

When a skill bundles large scripts:

```markdown
## Usage
Run the analysis script:
\`\`\`bash
python3 scripts/analyze.py --input data.csv --output report.md
\`\`\`

The script handles:
- Input validation
- Error reporting
- Output formatting

Do NOT read the script into context — it's too large. Call it directly.
```

## Multi-Phase Workflow Pattern

For complex skills with iterative steps:

```
Phase 1: Outline → User confirms
Phase 2: Research → Gather evidence
Phase 3: Draft → Generate output
Phase 4: Review → User feedback
Phase 5: Polish → Final output
```

Each phase:
- Has a clear completion criterion
- Produces a tangible artifact (outline, draft, report)
- Can be interrupted and resumed
- User confirms before proceeding to next

## Quality Signals

### High Quality

- Real use case with concrete scenarios
- Specific trigger conditions ("When to Use" section)
- Step-by-step procedural instructions with guardrails
- Concrete examples with actual prompts
- Common pitfalls documented with visual markers (✅/❌)
- Imperative writing style ("To accomplish X, do Y" not "You should do X")
- Scripts as black boxes, not read into context
- Progressive disclosure respected (SKILL.md < 5k tokens)
- Safety guardrails for destructive operations
- Attribution to original sources

### Low Quality (Red Flags)

- Vague descriptions ("helps you write better")
- No concrete examples or trigger conditions
- Everything crammed into SKILL.md instead of scripts/references
- No differentiation from what the agent already knows natively
- Theoretically interesting but no real-world usage evidence
- No "When NOT to use" section (risk of misuse)

## Skill Structure Template

```
---
name: <name>
description: <one sentence, includes when to trigger>
---
# Title

## When to Use This Skill
[Specific trigger scenarios]

## What This Skill Does
[1-2 sentences]

## How to Use
[Step-by-step instructions]

## Example
[Concrete User: "..." / Output: "..." examples]

## Tips / Common Pitfalls
[✅ Do this / ❌ Don't do this]
```
