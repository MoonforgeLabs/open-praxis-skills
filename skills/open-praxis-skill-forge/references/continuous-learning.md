# Continuous Learning: Instinct System

Source: affaan-m/ECC continuous-learning-v2

## Purpose

Capture recurring patterns from agent sessions as reusable "instincts" that improve future performance.

## Instinct Lifecycle

```
Observed pattern → Atomic instinct → Cluster → Skill/Command/Agent
```

| Stage | Description | Confidence |
|-------|-------------|------------|
| Observed | Pattern noticed in one or more sessions | — |
| Atomic instinct | Formalized as a rule with confidence score | 0.3–0.5 |
| Cluster | Multiple related instincts grouped | 0.5–0.7 |
| Promoted | Becomes a skill, command, or agent | 0.7–0.9 |

## Confidence Scoring

Each instinct has a confidence score (0.3–0.9):

| Score | Meaning | Action |
|-------|---------|--------|
| 0.3 | Observed once, unverified | Log only |
| 0.5 | Observed 2-3 times, consistent | Suggest to user |
| 0.7 | Observed 5+ times, never contradicted | Auto-apply with notification |
| 0.9 | Verified across multiple projects | Auto-apply silently |

## Scoping Rules

### Project-Scoped Instincts

- Belong to a specific project
- Prevent cross-project contamination
- Stored in project memory (e.g., `~/.claude/projects/<project>/memory/`)

### Global Promotion

An instinct promotes from project scope to global scope when:

1. Same instinct ID exists in 2+ projects
2. Average confidence across those projects ≥ 0.8

## Capture Mechanism

Hooks capture 100% of tool use (not probabilistic). Each captured event includes:
- Tool name and parameters
- Outcome (success/failure)
- Context (project, session, timestamp)
- User feedback (if any)

## Instinct Format

```yaml
id: instinct-<hash>
pattern: "When X happens, do Y instead of Z"
confidence: 0.6
scope: project  # or global
project: my-project
evidence:
  - date: 2026-06-20
    context: "Encountered timeout on API call"
    action: "Switched to retry with backoff"
    outcome: success
  - date: 2026-06-22
    context: "Same timeout pattern"
    action: "Applied retry with backoff"
    outcome: success
```

## Application to praxis-skills

When a skill consistently produces better results with a specific approach:
1. Log the pattern as an instinct with initial confidence
2. Track occurrences and outcomes
3. When confidence ≥ 0.7, update the SKILL.md to codify the pattern
4. When promoted to global, share across all skills via a reference file
