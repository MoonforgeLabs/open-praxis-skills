# Skill Taxonomy

This taxonomy classifies Alex skills by primary usage scenario. Keep the physical directory structure flat under `skills/praxis-*` for broad agent compatibility; use this document and README tables for organization.

## Categories

| Category | Purpose | When to add here |
|---|---|---|
| Knowledge & Research | Gather, extract, and synthesize external knowledge | News, webpages, transcripts, research scans |
| Content & Writing | Transform, polish, translate, and publish text | Translation, markdown formatting, writing style, HTML conversion |
| Visual & Media | Create or process visual/media artifacts | Images, diagrams, cards, slides, video clipping, compression |
| Developer & Automation | Operate engineering workflows, developer systems, and access-layer tools | GitHub monitoring, repo automation, engineering reports, Agent-Reach operations |
| Personal Operations | Manage personal systems, assets, and operating rules | Asset governance, configuration/security decisions |

## Current Classification

### Knowledge & Research

| Skill | Primary Use | Dependency |
|---|---|---|
| `praxis-news-aggregator` | Daily news / tech / AI briefings | WebSearch/WebFetch |
| `praxis-search-hub` | Safe search gateway and source routing | `mcporter`, `opencli`, `bili`, last30days optional |
| `praxis-url-to-markdown` | Save URLs as clean Markdown | WebFetch or curl |
| `praxis-youtube-transcript` | Download and structure YouTube transcripts | `yt-dlp` |
| `praxis-knowledge-radar` | 知识捕获管线 + 学习编排：文章/链接输入 → 归类入库 → 学习内化 → 应用输出 | Local JSONL store optional |

### Content & Writing

| Skill | Primary Use | Dependency |
|---|---|---|
| `praxis-translate` | Translation and refinement | None |
| `praxis-format-markdown` | Markdown cleanup and layout | None |
| `praxis-humanizer-zh` | Remove AI flavor from Chinese text | None |
| `praxis-markdown-to-html` | Convert Markdown to styled HTML | None |

### Visual & Media

| Skill | Primary Use | Dependency |
|---|---|---|
| `praxis-diagram` | SVG diagrams, flows, architecture visuals | None |
| `praxis-compress-image` | Compress images | `sips`, `cwebp`, ImageMagick, or Sharp |
| `praxis-slide-deck` | HTML slide decks | None |
| `praxis-logo-generator` | SVG logo variants | None |
| `praxis-image-gen` | AI image generation or SVG illustration | Optional AI image API |
| `praxis-infographic` | Data-driven infographics | Optional AI image API |
| `praxis-image-cards` | Social/article image cards | Optional AI image API |
| `praxis-cover-image` | Article cover images | Optional AI image API |
| `praxis-youtube-clipper` | Clip videos and add subtitles | `yt-dlp` + `ffmpeg-full` |

### Developer & Automation

| Skill | Primary Use | Dependency |
|---|---|---|
| `praxis-github-watchtower` | Operate GitHub repository monitoring and fork sync | Local watchtower project |
| `praxis-agent-reach-ops` | Operate Agent-Reach access, transcription, formatting, and health checks | `agent-reach` CLI |
| `praxis-personal-monitor` | Run personal AI/news/media/investment monitoring | Watchtower reports optional |
| `moonforge-os-monitor` | Run Moonforge AI OS monitoring and inspiration absorption | Moonforge + watchtower optional |

### Personal Operations

| Skill | Primary Use | Dependency |
|---|---|---|
| `praxis-asset-governance` | Decide where personal assets/configs/secrets belong | None |
| `praxis-skill-design-standard` | Design, review, prune, and refactor reusable Codex/Claude skills | None |
| `praxis-skill-forge` | Evaluate, deduplicate, and absorb external skills into praxis-skills | None |
| `moonforge-review` | Run weekly/monthly Moonforge reviews and improvement backlog triage | Local reports optional |

## Classification Rules

- Assign each Skill one primary category only.
- Mention secondary use cases in the description, not as duplicate categories.
- Do not change the physical folder structure for categorization.
- Keep category names stable to make README, docs, and future generated indexes consistent.
- If a Skill operates another tool or repository, classify by the user's goal, not by implementation language.

## Adding a New Skill

When adding a Skill:

1. Choose exactly one primary category.
2. Add it to this document.
3. Add it to the README category table.
4. Register it in `.claude-plugin/marketplace.json` if it should be installable as part of the plugin.
5. Validate Codex compatibility with conservative frontmatter.

## Adapted Productivity And Engineering

| Skill | Primary Use | Dependency |
|---|---|---|
| `praxis-grill-me` | Run a user-invoked plan/design pressure-test interview. | None |
| `praxis-grilling` | Reusable one-question-at-a-time plan/design interrogation loop. | None |
| `praxis-handoff` | Compact a session into a handoff for another agent or future session. | None |
| `praxis-teach` | Teach a skill or concept over multiple stateful sessions. | None |
| `praxis-debugger` | Diagnose bugs and regressions with reproduce-minimize-hypothesize-instrument-fix loop. | None |
| `praxis-codebase-design` | Design deep modules, small interfaces, clean seams, and testable architecture. | None |
| `praxis-domain-modeling` | Build glossaries, ubiquitous language, and domain ambiguity maps. | None |
| `praxis-tdd` | Run behavior-first red-green-refactor development loops. | None |
| `praxis-to-prd` | Turn a conversation or idea into a concise PRD. | None |
| `praxis-to-issues` | Break a PRD or plan into vertical executable issues. | None |
| `praxis-issue-triage` | Triage issues or backlog items into agent-ready next actions. | None |
| `praxis-prototype` | Build throwaway prototypes to answer product, UI, API, or state questions. | None |
| `praxis-code-review` | Review diffs against project standards and the originating spec. | None |
| `praxis-git-guardrails` | Design guardrails against dangerous git operations in agent workflows. | None |
| `praxis-edit-article` | Edit long-form writing for structure, clarity, and flow. | None |
| `praxis-writing-fragments` | Capture raw writing fragments before imposing structure. | None |
| `praxis-writing-shape` | Shape notes or drafts into publishable articles. | None |
| `praxis-exercise-scaffold` | Scaffold learning exercises with problems, solutions, and explainers. | None |
