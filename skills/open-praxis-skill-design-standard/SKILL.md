---
name: open-praxis-skill-design-standard
description: Design, review, prune, or refactor Codex/Claude skills so they are small, invokable, progressively disclosed, safe, and verifiable. Use when creating a new skill, improving an existing skill, splitting an oversized skill, writing trigger descriptions, or deciding what belongs in SKILL.md versus references.
---

# Alex Skill Design Standard

Use this skill to make other skills predictable and maintainable.

## Core Standard

A good skill is:

- **Small**: one recurring job, not a whole department.
- **Invokable**: description says exactly when the model or user should reach for it.
- **Portable**: avoids hard-coded private paths unless the skill is explicitly private.
- **Progressively disclosed**: `SKILL.md` contains routing and core steps; long rubrics live in `references/`.
- **Verifiable**: has a completion criterion, validation command, checklist, or observable artifact.
- **Safe**: names approval gates for secrets, external writes, public publishing, money, legal, medical, security, or destructive actions.

## Invocation Decision

| Type | Use When | Description Style |
|---|---|---|
| Model-invoked | The model can safely detect and use the skill autonomously. | Trigger-rich: “Use when the user asks…” |
| User-invoked | The skill is high-impact, broad, or should only run on explicit command. | Human-facing: concise slash-command summary. |

Default to model-invoked only when autonomous use is low-risk and clearly helpful.

## Design Workflow

1. Name the repeated job in one sentence.
2. Decide whether it is model-invoked or user-invoked.
3. Write the shortest useful `description`.
4. Put core execution in `SKILL.md`.
5. Move long examples, rubrics, schemas, and source notes into `references/`.
6. Add guardrails and completion criteria.
7. Check overlap with existing skills before adding a new one.
8. Validate frontmatter and repo indexes.

## Anti-Patterns

- **Sprawl**: one skill tries to cover many unrelated workflows.
- **No-op prose**: lines that do not change model behavior.
- **Sediment**: old instructions kept because deletion feels risky.
- **Premature completion**: moving to the next phase without a concrete artifact.
- **Hidden dependency**: relying on a tool, account, repo, or secret not declared in the skill.
- **Cross-reference maze**: linking deeply into another skill instead of invoking it or owning the reference locally.

## Output Shape For Reviews

Return:

- `Keep`: lines/sections that should remain.
- `Prune`: no-op, duplicate, stale, or unsafe sections.
- `Split`: parts that should become separate skills or references.
- `Move`: content that belongs in `references/`, README, taxonomy, or private config.
- `Validate`: exact command or manual check.

## Attribution

This standard adapts design patterns from `mattpocock/skills`: small composable skills, invocation boundaries, progressive disclosure, and anti-pattern pruning. It is rewritten for Alex's Codex/Claude skill repositories.
