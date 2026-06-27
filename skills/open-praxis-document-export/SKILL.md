---
name: open-praxis-document-export
description: Comprehensive authorized document export and packaging. Use when the user asks to download, archive, export full text, preserve images, save browser-viewable documents, export PDFs, package screenshots/images, or build a local knowledge copy from accessible webpages, logged-in docs, local HTML, PDFs, screenshots, or asset folders.
---

# Alex Document Export

Export accessible documents into a local package for backup, migration, learning, PixelRAG indexing, or MoonForge knowledge ingestion. Default exports go under `<WORKSPACE>/document-exports`. Default merged human view is `readable.html` inside the same package.

## Authorization Boundary

Proceed when the user confirms they have permission to download, copy, back up, migrate, or archive the document. Do not bypass access controls, paywalls, DRM, CAPTCHA, anti-bot systems, or technical restrictions. Use normal authenticated browser access, official export APIs, user-provided files, or the user's saved HTML/PDF/screenshots.

## Public / Private Boundary

Use `<WORKSPACE>/praxis-local-configs/docs/moonforge-public-private-boundary.md` when deciding where exported content belongs. The Skill code and package format are `public-extension`; exported document packages are `private-knowledge` by default. Treat Feishu/company docs, private PDFs, screenshots, source URLs, and generated `pixelrag-manifest.json` as private unless the user explicitly marks them public-safe.

Do not commit generated packages, `assets/`, source PDFs, or visual indexes into public repositories by default.

## Choose the Route

| Source type | Preferred route | Script |
| --- | --- | --- |
| Public/static webpage | Fetch URL, export Markdown/HTML/images | `scripts/export_url.py` |
| Logged-in or JS-heavy page | User saves rendered HTML or official export, then package | `scripts/export_url.py` on local file |
| PDF | Extract page text and optional source copy | `scripts/export_pdf.py` |
| Screenshots/images/assets | Copy into package with manifest and Markdown gallery | `scripts/package_assets.py` |
| Diagrams/whiteboards/architecture images | Export via official image/PDF route or browser screenshot, then attach to package | `scripts/attach_visual_assets.py` |
| Official export available | Prefer official export first, then normalize/package | depends on exported format |
| PixelRAG follow-up | Prepare visual indexing manifest for diagrams/tables/screenshots | `scripts/pixelrag_prepare.py` |

## Output Package Shape

Default output is one self-contained document package. Keep AI-readable source and user-readable renderings together:

```text
exported-doc/
├── document.md          # canonical AI-readable Markdown
├── document.html        # optional cleaned/source HTML
├── readable.html        # recommended single-file human view, images embedded
├── document.docx        # optional, only when user asks for Word
├── document.pdf         # optional, only when user asks for PDF
├── metadata.json        # source, timestamps, assets, hashes
└── assets/              # images/source files/screenshots
```

Default recommendation:

- Save `document.md` + `assets/` + `metadata.json` for AI analysis and provenance.
- Generate `readable.html` by default for user viewing/sharing.
- Generate DOCX/PDF only on request, for delivery or offline reading.



## Environment Check

Run this before first use or when DOCX/PDF/PDF-input conversion behaves unexpectedly:

```bash
python3 scripts/doctor.py
```

Dependency model:

- Bundled scripts cover the core workflow: export/package text, local images, metadata, and `readable.html`.
- Python standard library is enough for URL/local HTML basics, asset packaging, and HTML rendering.
- Optional PDF input extraction uses `pdfplumber` first and `pypdf` as fallback. Use the Codex bundled Python runtime when system Python lacks these modules.
- Optional DOCX/PDF outputs use `pandoc` when available; DOCX can fall back to macOS `textutil`, and PDF can fall back to Chrome/Edge/Chromium headless printing.
- Optional richer DOCX generation can use `python-docx`; it is not required for the default package workflow.
- PixelRAG is not bundled and is not part of default export; use `scripts/pixelrag_prepare.py` later only when the package needs visual retrieval over screenshots, diagrams, tables, charts, or UI images.

Install hints when needed:

```bash
brew install pandoc
python3 -m pip install pdfplumber pypdf python-docx
```

## Recommended Use

Default workflow for one link or one source file:

1. Create one package under `<WORKSPACE>/document-exports/<title-or-id>/`.
2. Keep `document.md`, `assets/`, and `metadata.json` as the canonical AI-readable archive.
3. Generate `readable.html` in the same package by default for quick viewing and sharing.
4. Do not generate DOCX/PDF by default; create `document.docx` only when a user needs Word/WPS editing, and `document.pdf` only for fixed-layout delivery or archival.

Editing/viewing guidance:

- Open the whole package folder in VS Code, Cursor, Windsurf, Obsidian, Typora, or another Markdown-aware editor.
- Preview `document.md` to see normal local images referenced from `assets/`.
- Open `readable.html` for browser viewing or lightweight sharing.
- Keep `document.md` and `assets/` together; copying only the `.md` file breaks image rendering.
- Preserve valuable diagrams as files under `assets/diagrams/` or `assets/visuals/` when available; Markdown should reference them rather than trying to encode complex diagrams inline.

## Webpage / HTML Export

Use for public pages or local saved HTML files:

```bash
python3 scripts/export_url.py "https://example.com/doc" --images --html
python3 scripts/export_url.py ./saved-page.html --images --html
python3 scripts/export_url.py "https://example.com/doc" --out ./my-custom-export --images --html
```

Options:

