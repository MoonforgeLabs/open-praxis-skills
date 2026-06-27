# Resource Evaluation Checklist

Source: hesreallyhim/awesome-claude-code

## Purpose

Security and quality checklist for evaluating external skills, hooks, and agents before absorbing into praxis-skills.

## Security Checklist

### Hooks

- [ ] Does the hook auto-execute shell scripts? → HIGH RISK, inspect every command
- [ ] Does the hook write persistent local state files? → Check what and where
- [ ] Does the hook read state to control execution flow? → Verify no tampering risk
- [ ] Does the hook have implicit execution without user confirmation? → Should require explicit opt-in
- [ ] Is there a clear disable/cancel mechanism? → Must exist
- [ ] Declared permissions vs actual permissions — are they consistent?

### Scripts

- [ ] Does the script download external resources at runtime? → Check URLs, verify integrity
- [ ] Does the script send data to external services? → What data? Where?
- [ ] Does the script modify files outside its own directory? → Should be self-contained
- [ ] Does the script use `eval`, `exec`, or dynamic code execution? → HIGH RISK
- [ ] Does the script access sensitive directories (`~/.ssh/`, `~/.aws/`, env vars)?

### SKILL.md

- [ ] Does the description trigger on unexpected inputs? → Too broad
- [ ] Does the skill reference external URLs that could change? → Pin versions
- [ ] Does the skill require authentication tokens? → Where are they stored?

## Quality Checklist

- [ ] Does the skill have a clear completion criterion per step?
- [ ] Does the skill degrade gracefully when dependencies are missing?
- [ ] Is the skill self-contained (no deep cross-references)?
- [ ] Is the description using SDO format ("Use when...")?
- [ ] Are there tests or verification steps?

## Evaluation Report Format

```
## Evaluation: [skill-name]

### Security
- Hooks: [PASS/FAIL] — [details]
- Scripts: [PASS/FAIL] — [details]
- Data flow: [SAFE/CONCERN] — [details]

### Quality
- Self-contained: [YES/NO]
- Graceful degradation: [YES/NO]
- Description quality: [GOOD/WEAK/MISSING]

### Recommendation
[ADOPT / WATCH / SKIP] — [reason]
```
