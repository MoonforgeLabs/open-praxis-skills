# Distribution Templates

Use these templates when generating distribution artifacts for org/public versions.

## Skill README.md Template

```markdown
# {SKILL_NAME}

> One-line description matching frontmatter.

## What it does

2-3 sentences explaining the skill's purpose.

## Install

### Claude Code
\`\`\`bash
# Option 1: Clone and symlink
git clone <repo-url> /tmp/{SKILL_NAME}
ln -s /tmp/{SKILL_NAME} ~/.claude/skills/{SKILL_NAME}

# Option 2: Copy
cp -r {SKILL_NAME} ~/.claude/skills/
\`\`\`

### Prerequisites
\`\`\`bash
brew install yt-dlp
pip install pysrt
\`\`\`

## Usage

\`\`\`
/{SKILL_NAME} <args>
\`\`\`

## Dependencies

| Dependency | Required | Install | Without it |
|------------|----------|---------|------------|
| yt-dlp | Yes | brew install yt-dlp | Skill won't work |
| pysrt | No | pip install pysrt | Manual subtitle editing |

## Compatibility

- Claude Code ✅
- Codex ✅
- OpenCode / OpenHuman ✅ (pure Markdown)

## License

MIT
```

## Repo INSTALL.md Template

For repos with 2+ skills:

```markdown
# Install Guide

## All skills
\`\`\`bash
git clone <repo-url> && cd {REPO_NAME}
bash scripts/install.sh
\`\`\`

## Single skill
\`\`\`bash
cp -r skills/{SKILL_NAME} ~/.claude/skills/
\`\`\`

## Dependencies

### Required (install before use)
\`\`\`bash
brew install yt-dlp ffmpeg-full
\`\`\`

### Optional (enhances functionality)
\`\`\`bash
pip install pysrt pdfplumber
\`\`\`
```

## delta-tracker.yaml Template

```yaml
# dist/delta-tracker.yaml
# Tracks divergence between personal → org/public versions

{SKILL_NAME}:
  type: skill
  source: skills/{SKILL_NAME}/SKILL.md
  org:
    target: org/skills/{ORG_NAME}/
    status: adapted | exact_copy | excluded
    changes:
      - "description of change"
    last_sync: YYYY-MM-DD
    source_hash: {md5}
  public:
    target: public/skills/{PUB_NAME}/
    status: adapted | exact_copy | excluded
    changes:
      - "description of change"
    last_sync: YYYY-MM-DD
    source_hash: {md5}
```
