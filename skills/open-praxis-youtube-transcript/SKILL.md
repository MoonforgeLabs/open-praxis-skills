---
name: open-praxis-youtube-transcript
description: Downloads YouTube video transcripts/subtitles and cover images by URL or video ID. Supports multiple languages, translation, chapters, and speaker identification. Use when user asks to "get YouTube transcript", "download subtitles", "get captions", "YouTube字幕", "YouTube封面", "视频字幕", or provides a YouTube URL and wants the transcript text extracted.
---

# YouTube Transcript

Downloads transcripts (subtitles/captions) from YouTube videos. Works with both manually created and auto-generated transcripts.

## Approach

Use `yt-dlp` (preferred) or YouTube's InnerTube API to fetch transcripts. No API key required.

### Prerequisites

Check for `yt-dlp`:
```bash
which yt-dlp 2>/dev/null || echo "yt-dlp not found — install via: brew install yt-dlp"
```

## Input Formats

Accepts any of these as video input:
- Full URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Short URL: `https://youtu.be/dQw4w9WgXcQ`
- Embed URL: `https://www.youtube.com/embed/dQw4w9WgXcQ`
- Video ID: `dQw4w9WgXcQ`

**Important**: Always single-quote YouTube URLs in shell — zsh treats `?` as a glob wildcard.

## Workflow

### Step 1: Fetch Metadata & Transcript

```bash
# List available subtitles
yt-dlp --list-subs '<youtube-url>' 2>/dev/null

# Download auto-generated subtitle (English)
yt-dlp --write-auto-sub --sub-lang en --skip-download --sub-format json3 -o '%(id)s' '<youtube-url>'

# Download manual subtitle if available
yt-dlp --write-sub --sub-lang en --skip-download --sub-format json3 -o '%(id)s' '<youtube-url>'

# Fetch metadata
yt-dlp --dump-json --no-download '<youtube-url>'
```

### Step 2: Process & Format

1. Parse the JSON3 subtitle file into text segments
2. Merge segments into natural sentences (split by punctuation: `.?!。？！`)
3. Group sentences into paragraphs (by pause gaps or topic shifts)
4. If chapters exist in video description, segment by chapter boundaries

### Step 3: Generate Output

Create markdown with frontmatter:

```yaml
---
title: <video-title>
channel: <channel-name>
date: <upload-date>
url: <video-url>
duration: <HH:MM:SS>
language: <transcript-language>
---
```

Include:
- Video title as H1
- Cover image (thumbnail)
- Chapter headings (if available)
- Transcript text with optional timestamps `[HH:MM:SS]`

### Step 4: Save

Output directory structure:
```
youtube-transcript/
└── {channel-slug}/{title-slug}/
    ├── transcript.md
    └── imgs/
        └── cover.jpg
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| Language | Transcript language priority | `en` |
| Timestamps | Include timestamps | yes |
| Chapters | Segment by chapters | yes |
| Speakers | Identify speakers (AI post-processing) | no |
| Format | Output format: markdown or srt | markdown |

## Speaker Identification

When requested, after fetching the raw transcript:

1. Analyze video metadata (title, description) for speaker names
2. Detect speaker turns from conversation patterns
3. Label with `**Speaker Name:**` format
4. Group into readable paragraphs (2-4 sentences each)

## Error Cases

| Error | Meaning |
|-------|---------|
| Transcripts disabled | Video has no captions |
| No transcript found | Requested language not available |
| Video unavailable | Video deleted, private, or region-locked |
| Age restricted | Video requires login for age verification |
