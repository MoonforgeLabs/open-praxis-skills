# Skill Writing TDD

Source: obra/superpowers writing-skills

## Three Phases

**RED**: Run agent WITHOUT skill, record verbatim failures
**GREEN**: Write minimal SKILL.md that fixes specific failures
**REFACTOR**: Plug holes, build rationalization table, add test scenarios

## Match Form to Failure

| Failure Type | Instruction Form |
|-------------|-----------------|
| Agent does forbidden thing | **Prohibition** ("NEVER use eval()") |
| Agent skips step | **Recipe** ("Step 1: X. Step 2: Y.") |
| Wrong structure | **Structural constraint** ("Output must have 3 sections") |
| Wrong judgment | **Decision rule** ("If X then Y") |
| Wrong approach | **Leading word** ("Use tracer-bullet") |

## Micro-Test: ≥5 runs per variant, always include control group (no skill)
