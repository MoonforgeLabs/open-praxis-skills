# Research Patterns

Source: mvanhorn/last30days-skill

## Entity-Based Research

Organize research around entities (people, companies, products, technologies), not topics.

### Why Entities > Topics

- Entities have unique identifiers (name, URL, ticker symbol)
- Entities can be tracked over time
- Entities have relationships that form a knowledge graph
- Entities produce evidence that can be clustered

### Entity Workflow

1. **Identify entities** from the research question
2. **Gather evidence** per entity (articles, commits, announcements)
3. **Cluster evidence** by theme (funding, product launch, hiring, controversy)
4. **Generate brief** per entity with evidence-backed claims

## Evidence Clustering

Group related evidence into themes before writing conclusions.

### Rules

- Each evidence item has: source, date, claim, confidence
- Cluster by theme, not by source
- Contradictory evidence stays in the same cluster (note the conflict)
- Missing evidence is itself a signal (absence of announcement ≠ no activity)

### Cluster Output Format

```
## [Entity Name]

### Theme: [Product Launch]
- [2026-06-01] Company announced X (source: blog, confidence: high)
- [2026-06-03] Reviewer Y confirmed Z (source: twitter, confidence: medium)

### Theme: [Hiring]
- [2026-05-15] Job posting for role A (source: careers page, confidence: high)

### Contradictions
- Company says "no layoffs" but 3 employees posted about job searching
```

## Brief Generation

Automatically generate structured briefs from clustered evidence.

### Brief Structure

1. **Executive Summary**: 2-3 sentences, key takeaway
2. **Entity Breakdown**: one section per entity
3. **Evidence Map**: themes → evidence items
4. **Confidence Assessment**: overall confidence level with justification
5. **Gaps**: what's missing, what to watch for

## Watchlist Pattern

Track entities over time with periodic re-evaluation.

### Watchlist Entry

```yaml
- entity: "Anthropic"
  watch_for:
    - "New model releases"
    - "API pricing changes"
    - "Safety research publications"
  check_frequency: weekly
  last_checked: 2026-06-20
  sources:
    - "anthropic.com/blog"
    - "twitter.com/AnthropicAI"
```

### Watchlist Rules

- Only watch entities with active relevance
- Re-evaluate watchlist monthly — remove stale entries
- New evidence triggers a brief update, not a full re-research
