# Writing Great Skills Adaptation

Use this distilled lens when curating Alex skills. Source: `mattpocock/skills` `skills/productivity/writing-great-skills/SKILL.md`.

## Core Goal

Optimize for predictability: the agent should follow the same process for the same class of task, even if outputs differ.

## Invocation Decisions

- Keep a skill model-invoked only when the agent must discover it autonomously or another skill must route to it.
- Prefer a router skill when many user-invoked skills create too much cognitive load.
- Front-load the leading word in a model-facing description.
- Keep one trigger per branch; remove synonym-only trigger duplication.

## Merge Or Split

Merge when:

- The user cannot remember which overlapping skill to invoke.
- Multiple skills share the same leading word, state model, or input/output shape.
- A router would reduce cognitive load more than separate descriptions help model invocation.

Split when:

- A branch has a distinct leading word that deserves independent invocation.
- Later steps tempt premature completion of earlier work.
- A branch needs substantial references that most runs should not load.

## Information Hierarchy

- Put essential ordered actions in `SKILL.md`.
- Keep every step checkable with a completion criterion.
- Move branch-specific checklists, source ledgers, templates, and long examples to `references/`.
- Keep definitions, rules, and caveats co-located under the same heading.

## Pruning Test

For each sentence ask: would behavior change if this line disappeared?

- If no, delete it.
- If the same meaning appears twice, keep one source of truth.
- If a paragraph keeps growing, move reference material behind a pointer.
- If a weak phrase says what the model already does, replace it with a stronger leading word or delete it.

## Failure Modes To Check

- `premature completion`: steps finish before the completion criterion is actually satisfied.
- `duplication`: one meaning exists in multiple places.
- `sediment`: stale layers remain because adding felt safer than pruning.
- `sprawl`: the skill is too long even if each line is individually useful.
- `no-op`: text does not change behavior versus default agent behavior.
