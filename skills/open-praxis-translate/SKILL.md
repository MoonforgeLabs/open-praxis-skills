---
name: open-praxis-translate
description: Translates articles and documents between languages with three modes - quick (direct), normal (analyze then translate), and refined (analyze, translate, review, polish). Supports custom glossaries and terminology consistency via EXTEND.md. Use when user asks to "translate", "翻译", "精翻", "translate article", "translate to Chinese/English", "改成中文", "改成英文", "convert to Chinese", "localize", "本地化", "refined translation", "精细翻译", "proofread translation", "快速翻译", "快翻", or when a URL or file is provided with translation intent.
---

# Translator

Three-mode translation skill: **quick** for direct translation, **normal** for analysis-informed translation, **refined** for full publication-quality workflow with review and polish.

## User Input Tools

When this skill prompts the user, follow this tool-selection rule (priority order):

1. **Prefer built-in user-input tools** exposed by the current agent runtime — e.g., `AskUserQuestion`, `request_user_input`, `clarify`, `ask_user`, or any equivalent.
2. **Fallback**: if no such tool exists, emit a numbered plain-text message and ask the user to reply with the chosen number/answer for each question.
3. **Batching**: if the tool supports multiple questions per call, combine all applicable questions into a single call; if only single-question, ask them one at a time in priority order.

## Preferences (EXTEND.md)

Check EXTEND.md in priority order — the first one found wins:

