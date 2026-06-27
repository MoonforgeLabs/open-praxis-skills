# Token Budget Guidelines

Sources: Anthropic best-practices, Skill Creator plugin, Claude Code docs

## Key Numbers

| Parameter | Limit | Source |
|-----------|-------|--------|
| All skill descriptions combined | ~1% of context window (~2K tokens on 200K) | Anthropic |
| Per-skill description (Claude Code truncation) | 1,536 chars | Anthropic |
| Per-skill description (Claude.ai limit) | 200 chars | Anthropic |
| Description target length | 100-200 chars | Best practice |
| SKILL.md body | < 500 lines | Anthropic |
| SKILL.md body tokens | < 5,000 tokens | Anthropic Complete Guide |
| Compaction per-skill budget | 5,000 tokens | Anthropic |
| Compaction total budget | 25,000 tokens | Anthropic |

## Progressive Disclosure Levels

| Level | Content | Loaded When | Token Cost |
|-------|---------|-------------|------------|
| 1: Metadata | name + description | Session startup, always | ~100 tokens |
| 2: SKILL.md body | Full instructions | When skill is activated | ~5,000 tokens max |
| 3: References | scripts/, references/, assets/ | Only when read via bash | 0 until accessed |

## Why Token Budget Matters

- SKILL.md body stays in context across turns once loaded
- Every token competes with conversation history
- Level 3 files are on filesystem, zero cost until read
- Scripts execute via bash, only stdout costs tokens

## Optimization Strategies

### Description
- Front-load the leading word (verb)
- Put WHAT + WHEN first, trim everything else
- 100-200 chars is optimal; 300+ is a candidate for trimming
- Test with the 20-query eval (10 should trigger, 10 should not)

### SKILL.md Body
- Use the no-op test on every sentence
- Move branch-specific content to references/
- Use context pointers: "See [file.md](file.md) for X"
- Replace prose with checklists (more compact)
- Use tables instead of bullet lists for structured data

### References
- Add table of contents for files > 300 lines
- Keep reference chains to 1 level deep
- Split large references into focused files

## Namespace Routing Savings

For large skill collections (>30 skills):

| Approach | Token Cost |
|----------|------------|
| 86 flat skills listed | ~2,150 tokens |
| 6 namespace routers + sub-skills | ~120 tokens |
| **Savings** | **94%** |

Group skills into namespaces: `<namespace>-<skill>` with a router skill per namespace.
