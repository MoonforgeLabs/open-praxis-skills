# Selective Install Modules

Source: affaan-m/ECC install modules

## Problem

Installing an entire skill collection when the user only needs one capability wastes tokens and clutters the skill directory.

## Solution: Modular Installation

Define install modules — logical groupings of skills that can be installed independently.

## Module Definition

```json
{
  "modules": {
    "analytics": {
      "description": "Usage statistics and reporting",
      "skills": ["praxis-ai-usage-stats"],
      "dependencies": ["python3"]
    },
    "search": {
      "description": "Search gateway and web research",
      "skills": ["praxis-search-hub", "praxis-url-to-markdown"],
      "dependencies": ["python3", "gh"]
    },
    "content": {
      "description": "Translation, formatting, and content creation",
      "skills": ["praxis-translate", "praxis-format-markdown", "praxis-humanizer-zh"],
      "dependencies": []
    },
    "media": {
      "description": "Image, video, and diagram tools",
      "skills": ["praxis-diagram", "praxis-compress-image", "praxis-youtube-clipper"],
      "dependencies": ["yt-dlp", "ffmpeg"]
    }
  }
}
```

## Install Commands

```bash
# Install everything
bash scripts/install.sh

# Install specific module
bash scripts/install.sh --module analytics

# Install multiple modules
bash scripts/install.sh --module search,content

# List available modules
bash scripts/install.sh --list
```

## Module Rules

1. Each skill belongs to exactly one module (no overlap)
2. Module dependencies are the union of its skills' dependencies
3. Installing a module checks all dependencies before proceeding
4. Modules are independent — installing one doesn't require another

## Application to praxis-skills

When praxis-skills grows beyond 30 skills, create `modules.json`:

```json
{
  "knowledge": {
    "skills": ["praxis-news-aggregator", "praxis-search-hub", "praxis-url-to-markdown", "praxis-youtube-transcript"]
  },
  "content": {
    "skills": ["praxis-translate", "praxis-format-markdown", "praxis-humanizer-zh", "praxis-markdown-to-html"]
  },
  "visual": {
    "skills": ["praxis-diagram", "praxis-compress-image", "praxis-slide-deck", "praxis-logo-generator"]
  }
}
```

Users install what they need, not everything.
