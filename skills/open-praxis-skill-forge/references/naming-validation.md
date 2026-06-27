# Naming & Validation Rules

Source: anthropics/skills skill-creator

## Name Rules

- Regex: `^[a-z0-9-]+$`
- Max 64 chars
- No leading/trailing hyphen, no `--`
- Must match parent directory name

## Description Rules

- Max 1,536 chars
- No angle brackets (`<` `>`)
- Third person, trigger-oriented

## Allowed Frontmatter Keys

Only: `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`

Other keys (version, author, tags) → README or marketplace.json
