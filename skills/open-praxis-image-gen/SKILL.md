---
name: open-praxis-image-gen
description: Generates images using AI image generation APIs or creates SVG illustrations programmatically. Use when user asks to "generate image", "create illustration", "生成图片", "画一个", or needs custom visual assets.
---

# Image Generator

Generates images via AI APIs or creates SVG illustrations programmatically.

## Approaches

### 1. SVG Illustration (No API needed)

For diagrams, icons, abstract art, patterns, and simple illustrations — generate directly as SVG:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea"/>
      <stop offset="100%" style="stop-color:#764ba2"/>
    </linearGradient>
  </defs>
  <rect width="800" height="600" fill="url(#bg)"/>
  <!-- Content -->
</svg>
```

### 2. AI Image Generation (API required)

For photorealistic images, complex scenes, or artistic styles — use available AI image APIs.

**Supported APIs** (check availability):
- OpenAI DALL-E (`openai` CLI or API)
- Stable Diffusion (local or API)
- Other available image generation MCP tools

## Prompt Engineering

When generating prompts for AI image APIs:

### Structure
```
[Subject], [Style], [Composition], [Lighting], [Details], [Quality modifiers]
```

### Style Keywords

| Style | Keywords |
|-------|----------|
| Photorealistic | `photorealistic, 8k, detailed, sharp focus` |
| Illustration | `digital illustration, clean lines, vibrant colors` |
| Minimalist | `minimalist, clean, simple, whitespace` |
| Technical | `technical drawing, blueprint style, precise` |
| Watercolor | `watercolor painting, soft edges, flowing colors` |
| Isometric | `isometric view, 3d illustration, flat shading` |

### Quality Modifiers
- `high quality, detailed, professional`
- `4k, 8k resolution`
- `studio lighting, soft shadows`
- `sharp focus, bokeh background`

## Workflow

1. **Understand the request**: What image is needed and for what purpose?
2. **Choose approach**: SVG for simple/technical, AI API for complex/photorealistic
3. **Generate**:
   - SVG: Write the SVG file directly
   - AI: Craft prompt, call API, save result
4. **Save**: Output to `./images/{descriptive-slug}.{svg|png}`
5. **Offer variants**: Ask if adjustments are needed

## Output

- **SVG**: Self-contained, scalable, editable
- **PNG/JPEG**: From AI APIs, typically 1024x1024 or higher
- **Save location**: `./images/` directory by default