| Priority | Path | Scope |
|----------|------|-------|
| 1 | `.praxis-skills/praxis-translate/EXTEND.md` | Project |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/praxis-skills/praxis-translate/EXTEND.md` | XDG |
| 3 | `$HOME/.praxis-skills/praxis-translate/EXTEND.md` | User home |

| Result | Action |
|--------|--------|
| Found | Read, parse, apply. On first use in session, briefly remind: "Using preferences from [path]. You can edit EXTEND.md to customize glossary, audience, etc." |
| Not found | **MUST** run first-time setup (see below) — do NOT silently use defaults |

**EXTEND.md supports**: default target language, default mode, target audience, custom glossaries (inline or file path), translation style, chunk settings.

### First-Time Setup (BLOCKING)

When EXTEND.md is not found, you **MUST** run the first-time setup before ANY translation.

Use `AskUserQuestion` with all questions (target language, mode, audience, style, save location) in ONE call. After user answers, create EXTEND.md at the chosen location, confirm "Preferences saved to [path]", then continue.

## Defaults

| Setting | Default | EXTEND.md key | Description |
|---------|---------|---------------|-------------|
| Target language | `zh-CN` | `target_language` | Translation target language |
| Mode | `normal` | `default_mode` | Translation mode |
| Audience | `general` | `audience` | Target reader profile |
| Style | `storytelling` | `style` | Translation style preference |
| Chunk threshold | `4000` | `chunk_threshold` | Word count to trigger chunked translation |
| Chunk max words | `5000` | `chunk_max_words` | Max words per chunk |

## Modes

| Mode | Flag | Steps | When to Use |
|------|------|-------|-------------|
| Quick | `--mode quick` | Translate | Short texts, informal content, quick tasks |
| Normal | `--mode normal` (default) | Analyze → Translate | Articles, blog posts, general content |
| Refined | `--mode refined` | Analyze → Translate → Review → Polish | Publication-quality, important documents |

**Style presets** — control the voice and tone of the translation:

| Value | Description | Effect |
|-------|-------------|--------|
| `storytelling` | Engaging narrative flow (default) | Draws readers in, smooth transitions, vivid phrasing |
| `formal` | Professional, structured | Neutral tone, clear organization, no colloquialisms |
| `technical` | Precise, documentation-style | Concise, terminology-heavy, minimal embellishment |
| `literal` | Close to original structure | Minimal restructuring, preserves source sentence patterns |
| `academic` | Scholarly, rigorous | Formal register, complex clauses OK, citation-aware |
| `business` | Concise, results-focused | Action-oriented, executive-friendly, bullet-point mindset |
| `humorous` | Preserves and adapts humor | Witty, playful, recreates comedic effect in target language |
| `conversational` | Casual, spoken-like | Friendly, approachable, as if explaining to a friend |
| `elegant` | Literary, polished prose | Aesthetically refined, rhythmic, carefully crafted word choices |

**Auto-detection**:
- "快翻", "quick", "直接翻译" → quick mode
- "精翻", "refined", "publication quality", "proofread" → refined mode
- Otherwise → default mode (normal)

**Upgrade prompt**: After normal mode completes, display:
> Translation saved. To further review and polish, reply "继续润色" or "refine".

**Audience presets**:

| Value | Description | Effect |
|-------|-------------|--------|
| `general` | General readers (default) | Plain language, more translator's notes for jargon |
| `technical` | Developers / engineers | Less annotation on common tech terms |
| `academic` | Researchers / scholars | Formal register, precise terminology |
| `business` | Business professionals | Business-friendly tone, explain tech concepts |

## Workflow

### Step 1: Load Preferences

1.1 Check EXTEND.md (see Preferences section above)
1.2 Load built-in glossary for the language pair if available
1.3 Merge glossaries: EXTEND.md `glossary` (inline) + EXTEND.md `glossary_files` (external files) + built-in glossary

### Step 2: Materialize Source & Create Output Directory

Materialize source (file as-is, inline text/URL → save to `translate/{slug}.md`), then create output directory: `{source-dir}/{source-basename}-{target-lang}/`. Detect source language if not specified.

**Output directory contents**:

| File | Mode | Description |
|------|------|-------------|
| `translation.md` | All | Final translation (always this name) |
| `01-analysis.md` | Normal, Refined | Content analysis (domain, tone, terminology) |
| `02-prompt.md` | Normal, Refined | Assembled translation prompt |
| `03-draft.md` | Refined | Initial draft before review |
| `04-critique.md` | Refined | Critical review findings |
| `05-revision.md` | Refined | Revised translation based on critique |

### Step 3: Assess Content Length

For normal and refined modes:

| Content | Action |
|---------|--------|
| < chunk threshold | Translate as single unit |
| >= chunk threshold | Chunk translation |

For long content, extract terminology first, build session glossary, split into chunks at markdown block boundaries, then translate chunks (via subagents if available) and merge.

### Step 4: Translate & Refine

**Translation principles** (apply to all modes):

- **Rewrite, not translate**: Rewrite content into natural, engaging target language as if a skilled native writer composed it from scratch
- **Accuracy first**: Facts, data, and logic must match the original exactly
- **Natural flow**: Use idiomatic target language word order. Break long source sentences into shorter, natural ones
- **Terminology**: Use standard translations consistently. First occurrence of specialized terms: annotate with original in parentheses
- **Preserve format**: Keep all markdown formatting (headings, bold, italic, images, links, code blocks)
- **Proactive interpretation**: For jargon or concepts the target audience may lack context for, add concise explanations in **bold parentheses**
- **Frontmatter**: If source has YAML frontmatter, rename source-metadata fields with `source` prefix, add translated values as new top-level fields

#### Quick Mode
Translate directly → save to `translation.md`.

#### Normal Mode
1. **Analyze** → `01-analysis.md`
2. **Assemble prompt** → `02-prompt.md`
3. **Translate** → `translation.md`

#### Refined Mode
1. **Analyze** → `01-analysis.md`
2. **Assemble prompt** → `02-prompt.md`
3. **Draft** → `03-draft.md`
4. **Critical review** → `04-critique.md`
5. **Revision** → `05-revision.md`
6. **Polish** → `translation.md`

### Step 5: Output

Display summary:
```
**Translation complete** ({mode} mode)

Source: {source-path}
Languages: {from} → {to}
Output dir: {output-dir}/
Final: {output-dir}/translation.md
Glossary terms applied: {count}
```
