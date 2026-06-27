---
name: open-praxis-url-to-markdown
description: Fetch any URL and convert to clean markdown. Handles general webpages, X/Twitter threads, YouTube transcripts, and Hacker News threads. Use when user wants to save a webpage as markdown, "抓取网页", "save page as markdown", or provides a URL to extract content from.
---

# URL to Markdown

Fetches any URL and converts it to clean, well-formatted markdown.

## User Input Tools

When this skill prompts the user, follow this tool-selection rule (priority order):

1. **Prefer built-in user-input tools** exposed by the current agent runtime — e.g., `AskUserQuestion`, `request_user_input`, `clarify`, `ask_user`, or any equivalent.
2. **Fallback**: if no such tool exists, emit a numbered plain-text message and ask the user to reply with the chosen number/answer.

## Preferences (EXTEND.md)

Check EXTEND.md in priority order — the first one found wins:

| Priority | Path | Scope |
|----------|------|-------|
| 1 | `.praxis-skills/praxis-url-to-markdown/EXTEND.md` | Project |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/praxis-skills/praxis-url-to-markdown/EXTEND.md` | XDG |
| 3 | `$HOME/.praxis-skills/praxis-url-to-markdown/EXTEND.md` | User home |

**EXTEND.md supports**: download media by default, default output directory.

### First-Time Setup (BLOCKING)

When EXTEND.md is not found, use `AskUserQuestion` to gather preferences:

- **Media handling**: Ask each time / Always download / Never download
- **Output directory**: Default `./url-to-markdown/{domain}/{slug}.md` or custom
- **Save location**: User-level (`~/.praxis-skills/`) or project-level (`.praxis-skills/`)

## Workflow

1. **Fetch the URL** using available tools (WebFetch, curl, or browser automation)
2. **Extract main content** — strip navigation, ads, sidebars, footers
3. **Convert to markdown** — preserve headings, lists, code blocks, images, links
4. **Add frontmatter** with metadata:
   ```yaml
   ---
   sourceUrl: <original-url>
   title: <page-title>
   author: <if-available>
   date: <publish-date-if-available>
   fetchedAt: <current-timestamp>
   ---
   ```
5. **Handle media** based on preferences:
   - `ask`: prompt user after save
   - `always`: download images/videos to local `imgs/` directory, rewrite markdown links
   - `never`: keep remote URLs
6. **Save** to output path: `{base_dir}/{domain}/{slug}/{slug}.md`

## Output Path Generation

1. Base directory from EXTEND.md `default_output_dir` or default `./url-to-markdown/`
2. Extract domain from URL (e.g., `example.com`)
3. Generate slug from URL path or page title (kebab-case, 2-6 words)
4. Construct: `{base_dir}/{domain}/{slug}/{slug}.md`
5. Conflict resolution: append timestamp

## Quality Gate

After fetching, inspect the saved markdown:
- Content should be substantial (not just navigation or error pages)
- Images should have alt text where possible
- Links should be preserved and functional
- Code blocks should have language annotations

If content looks incomplete or suspicious (login walls, CAPTCHA), inform the user and suggest alternatives.

## Site-Specific Handling

| Site | Approach |
|------|----------|
| X/Twitter | Extract thread text, embed media links, preserve reply chain |
| YouTube | Extract description, metadata; for transcript use praxis-youtube-transcript skill |
| Hacker News | Extract post + top comments in threaded format |
| Generic | Use readability extraction (Mozilla Readability algorithm) |
