---
name: open-praxis-slide-deck
description: Creates presentation slide decks as HTML files with speaker notes, transitions, and keyboard navigation. Use when user asks to "create slides", "make presentation", "做PPT", "幻灯片", "slide deck", or wants to present content.
---

# Slide Deck Generator

Creates self-contained HTML slide presentations with keyboard navigation, speaker notes, and responsive design.

## Features

- Keyboard navigation (arrow keys, space, escape)
- Speaker notes (press `S` to toggle)
- Progress bar
- Slide counter
- Dark theme with accent colors
- Code syntax highlighting
- Responsive images
- Print to PDF support

## Slide Types

| Type | Purpose | Layout |
|------|---------|--------|
| **Title** | Opening slide | Centered title + subtitle |
| **Content** | Standard text | Heading + bullet points |
| **Split** | Side by side | Two-column layout |
| **Image** | Visual focus | Full-bleed or captioned image |
| **Code** | Code showcase | Syntax-highlighted block |
| **Quote** | Key quote | Large centered quote |
| **Comparison** | A vs B | Side-by-side cards |
| **Metrics** | KPI highlight | Large numbers + labels |
| **Section** | Chapter break | Centered section title |
| **End** | Closing slide | Thank you + contact |

## Design System

### Colors

```
Background:    #0f172a
Surface:       #1e293b
Text:          #f1f5f9
Text Muted:    #94a3b8
Accent:        #22d3ee (cyan)
Highlight:     #fbbf24 (amber)
Code BG:       #1e293b
```

### Typography

- **Slide Title**: 42px, weight 700
- **Subtitle**: 24px, weight 400, `#94a3b8`
- **Body**: 24px, weight 400, line-height 1.6
- **Bullet points**: 22px
- **Code**: 18px, `'JetBrains Mono', monospace`
- **Speaker note**: 16px

### Layout

- **Slide dimensions**: 16:9 aspect ratio (1280x720 base)
- **Content padding**: 80px horizontal, 60px vertical
- **Max content width**: 1120px
- **Bullet indent**: 40px per level

## HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{presentation-title}</title>
  <style>/* All styles embedded */</style>
</head>
<body>
  <div class="deck">
    <div class="slide" data-type="title">
      <h1>Title</h1>
      <p class="subtitle">Subtitle</p>
      <aside class="notes">Speaker notes here</aside>
    </div>
    <!-- More slides -->
  </div>
  <div class="progress-bar"><div class="progress"></div></div>
  <div class="slide-counter">1 / N</div>
  <script>/* Navigation JS */</script>
</body>
</html>
```

## Navigation (embedded JS)

| Key | Action |
|-----|--------|
| `→` / `Space` / `PageDown` | Next slide |
| `←` / `PageUp` | Previous slide |
| `Home` | First slide |
| `End` | Last slide |
| `S` | Toggle speaker notes |
| `F` | Toggle fullscreen |
| `Escape` | Exit fullscreen |

## Workflow

1. **Analyze content**: Understand the topic, key points, and flow
2. **Plan structure**: Create slide outline — ~1 slide per key point, max 15-20 slides
3. **Design slides**: Select appropriate type for each slide
4. **Write HTML**: Generate self-contained file with embedded CSS/JS
5. **Save**: Output to `./slides/{topic-slug}.html`

## Content Guidelines

- **One idea per slide** — don't overcrowd
- **6 words per bullet** max — audience reads, not you
- **3-5 bullets per slide** max
- **Use visuals** where possible — diagrams, charts, images
- **Speaker notes** for details you'll say out loud
- **Consistent progression** — tell a story, don't list facts
