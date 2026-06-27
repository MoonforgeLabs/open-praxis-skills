---
name: open-praxis-logo-generator
description: >
  Generate professional SVG logos for products and brands. Supports geometric patterns,
  dot matrix designs, line systems, and mixed compositions. Use when user asks to
  "design a logo", "create logo", "做logo", "设计标志", or needs brand identity visuals.
---

# Logo Generator

Generate professional SVG logos and showcase presentations for products and brands.

## Workflow

### Phase 1: Information Gathering

Collect essential information from the user:

1. **Product/Brand Name** (required)
2. **Industry/Category** (e.g., AI, fintech, design tools)
3. **Core Concept** (e.g., connection, flow, security, simplicity)
4. **Design Preferences**:
   - Style: minimal/complex, geometric/organic
   - Color preference: monochrome/specific colors
   - Mood: cold/warm, professional/friendly

Ask concise questions. Don't overwhelm with too many questions at once.

### Phase 2: SVG Generation

Based on gathered information:

1. **Generate at least 6 design variants**
   - Use different pattern types for diversity
   - Include both single-pattern and mixed-pattern compositions
   - Vary complexity levels
   - Each variant should feel distinctly different
   - Explain the design rationale for each

2. **Generate SVG code** for each variant
   - Use `viewBox="0 0 100 100"` for easy scaling
   - Keep code clean and well-structured
   - Use `currentColor` for flexible color control

3. **Create interactive showcase webpage**
   - Display all 6+ variants in a grid layout
   - Include hover effects and smooth transitions
   - Add design rationale for each variant

### Phase 3: Iteration & Refinement

Allow user to provide feedback:
- Select favorite variants (narrow down to 2-3)
- Adjust parameters (size, spacing, rotation)
- Combine elements from different variants
- Change colors or add gradients

### Phase 4: Delivery

Provide:
- Interactive HTML showcase page
- SVG files (editable vector format)
- PNG exports if requested

## Design Patterns

### Geometric Patterns
- **Concentric circles**: Radiating rings of dots or lines
- **Polygons**: Triangles, hexagons, pentagons with variations
- **Grid systems**: Regular or irregular dot/line grids
- **Symmetry**: Rotational or reflective symmetry

### Dot Matrix Designs
- **Circular arrangements**: Dots in concentric rings
- **Gradient density**: Varying dot sizes for depth
- **Negative space**: Using absence of dots to create shapes

### Line Systems
- **Parallel lines**: With varying spacing or thickness
- **Intersecting lines**: Creating geometric patterns
- **Curved paths**: Bezier curves forming organic shapes
- **Network nodes**: Connected dots suggesting relationships

### Mixed Compositions
- **Shape + typography**: Geometric form integrated with lettermark
- **Layered elements**: Multiple patterns at different opacities
- **Contained designs**: Patterns within geometric boundaries

## SVG Best Practices

```svg
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <g>
    <!-- Use semantic grouping -->
    <!-- Leverage <defs> for reusable elements -->
    <!-- Use <clipPath> for masking effects -->
    <!-- Prefer geometric primitives over complex paths -->
  </g>
</svg>
```

## Common Templates

### Concentric Circle Dots
```svg
<svg viewBox="0 0 100 100">
  <circle cx="50" cy="38" r="3" fill="currentColor"/>
  <!-- More dots in circular arrangement -->
</svg>
```

### Geometric Shape with Line Accent
```svg
<svg viewBox="0 0 100 100">
  <polygon points="50,30 70,60 30,60" fill="none" stroke="currentColor" stroke-width="2"/>
  <circle cx="50" cy="30" r="4" fill="currentColor"/>
</svg>
```

### Node Network
```svg
<svg viewBox="0 0 100 100">
  <path d="M 30 70 Q 50 70, 50 50 T 70 30" stroke="currentColor" stroke-width="2" fill="none"/>
  <circle cx="30" cy="70" r="4" fill="currentColor"/>
  <circle cx="50" cy="50" r="5" fill="currentColor"/>
  <circle cx="70" cy="30" r="4" fill="currentColor"/>
</svg>
```

## Key Principles

1. **Provide Variety**: At least 6 distinct variants
2. **Start Simple**: Begin with basic patterns, add complexity when needed
3. **Meaningful Design**: Connect visual elements to product concepts
4. **Scalability**: Ensure logos work at all sizes (favicon to billboard)
5. **Professional Quality**: Match high-end brand identity standards

## Credits

Inspired by [op7418/logo-generator-skill](https://github.com/op7418/logo-generator-skill).
