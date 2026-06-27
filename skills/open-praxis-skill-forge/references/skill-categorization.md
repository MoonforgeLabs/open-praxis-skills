# Skill Categorization

Source: ComposioHQ/awesome-claude-skills

## Two-Tier Taxonomy

### Tier 1: README Categories (human-facing)

Group skills by end-user purpose, not technical implementation:

| Category | Scope |
|----------|-------|
| Knowledge & Research | Gathering, extracting, synthesizing external information |
| Content & Writing | Translation, formatting, editing, publishing |
| Visual & Media | Images, diagrams, video, slides |
| Developer & Automation | Engineering workflows, CI/CD, repo management |
| Personal Operations | Config, governance, monitoring, reviews |
| App Automation | Connecting to external tools and services |

### Tier 2: Machine-Readable Tags (marketplace.json)

For plugin manifests and search, use granular tags:

```
business-marketing, communication-writing, creative-media,
development, productivity-organization, crm, project-management,
email, devops, analytics, calendar, storage-docs, design,
support, ecommerce, social-media, spreadsheets, hr, automation
```

## Categorization Rules

1. **Functional, not technical** — slot by what the skill does for the user, not how it works internally
2. **Primary purpose wins** — if a skill does translation AND formatting, pick the dominant use case
3. **App automation gets a second layer** — subcategorize by app vertical (CRM, DevOps, Email, etc.)
4. **One primary category** — each skill has exactly one primary category; use tags for secondary classification

## Anti-Patterns

- **"Utility" catch-all** — too vague, forces everything in
- **Technical categories** — "Python skills", "API skills" — users don't think this way
- **Over-granular** — 50 categories with 1 skill each defeats the purpose

## Application to praxis-skills

Current taxonomy in `docs/skill-taxonomy.md`. Align with these categories:

| praxis-skills Category | Maps to |
|---------------------|---------|
| Knowledge & Research | Knowledge & Research |
| Content & Writing | Content & Writing |
| Visual & Media | Visual & Media |
| Developer & Automation | Developer & Automation |
| Personal Operations | Personal Operations |
