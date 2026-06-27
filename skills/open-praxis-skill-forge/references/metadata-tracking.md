# Metadata Tracking Pattern

Source: hesreallyhim/awesome-claude-code

## Problem

Managing 30+ skills with metadata (source, author, license, version, status) scattered across individual files is unmaintainable.

## Solution: CSV as Single Source of Truth

Use one CSV file as the canonical metadata store. All other views (README tables, taxonomy docs, marketplace manifests) are generated from it.

## CSV Schema

| Column | Purpose | Example |
|--------|---------|---------|
| `ID` | Unique identifier | `skill-a1b2c3d4` |
| `Display Name` | Human-readable name | `Alex Translate` |
| `Category` | Primary category | `Content & Writing` |
| `Sub-Category` | Secondary classification | `Translation` |
| `Primary Link` | Main URL | `https://github.com/...` |
| `Author Name` | Author | `Alex` |
| `Active` | Still maintained? | `TRUE/FALSE` |
| `Date Added` | When imported | `2026-06-26` |
| `Last Modified` | Last content change | `2026-06-26` |
| `Last Checked` | Last upstream check | `2026-06-26` |
| `License` | Open source license | `MIT` |
| `Description` | One-line description | `Three-mode translation...` |
| `Stale` | Over 90 days unchecked? | `TRUE/FALSE` |
| `Source Repo` | Upstream repo URL | `https://github.com/...` |

## ID Generation

Format: `{category_prefix}-{sha256[:8]}`

- Prefix from category: `skill-`, `agent-`, `hook-`, `tool-`
- Hash: `sha256(display_name + primary_link)[:8]` — idempotent, deterministic

## Automation Pipeline

1. **Cron job** (every 3 hours): update `Last Modified` and release info via GitHub API
2. **Health check**: flag repos > 6 months old with > 2 open issues
3. **Link validation**: verify all URLs are reachable
4. **README generation**: `make generate` produces README tables from CSV

## Core Principle

**CSV is the source of truth. README is a derived product.** All changes go into CSV first, then auto-generate documentation.

## Application to praxis-skills

Use `source-notes.md` or a new `skill-registry.csv` as the single source. Generate:
- README skill tables
- `docs/skill-taxonomy.md` categories
- `.claude-plugin/marketplace.json` entries
