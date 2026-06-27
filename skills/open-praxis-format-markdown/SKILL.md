---
name: open-praxis-format-markdown
description: Formats plain text or markdown files with frontmatter, titles, summaries, headings, bold, lists, and code blocks. Use when user asks to "format markdown", "beautify article", "add formatting", "排版", "格式化", or improve article layout.
---

# Markdown Formatter

Transforms plain text or markdown into well-structured, reader-friendly markdown. The goal is to help readers quickly grasp key points, highlights, and structure — without changing any original content.

**Core principle**: Only adjust formatting and fix obvious typos. Never add, delete, or rewrite content.

## User Input Tools

When this skill prompts the user, follow this tool-selection rule (priority order):

1. **Prefer built-in user-input tools** exposed by the current agent runtime — e.g., `AskUserQuestion`.
2. **Fallback**: emit a numbered plain-text message and ask the user to reply.

## Workflow

### Step 1: Read & Detect Content Type

| Indicator | Classification |
|-----------|----------------|
| Has `---` YAML frontmatter | Markdown |
| Has `#`, `##`, `###` headings | Markdown |
| Has `**bold**`, `*italic*`, lists, code blocks | Markdown |
| None of above | Plain text |

**If Markdown detected, ask user:**

1. **Optimize formatting** (Recommended) — Analyze content, improve headings/bold/lists, output to `{filename}-formatted.md`
2. **Keep original formatting** — Preserve existing structure, only fix typography
3. **Typography fixes only** — Fix spacing/emphasis in-place, no copy

### Step 2: Analyze Content

Read the entire content from a reader's perspective. Produce analysis covering:

- **Highlights & Key Insights**: Core arguments, surprising facts, golden quotes
- **Structure Assessment**: Logical flow, natural section boundaries, walls of text
- **Reader-Important Info**: Actionable advice, key concepts, lists buried in prose
- **Formatting Issues**: Missing headings, mixed-topic paragraphs, unmarked code

Save analysis to `{original-filename}-analysis.md`.

### Step 3: Create Frontmatter, Title & Summary

| Field | Processing |
|-------|------------|
| `title` | Generate 4-5 candidates, ask user to pick (or auto-select) |
| `slug` | Infer from file path or generate from title |
| `summary` | 1 sentence, ~50-80 chars — concise hook |
| `description` | 2-3 sentences, ~100-200 chars — richer context |

**Title Generation**: Generate mix of hook titles + straightforward titles. Present strongest first as recommended. If `auto_select` enabled in EXTEND.md, skip user prompt.

### Step 4: Format Content

**Formatting toolkit:**

| Element | When to use |
|---------|-------------|
| `##`, `###` | Natural topic boundaries |
| `**bold**` | Key conclusions, important terms |
| `- item` | Parallel items, feature lists |
| `1. item` | Sequential steps, procedures |
| Markdown table | Comparisons, structured data |
| `` `code` `` | Commands, file paths, technical terms |
| `> quote` | Notable quotes, warnings |
| `---` | Major topic transitions |

**What NOT to do:**
- Do NOT add, delete, or rewrite content
- Do NOT add editorializing headings
- Do NOT over-format: not every sentence needs bold

**What TO do:**
- Preserve the author's voice and every word
- **Bold key conclusions and takeaways**
- Extract parallel items from prose into lists
- Add headings where topics genuinely shift
- Fix obvious typos

### Step 5: Save

Save as `{original-filename}-formatted.md`. Backup existing file if it exists.

### Step 6: Typography Fixes

Apply post-processing:
- Fix CJK emphasis/bold punctuation issues
- Add CJK/English mixed text spacing
- Format frontmatter YAML

### Step 7: Completion Report

```
**Formatting Complete**

Files:
- Analysis: {filename}-analysis.md
- Formatted: {filename}-formatted.md

Changes Applied:
- Headings added: X
- Bold markers added: X
- Lists created: X
- Tables created: X
- Typos fixed: X
```

## Preferences (EXTEND.md)

| Priority | Path | Scope |
|----------|------|-------|
| 1 | `.praxis-skills/praxis-format-markdown/EXTEND.md` | Project |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/praxis-skills/praxis-format-markdown/EXTEND.md` | XDG |
| 3 | `$HOME/.praxis-skills/praxis-format-markdown/EXTEND.md` | User home |

**Supports**: `auto_select` (skip title/summary selection), `auto_select_title`, `auto_select_summary`.
