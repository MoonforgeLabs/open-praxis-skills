---
name: open-praxis-infographic
description: Create data-driven infographics as standalone SVG or HTML files. Supports KPI dashboards, timelines, comparisons, funnels, SWOT analysis, and process flows. Use when user asks to "create infographic", "make infographic", "信息图", "数据可视化", or wants visual summaries of data/processes.
---

# Infographic Generator

Creates visually compelling infographics as self-contained SVG or HTML files.

## Supported Types

| Type | When to Use | Layout |
|------|-------------|--------|
| **KPI Dashboard** | Key metrics overview | Grid of metric cards |
| **Timeline** | Chronological events | Vertical/horizontal progression |
| **Comparison** | A vs B analysis | Side-by-side columns |
| **Funnel** | Conversion or pipeline | Narrowing stages |
| **SWOT** | Strategic analysis | 2x2 quadrant grid |
| **Process Flow** | Step-by-step workflow | Connected stages |
| **Statistics** | Data highlights | Mixed charts + callouts |
| **Roadmap** | Feature/project planning | Horizontal swim lanes |

## Design System

### Color Palette (Dark Theme)

```
Background:   #0f172a
Surface:      #1e293b
Card:         #334155
Text Primary: #f1f5f9
Text Muted:   #94a3b8
Accent 1:     #22d3ee (cyan)
Accent 2:     #34d399 (emerald)
Accent 3:     #a78bfa (violet)
Accent 4:     #fbbf24 (amber)
Accent 5:     #fb7185 (rose)
Accent 6:     #fb923c (orange)
```

### Typography

- **Title**: 28-32px, weight 700, `#f1f5f9`
- **Section heading**: 18-20px, weight 600
- **Metric value**: 36-48px, weight 700, accent color
- **Label**: 12-14px, weight 500, `#94a3b8`
- **Body**: 14px, weight 400
- **Font**: `'Inter', 'Noto Sans SC', -apple-system, sans-serif`

### Visual Elements

**Metric Card:**
```svg
<rect x="X" y="Y" width="200" height="120" rx="12" fill="#1e293b" stroke="#334155" stroke-width="1"/>
<text x="CX" y="Y+35" fill="#94a3b8" font-size="13" text-anchor="middle">Revenue</text>
<text x="CX" y="Y+70" fill="#22d3ee" font-size="36" font-weight="700" text-anchor="middle">$2.4M</text>
<text x="CX" y="Y+95" fill="#34d399" font-size="12" text-anchor="middle">↑ 23% vs last quarter</text>
```

**Progress Bar:**
```svg
<rect x="X" y="Y" width="300" height="8" rx="4" fill="#334155"/>
<rect x="X" y="Y" width="210" height="8" rx="4" fill="#22d3ee"/>
```

**Divider:**
```svg
<line x1="X1" y1="Y" x2="X2" y2="Y" stroke="#334155" stroke-width="1"/>
```

## Workflow

1. **Understand the data**: Extract key metrics, categories, and relationships from user input
2. **Select layout**: Pick the best infographic type based on the data structure
3. **Plan composition**: Sketch sections — title area, main content, supporting details, footer
4. **Generate SVG/HTML**: Build the self-contained file with embedded styles
5. **Save**: Output to `./infographic/{topic-slug}.svg` (or `.html` for interactive elements)

## Output Rules

1. **Self-contained**: No external dependencies (embed fonts via Google Fonts import or use system fonts)
2. **Responsive viewBox**: Set `viewBox` to fit content, no fixed `width`/`height`
3. **CJK support**: Use `'Noto Sans SC', 'PingFang SC'` fallback fonts, wider boxes for Chinese text
4. **Accessibility**: Include `<title>` and `<desc>` elements in SVG
5. **Print friendly**: Use sufficient contrast ratios
