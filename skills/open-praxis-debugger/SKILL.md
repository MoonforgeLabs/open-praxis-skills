---
name: open-praxis-debugger
description: Diagnose hard bugs, failing tests, regressions, or performance problems with a disciplined loop: reproduce, minimize, hypothesize, instrument, fix, and regression-test.
---

# Alex Debugger

Use a diagnosis loop, not guesswork.

## Workflow

1. Reproduce the failure or identify why it cannot be reproduced.
2. Minimize the failing case.
3. State hypotheses ranked by likelihood.
4. Inspect code/logs/tests to eliminate hypotheses.
5. Patch the smallest root cause.
6. Add or run a regression check.
7. Report what changed and what remains uncertain.

## Anti-Patterns

- Fixing before reproducing.
- Changing multiple unrelated areas.
- Treating symptoms as root causes.
- Skipping regression validation.

Inspired by `mattpocock/skills` `diagnosing-bugs` under MIT License.
