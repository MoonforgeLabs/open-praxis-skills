---
name: open-praxis-compress-image
description: Compresses images to WebP (default) or PNG/JPEG with automatic tool selection. Use when user asks to "compress image", "optimize image", "convert to webp", "压缩图片", or reduce image file size.
---

# Image Compressor

Compresses images using the best available tool on the system.

## Tool Selection Priority

1. **sips** (macOS built-in) — fast, no install needed
2. **cwebp** (Google WebP tools) — best WebP compression
3. **ImageMagick** (convert) — universal format support
4. **Sharp** (Node.js) — programmatic fallback

## Usage

Detect available tools and use the best one:

```bash
# Check available tools
which sips cwebp convert 2>/dev/null

# sips (macOS) — convert to specified format
sips -s format webp --setProperty formatOptions 80 input.png --out output.webp

# cwebp — WebP compression
cwebp -q 80 input.png -o output.webp

# ImageMagick — universal
convert input.png -quality 80 output.webp
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| Format | `webp` | Output format: webp, png, jpeg |
| Quality | `80` | Quality 0-100 |
| Keep original | `false` | Keep original file |
| Recursive | `false` | Process subdirectories |

## Workflow

1. **Detect input**: single file or directory
2. **Select tool**: pick best available from priority list
3. **Compress**: apply format and quality settings
4. **Report**: show before/after size and reduction percentage

```
image.png → image.webp (245KB → 89KB, 64% reduction)
```

## Batch Processing

For directories, process all image files (`*.png`, `*.jpg`, `*.jpeg`, `*.gif`, `*.bmp`, `*.tiff`):

```bash
find ./images -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) -exec <compress-command> {} \;
```

Report total savings at the end.

## Preferences (EXTEND.md)

Check EXTEND.md in priority order:

| Priority | Path | Scope |
|----------|------|-------|
| 1 | `.praxis-skills/praxis-compress-image/EXTEND.md` | Project |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/praxis-skills/praxis-compress-image/EXTEND.md` | XDG |
| 3 | `$HOME/.praxis-skills/praxis-compress-image/EXTEND.md` | User home |

**Supports**: Default format, default quality, keep-original preference.
