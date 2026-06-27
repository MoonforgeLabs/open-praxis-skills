---
name: open-praxis-cover-image
description: Creates article cover images and blog post hero images as SVG. Use when user asks for "cover image", "封面图", "hero image", "blog cover", "文章配图", or needs a visual header for an article or blog post.
---

# Cover Image Generator

Creates stunning article cover images as self-contained SVG files.

## Styles

| Style | Description | Best For |
|-------|-------------|----------|
| **Gradient** | Bold gradient background + typography | Blog posts, newsletters |
| **Geometric** | Abstract geometric shapes + text | Tech articles, dev blogs |
| **Minimal** | Clean, lots of whitespace | Professional, corporate |
| **Dark** | Dark background + accent colors | Dev.to, personal blogs |
| **Split** | Image area + text area | Tutorial, how-to |
| **Pattern** | Repeating pattern background | Series branding |

## Dimensions

| Platform | Size | Aspect |
|----------|------|--------|
| Blog/OG | 1200x630 | ~1.91:1 |
| Twitter | 1200x675 | 16:9 |
| Dev.to | 1000x420 | ~2.38:1 |
| Medium | 1400x788 | 16:9 |
| Default | 1200x630 | ~1.91:1 |

## Design System

### Gradients

```svg
<!-- Tech/Coding -->
<linearGradient id="tech" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" style="stop-color:#667eea"/>
  <stop offset="100%" style="stop-color:#764ba2"/>
</linearGradient>

<!-- Nature/Growth -->
<linearGradient id="growth" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" style="stop-color:#11998e"/>
  <stop offset="100%" style="stop-color:#38ef7d"/>
</linearGradient>

<!-- Warm/Creative -->
<linearGradient id="warm" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" style="stop-color:#ee0979"/>
  <stop offset="100%" style="stop-color:#ff6a00"/>
</linearGradient>

<!-- Dark/Professional -->
<linearGradient id="dark" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" style="stop-color:#0f172a"/>
  <stop offset="100%" style="stop-color:#1e3a5f"/>
</linearGradient>

<!-- Ocean/Calm -->
<linearGradient id="ocean" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" style="stop-color:#2193b0"/>
  <stop offset="100%" style="stop-color:#6dd5ed"/>
</linearGradient>
```

### Typography

- **Title**: 48-64px, weight 700-800, white or light color
- **Subtitle**: 24-28px, weight 400, slightly transparent white
- **Tag/Category**: 14-16px, weight 600, uppercase, accent color
- **Author**: 18px, weight 500

### Decorative Elements

**Geometric shapes** for visual interest:
```svg
<!-- Floating circles -->
<circle cx="900" cy="150" r="80" fill="rgba(255,255,255,0.05)"/>
<circle cx="1050" cy="400" r="120" fill="rgba(255,255,255,0.03)"/>

<!-- Grid dots -->
<pattern id="dots" width="30" height="30" patternUnits="userSpaceOnUse">
  <circle cx="15" cy="15" r="1.5" fill="rgba(255,255,255,0.1)"/>
</pattern>

<!-- Diagonal lines -->
<pattern id="lines" width="20" height="20" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
  <line x1="0" y1="0" x2="0" y2="20" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
</pattern>
```

## Template: Gradient Style

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea"/>
      <stop offset="100%" style="stop-color:#764ba2"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" fill="url(#bg)"/>

  <!-- Decorative elements -->
  <circle cx="1000" cy="100" r="200" fill="rgba(255,255,255,0.05)"/>
  <circle cx="1100" cy="500" r="150" fill="rgba(255,255,255,0.03)"/>

  <!-- Category tag -->
  <rect x="80" y="180" width="120" height="30" rx="15" fill="rgba(255,255,255,0.2)"/>
  <text x="140" y="200" fill="white" font-size="13" font-weight="600" text-anchor="middle" letter-spacing="1">TUTORIAL</text>

  <!-- Title (manual line breaks for wrapping) -->
  <text x="80" y="280" fill="white" font-size="52" font-weight="700" font-family="'Inter', sans-serif">
    <tspan x="80" dy="0">Article Title That</tspan>
    <tspan x="80" dy="64">Wraps to Two Lines</tspan>
  </text>

  <!-- Subtitle -->
  <text x="80" y="430" fill="rgba(255,255,255,0.7)" font-size="24" font-weight="400">A brief description of the article</text>

  <!-- Author -->
  <text x="80" y="560" fill="rgba(255,255,255,0.6)" font-size="18" font-weight="500">Alex</text>
</svg>
```

## Workflow

1. **Extract info**: Get title, subtitle/description, category, author from the article or user
2. **Select style**: Match to content tone (tech→geometric, personal→gradient, etc.)
3. **Choose gradient**: Pick colors that match the content mood
4. **Generate SVG**: Create self-contained file
5. **Save**: Output to `{article-dir}/imgs/cover.svg` or `./covers/{slug}.svg`

## Text Wrapping Rules

- Max ~20-25 characters per line at 52px
- Max ~30-35 characters per line at 36px
- Use `<tspan>` elements with `dy` for line spacing
- Title should be 1-3 lines max
- Break at natural word boundaries
