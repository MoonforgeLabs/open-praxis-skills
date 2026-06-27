# Skill Evaluation Methodology

Source: anthropics/skills skill-creator

## Progressive Disclosure Levels

| Level | Content | Loaded When | Token Cost |
|-------|---------|-------------|------------|
| 1: Metadata | name + description | Session startup, always | ~100 tokens |
| 2: SKILL.md body | Full instructions | When skill is activated | ~5,000 tokens max |
| 3: References | scripts/, references/, assets/ | Only when read via bash | 0 until accessed |

**Rule**: Keep core instructions in Level 2. Move branch-specific details to Level 3. Level 3 files are on filesystem, zero cost until read.

## Eval Framework

Test each skill against real-world scenarios before publishing.

### 20-Query Eval

For description quality testing:

- 10 queries that SHOULD trigger the skill
- 10 queries that SHOULD NOT trigger the skill
- Target: ≥80% accuracy on both sets

### Scenario-Based Eval

Run the skill against 3+ real scenarios:

1. **Happy path**: standard use case, should complete cleanly
2. **Edge case**: unusual input, missing dependencies, partial data
3. **Error case**: invalid input, network failure, permission denied

### Completion Criteria Check

For each scenario, verify:
- [ ] Every step in the SKILL.md was followed
- [ ] Every completion criterion was met
- [ ] No steps were skipped or improvised
- [ ] Output matches expected format

## Benchmark Results Format

```
## Eval Results: praxis-xxx

### Trigger Accuracy
- True positive: 9/10 (90%)
- True negative: 8/10 (80%)
- Overall: 85%

### Scenario Results
| Scenario | Pass | Notes |
|----------|------|-------|
| Happy path | ✅ | Clean completion |
| Edge case | ⚠️ | Missing fallback for empty input |
| Error case | ❌ | No error handling for network timeout |

### Issues Found
1. Description too broad — triggers on "search" even when not relevant
2. No fallback when dependency X is missing

### Recommendation
Fix issues #1 and #2 before publishing.
```

## A/B Comparison

When evaluating a new version against old:

1. Run both versions against the same eval set
2. Compare: completion rate, output quality, token cost
3. Report: which version wins, by how much, on what criteria
