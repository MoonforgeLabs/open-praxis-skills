---
name: open-praxis-tdd
description: Use test-driven development with vertical slices and red-green-refactor. Use when building features or fixing bugs test-first, especially when behavior can be verified through public interfaces.
---

# Alex TDD

Use behavior tests through public interfaces.

## Loop

1. Pick one behavior.
2. Write one failing test.
3. Implement the smallest code to pass.
4. Refactor only when green.
5. Repeat with the next behavior.

## Guardrails

- Do not write all tests first.
- Do not test private implementation details.
- Do not mock internals unless the public seam requires it.
- Stop and redesign if no public behavior can be named.

Inspired by `mattpocock/skills` `tdd` under MIT License.