- `--out DIR`: output package directory. If omitted, use the default myWiki export root.
- `--images`: download/copy image assets and rewrite Markdown links.
- `--html`: also save cleaned/source HTML as `document.html`; `readable.html` is generated regardless.
- `--title TITLE`: override title.

For logged-in pages: open the page in the browser with your normal account, use the browser's save/export feature if available, then run the script on the saved HTML file. If the page is lazy-loaded, scroll/load all relevant content before saving.

## PDF Export

Use the bundled Codex Python runtime if system Python lacks `pdfplumber`/`pypdf`:

```bash
<CACHE_DIR>/codex-primary-runtime/dependencies/python/bin/python3 \
  scripts/export_pdf.py ./document.pdf --copy-source
```

Output:

- `document.md` with page sections.
- `readable.html` for browser viewing.
- `metadata.json` with page counts and extraction backend.
- optional `assets/source.pdf` when `--copy-source` is used.

## Screenshot / Image Package

Use when you already have screenshots or exported images:

```bash
python3 scripts/package_assets.py ./screenshots --recursive --title "Product docs screenshots"
```

This creates a Markdown gallery, `metadata.json` with hashes and content types, and `readable.html` for viewing.

## Diagrams / Architecture Image Fidelity

Some tools return diagrams as placeholders such as `<diagram type="1"/>`, `<whiteboard .../>`, or readonly embedded canvases. Do not treat a placeholder-only export as complete when the user needs architecture diagrams preserved.

Use this priority order:

1. Official export/download for diagrams or PDF export of the full document.
2. API-provided image/whiteboard token, if available.
3. Browser screenshot of the exact diagram region or full page, using the user's normal access.
4. Attach the exported visual assets to the existing package.

Attach screenshots or diagram images to an existing package:

```bash
python3 scripts/attach_visual_assets.py <WORKSPACE>/document-exports/example-doc ./diagram-screenshots --recursive --replace-placeholders
```

This copies images into `assets/visuals/`, updates `document.md`, and records `visualAssets` in `metadata.json`.

For Feishu/Lark docs:

- Prefer `fetch_doc(..., need_url=true)` first.
- If the returned Markdown contains `<diagram type="1"/>` without a downloadable token, export the doc as PDF or capture the diagram region in the browser.
- Run `attach_visual_assets.py` to place the diagram images next to placeholders.


## Merge Package to One File

Use when the user wants a single shareable file after exporting a package. Default to HTML only unless the user explicitly asks for Word/PDF/all formats:

```bash
python3 scripts/bundle_to_doc.py <WORKSPACE>/document-exports/example-doc
python3 scripts/bundle_to_doc.py <WORKSPACE>/document-exports/example-doc --format docx
python3 scripts/bundle_to_doc.py <WORKSPACE>/document-exports/example-doc --format pdf
python3 scripts/bundle_to_doc.py <WORKSPACE>/document-exports/example-doc --format all
```

Behavior:

- Default export scripts create `readable.html`; this merge script can regenerate it or create optional DOCX/PDF.
- By default, merged outputs are written into the same export package directory.
- DOCX uses `pandoc` when available, otherwise macOS `textutil`.
- PDF uses `pandoc` when available, otherwise headless Chrome/Edge/Chromium.
- If DOCX/PDF tooling is unavailable, report the generated `readable.html` path and tell the user which converter is missing.

## Quality Gate

After exporting, inspect:

- `document.md` contains substantial body content, not just nav/login text.
- `metadata.json` has correct source and timestamp.
- Images are present under `assets/` and Markdown links are local.
- Diagram/whiteboard placeholders have matching visual assets, or the report clearly says they are still placeholders.
- Tables/code blocks are usable enough for downstream indexing.
- If content is incomplete, note whether the page required scrolling, browser session, official export, or PDF source.

## PixelRAG / Visual RAG Follow-up

PixelRAG is a downstream visual retrieval layer, not the default exporter. Do not run PixelRAG for every document. Use it when the value is in visual layout or images: architecture diagrams, flowcharts, dense tables, charts, UI screenshots, scanned pages, or slides.

Prepare a PixelRAG handoff manifest after the canonical package exists:

```bash
python3 scripts/pixelrag_prepare.py <WORKSPACE>/document-exports/example-doc
python3 scripts/pixelrag_prepare.py <WORKSPACE>/document-exports/example-doc --include-html --include-pdf
```

This writes `pixelrag-manifest.json` into the same package. It lists visual candidates, hashes, content types, reasons, and recommended tile settings. It does not run PixelRAG itself.

Recommended handoff:

1. Export one canonical package with `document.md`, `assets/`, `metadata.json`, and `readable.html`.
2. Ensure valuable visual assets are present under `assets/diagrams/`, `assets/visuals/`, or `assets/`.
3. If available, keep source PDF or official visual export in `assets/source.pdf` or `assets/originals/`.
4. Run `pixelrag_prepare.py` to create `pixelrag-manifest.json`.
5. Run a separately installed PixelRAG-compatible visual indexer against the manifest.
6. Store generated tiles/index next to the package or in a separate visual index store, preserving references back to `packagePath` and `candidate.path`.
7. Do not replace the canonical Markdown package with vector/index artifacts.

Current status: PixelRAG is tracked as a learning/monitoring candidate, but this Skill does not bundle PixelRAG code or require it for normal export.

## When Reporting Results

Tell the user:

- Output directory.
- Number of images/assets copied.
- Whether source was URL, local HTML, PDF, or screenshots.
- Any missing/failed images.
- Whether the export looks complete or needs browser/manual export.
