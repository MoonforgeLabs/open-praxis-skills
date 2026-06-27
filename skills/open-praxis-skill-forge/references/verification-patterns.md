# Verification Patterns

Source: affaan-m/ECC

## Verification Loop

Six sequential phases, each must pass before the next:

| Phase | Check | Example Command |
|-------|-------|-----------------|
| 1. Build | Project builds without errors | `npm run build` |
| 2. Types | No type errors | `npx tsc --noEmit` or `pyright` |
| 3. Lint | No lint violations | `eslint .` |
| 4. Tests | All tests pass, coverage ≥ 80% | `pytest --cov` |
| 5. Security | No secrets or dangerous patterns | `grep -r "password\|secret\|console.log"` |
| 6. Diff Review | Every changed file reviewed | Manual review |

### Verification Report Format

```
VERIFICATION REPORT
==================
Build:     [PASS/FAIL]
Types:     [PASS/FAIL] (X errors)
Lint:      [PASS/FAIL] (X warnings)
Tests:     [PASS/FAIL] (X/Y passed, Z% coverage)
Security:  [PASS/FAIL] (X issues)
Diff:      [X files changed]
Overall:   [READY/NOT READY] for PR
```

## Agent Self-Debugging Loop

When an agent fails, follow this 4-phase recovery:

1. **Failure Capture**: error type, last tool call sequence, context pressure, environment assumptions
2. **Root-Cause Diagnosis**: match against known patterns:
   - Loop: agent repeating same action
   - Context overflow: too much in context window
   - Service unavailable: external API down
   - Quota exhaustion: rate limit hit
   - File stale: file changed since last read
   - Wrong hypothesis: initial assumption was wrong
3. **Contained Recovery**: smallest reversible action, NOT blind retry
4. **Introspection Report**: failure pattern, root cause, recovery action, evidence

## Workspace Governance

Track project state with a `WORKING-CONTEXT.md`:

- **Current Truth**: branch, version, counts
- **Current Constraints**: rules that apply right now
- **Active Queues**: what's in progress, by track
- **Latest Execution Notes**: dated entries — what changed, why, what test ran

**Rule**: Keep detailed only for current sprint, archive completed work.

## Anti-Anchoring: Council Pattern

For important decisions, launch multiple independent reviewers in parallel:

- Each gets ONLY the decision question and compact context (not full conversation)
- Each produces an independent judgment
- Synthesize — don't just pick the first answer

This prevents anchoring bias where later agents echo the first agent's conclusion.

## Autonomous Loop Monitoring

When running loop-based workflows (polling, batch processing, iterative refinement), define explicit stop conditions.

### Stop Conditions

| Condition | Description |
|-----------|-------------|
| No progress | Two consecutive checkpoints with no change |
| Repeated failure | Same error/stack trace appearing multiple times |
| Cost drift | Token/resource usage outside budget window |
| Blocked | Merge conflicts or dependency failures blocking queue advancement |
| Max iterations | Hard cap to prevent infinite loops |

### Checkpoint Format

```
## Loop Checkpoint [N]
- Items processed: X/Y
- New findings: Z
- Errors: [list]
- Token cost: N tokens
- Status: CONTINUE / STOP
- Stop reason (if STOP): [reason]
```

### Escalation Rules

- After 2 no-progress checkpoints → STOP and report
- After 3 identical failures → STOP and report
- After cost exceeds 2x budget → STOP and report
- Always log checkpoint history for post-mortem analysis

### Application to praxis-skills

Use in skills with iterative workflows:
- `praxis-search-hub`: rate limit monitoring loop
- `praxis-news-aggregator`: multi-source fetch loop
- `praxis-knowledge-radar`: daily/weekly learning orchestration
