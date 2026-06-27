---
name: open-praxis-markdown-to-html
description: Converts markdown files to beautifully styled HTML with dark/light themes, syntax highlighting, and responsive design. Use when user asks to "convert markdown to HTML", "生成HTML", "preview markdown", or wants a styled HTML version of a markdown document.
---

# Markdown to HTML

Converts markdown files to standalone, beautifully styled HTML pages.

## Features

- Dark and light theme support
- Syntax highlighting for code blocks
- Responsive design
- Table of contents generation
- Print-friendly styles
- CJK typography support

## Workflow

### Step 1: Parse Markdown

1. Read the markdown file
2. Extract YAML frontmatter (title, author, date, etc.)
3. Parse markdown content to HTML using standard CommonMark rules

### Step 2: Apply Styling

Generate a self-contained HTML file with embedded CSS:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    /* Embedded styles — no external dependencies */
  </style>
</head>
<body>
  <article class="content">
    {html-content}
  </article>
</body>
</html>
```

### Design Tokens

| Token | Light | Dark |
|-------|-------|------|
| Background | `#ffffff` | `#1a1a2e` |
| Text | `#2d3748` | `#e2e8f0` |
| Heading | `#1a202c` | `#f7fafc` |
| Link | `#3182ce` | `#63b3ed` |
| Code BG | `#f7fafc` | `#2d3748` |
| Border | `#e2e8f0` | `#4a5568` |
| Blockquote | `#edf2f7` | `#2d3748` |

### Typography

- **Body**: `'Inter', 'Noto Sans SC', -apple-system, sans-serif`, 16px/1.75
- **Headings**: `'Inter', 'Noto Sans SC', sans-serif`, weights 600-700
- **Code**: `'JetBrains Mono', 'Fira Code', monospace`, 14px
- **Max width**: 720px, centered

### Syntax Highlighting

Embed a minimal syntax highlighting theme (similar to One Dark):

| Token | Color |
|-------|-------|
| Keyword | `#c678dd` |
| String | `#98c379` |
| Number | `#d19a66` |
| Comment | `#5c6370` |
| Function | `#61afef` |
| Operator | `#56b6c2` |

### Step 3: Generate TOC

If the document has 3+ headings, generate a Table of Contents:
- Collapsible `<details>` element
- Linked to heading anchors
- Indented by heading level

### Step 4: Save

Save as `{filename}.html` in the same directory as the source markdown.

Display:
```
Markdown → HTML complete
Source: {source-path}
Output: {output-path}
Theme: dark/light (auto)
Headings: {count}
Code blocks: {count}
```
