---
name: open-praxis-image-cards
description: Creates styled image cards for social media sharing — knowledge summaries, quote cards, tip cards, and data highlights. Use when user asks to "make a card", "create social card", "做卡片", "知识卡片", "quote card", or needs shareable visual content cards.
---

# Image Cards

Creates beautifully styled image cards as SVG files, optimized for social media sharing.

## Card Types

| Type | Purpose | Best For |
|------|---------|----------|
| **Quote** | Highlight a memorable quote | Twitter/X, Instagram |
| **Knowledge** | Summarize a concept or fact | LinkedIn, WeChat |
| **Tip** | Share a practical tip | Instagram stories |
| **Stats** | Highlight key metrics | LinkedIn, Twitter/X |
| **Comparison** | A vs B side by side | LinkedIn, blog |
| **List** | Top N items | Instagram carousel |
| **Code** | Code snippet showcase | Twitter/X, dev community |

## Design System

### Dimensions

| Platform | Size | Aspect |
|----------|------|--------|
| Twitter/X | 1200x675 | 16:9 |
| Instagram Square | 1080x1080 | 1:1 |
| Instagram Story | 1080x1920 | 9:16 |
| LinkedIn | 1200x627 | ~1.91:1 |
| WeChat | 900x500 | ~1.8:1 |
| Default | 1200x675 | 16:9 |

### Color Themes

**Dark (default):**
```
Background:  #0f172a
Surface:     #1e293b
Text:        #f1f5f9
Muted:       #94a3b8
Accent:      #22d3ee
```

**Light:**
```
Background:  #ffffff
Surface:     #f8fafc
Text:        #1e293b
Muted:       #64748b
Accent:      #0ea5e9
```

**Gradient options:**
- Cyan→Blue: `#22d3ee → #3b82f6`
- Purple→Pink: `#a78bfa → #f472b6`
- Emerald→Cyan: `#34d399 → #22d3ee`
- Amber→Orange: `#fbbf24 → #fb923c`

### Typography

- **Title/Quote**: 32-48px, weight 700
- **Body**: 20-24px, weight 400
- **Label**: 14-16px, weight 500, muted color
- **Attribution**: 16-18px, weight 500, accent color
- **Watermark**: 12px, weight 400, very muted

### Layout Patterns

**Quote Card:**
```
┌─────────────────────────────┐
│                             │
│  ❝                          │
│  Quote text here that       │
│  wraps naturally across     │
│  multiple lines             │
│                      ❞      │
│                             │
│  — Attribution              │
│                             │
│              @handle  #tag  │
└─────────────────────────────┘
```

**Knowledge Card:**
```
┌─────────────────────────────┐
│  [Category Label]           │
│                             │
│  Title / Concept            │
│  ─────────────              │
│                             │
│  • Point one                │
│  • Point two                │
│  • Point three              │
│                             │
│  💡 Key takeaway sentence   │
│                             │
│              @handle  logo  │
└─────────────────────────────┘
```

## SVG Template

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f172a"/>
      <stop offset="100%" style="stop-color:#1e293b"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="1200" height="675" fill="url(#bg)"/>

  <!-- Content area (80px padding) -->
  <g transform="translate(80, 60)">
    <!-- Card content here -->
  </g>

  <!-- Watermark -->
  <text x="1120" y="650" fill="#475569" font-size="12" text-anchor="end">@praxis</text>
</svg>
```

## Workflow

1. **Understand content**: Extract the key message, quote, or data
2. **Select card type**: Match content to best card format
3. **Choose platform**: Determine dimensions based on target platform
4. **Generate SVG**: Create self-contained SVG with embedded styles
5. **Save**: Output to `./cards/{descriptive-slug}.svg`

## Text Wrapping

SVG doesn't auto-wrap text. Manually split long text into `<tspan>` elements:

```svg
<text x="80" y="200" fill="#f1f5f9" font-size="36" font-weight="700">
  <tspan x="80" dy="0">First line of the quote</tspan>
  <tspan x="80" dy="48">that wraps to second line</tspan>
  <tspan x="80" dy="48">and maybe a third</tspan>
</text>
```

Rule of thumb: ~30-35 characters per line at 36px for 1200px wide cards.
