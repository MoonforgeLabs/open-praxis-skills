# Skill Architecture Patterns

Sources: mattpocock/skills, gsd-build/get-shit-done

## Router Skill Pattern (mattpocock)

When praxis-skills exceeds 30 skills, create a **router skill** — a user-invoked markdown decision tree that maps situations to skill sequences.

### Rules

- Router is **pure markdown**, not code — the model interprets the decision tree
- Router is **user-invoked** (`disable-model-invocation: true`) — only humans trigger it
- Router references skills via `/skill-name` prose, not file paths
- Router chains skills into workflows: "Run `/grill-with-docs`, then `/to-prd`, then `/to-issues`"

### Invocation Types

| Type | Invoked by | Description | Purpose |
|------|-----------|-------------|---------|
| User-invoked | Human only (`/skill-name`) | Human-facing summary, no trigger list | Orchestration, entry points |
| Model-invoked | Human or model autonomously | Rich trigger description ("Use when...") | Composable building blocks |

**Constraint**: A user-invoked skill can invoke model-invoked skills, but never another user-invoked skill. This creates a clean hierarchy.

### Cross-Skill References

Skills reference each other via `/skill-name` prose invocation, NOT deep file cross-references:

```markdown
# Good — prose invocation
Use `/tdd` where possible, at pre-agreed seams.

# Bad — file cross-reference
See ../tdd/SKILL.md for the TDD workflow.
```

This survives reorganization. If a skill moves, only its registration needs updating.

## Namespace Routing (gsd-build)

When skill count grows large, group into namespaces with router skills per namespace.

### Problem

86 flat skills = ~2,150 tokens in description list. Too expensive.

### Solution

6 namespace meta-skills that each route to their sub-skills:

```
Model sees 6 namespace routers (~120 tokens)
  → Selects namespace
    → Routes to specific sub-skill via routing table
```

**Savings**: 94% token reduction.

### Routing Table Format

Use pipe-delimited keyword labels (≤60 chars). Based on Tool Attention research — keyword-dense labels are more effective than prose, with ~40% lower token cost:

```markdown
| User wants | Invoke |
|---|---|
| Gather context before planning | praxis-discuss |
| Create a plan | praxis-plan |
| Execute plans | praxis-execute |
| Verify results | praxis-verify |
```

## Thin Orchestrator (gsd-build)

Workflow files do NO heavy work — they only coordinate.

### Principle

```
Orchestrator coordinates, not executes.
Each subagent loads the full context.
Orchestrator: discover → analyze → group → spawn → collect.
```

### Benefits

- Each agent gets a fresh 200K context window
- Orchestrator stays lean, avoids context pollution
- Agents verify file system and git state after completion

## Wave Execution (gsd-build)

When executing multiple plans, group by dependency into waves:

```
Plan 01 (no deps)      ─┐
Plan 02 (no deps)      ─┤── Wave 1 (parallel)
Plan 03 (depends: 01)  ─┤── Wave 2 (waits for Wave 1)
Plan 04 (depends: 02)  ─┘
Plan 05 (depends: 03,04) ── Wave 3 (waits for Wave 2)
```

### Execution

1. Analyze plan dependencies, group into waves
2. Execute each wave's agents in parallel
3. Each executor gets: fresh context, specific plan, project state
4. Verify wave completion before proceeding

### Safety

- Parallel agents use `--no-verify` commits to avoid lock contention
- STATE.md file lock (`O_EXCL` atomic creation) prevents read-modify-write races
- If wave N has unfinished lower-wave plans, stop and report

## Context Hygiene (mattpocock)

When a session grows long, manage context deliberately:

| Situation | Action | Why |
|-----------|--------|-----|
| Task complete, starting new task | `/handoff` — fork to fresh session | Clean context for new task |
| Task ongoing, context getting heavy | `/compact` — compress in same session | Preserve task continuity |
| Switching between unrelated topics | `/handoff` — new session | Prevent context pollution |
| Deep in one topic, need more space | `/compact` — compress | Keep accumulated understanding |

### Rules

- **Never start a new task in a heavy context** — the agent will carry stale assumptions
- **Handoff includes**: current state, next steps, suggested skills for the new session
- **Compact includes**: compressed conversation, key decisions preserved, file references maintained
- **Router skill should guide**: "If context is heavy, run `/handoff` first"
