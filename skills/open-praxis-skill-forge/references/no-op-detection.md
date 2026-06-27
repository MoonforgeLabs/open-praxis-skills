# No-Op Detection Guide

Source: mattpocock/skills `writing-great-skills`

## Core Principle

A skill exists to wrangle determinism out of a stochastic system. Every line in SKILL.md must change the agent's default behavior. If removing a line would not change the output, that line is a no-op — delete it.

## Detection Test

For each sentence in SKILL.md, ask:

> "If this line disappeared, would the agent's behavior change?"

- **If no** → delete the entire sentence (not just trim words).
- **If the same meaning appears twice** → keep one source of truth.
- **If a paragraph keeps growing** → move reference material behind a context pointer.
- **If a weak phrase says what the model already does** → replace with a stronger leading word or delete.

## Common No-Op Patterns

| Pattern | Example | Why it's no-op |
|---------|---------|----------------|
| Stating the obvious | "Be thorough" | Agent default behavior is already thorough |
| Generic quality advice | "Write good code" | Agent already tries to write good code |
| Redundant instruction | "Make sure to check" (already in a step) | Duplicate of existing step |
| Philosophy without action | "Quality matters" | Doesn't change any specific behavior |
| Hedge words | "If possible, try to..." | Agent already does what's possible |

## Strong Replacements

| Weak (no-op) | Strong (changes behavior) |
|--------------|---------------------------|
| "Be thorough" | "Account for every modified model" |
| "Check carefully" | "Run validation and confirm zero errors" |
| "Consider edge cases" | "Test with empty input, max input, and null" |
| "Write clearly" | "Use one sentence per step, imperative mood" |

## Pruning Aggression

"Be aggressive — most prose that fails should go, not be rewritten."

When in doubt, delete. The agent is more capable than you think. Only keep lines that prevent specific, observed failure modes.

## Leading Word Quality

A **leading word** is a concept already in the model's pretraining that anchors behavior. Use it consistently throughout the skill.

Good leading words (compact, high-signal):
- `tracer bullet` — thin vertical slice through all layers
- `fog of war` — uncertainty in complex systems
- `relentless` — exhaustive completion
- `single source of truth` — no duplication

Weak leading words (no-op or vague):
- `best practices` — too generic
- `comprehensive` — agent default
- `carefully` — no specific behavior change

## When NOT to Prune

Keep lines that:
1. Prevent a specific observed failure mode.
2. Define a completion criterion the agent would otherwise skip.
3. Correct a common agent misconception about the domain.
4. Specify an output format the agent would otherwise improvise.