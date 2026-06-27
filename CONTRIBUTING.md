# Contributing to praxis-skills

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Quick Start

1. Fork the repository
2. Create a skill directory under `skills/`
3. Add a `SKILL.md` with frontmatter (`name`, `description`)
4. Submit a pull request

## Skill Structure

```
skills/praxis-your-skill/
├── SKILL.md              # Required: main instructions
├── deps-manifest.json    # Optional: dependency declaration
├── setup.sh              # Optional: install script
├── scripts/              # Optional: helper scripts
│   └── your_script.py
└── references/           # Optional: supporting docs
    └── vendor-manifest.yaml
```

## Requirements

### SKILL.md Frontmatter

```yaml
---
name: praxis-your-skill
description: >
  What this skill does and when to use it.
  Include trigger words users might say.
---
```

### Capability Tiers

Mark each command with a tier (see [capability-tiers.md](skills/praxis-skill-forge/references/capability-tiers.md)):

| Tier | Meaning |
|------|---------|
| `CORE` | Python stdlib only, zero external deps |
| `ENHANCED` | Optional CLI tools, graceful degradation |
| `ADVANCED` | External skills or authenticated APIs |

### Dependency Lifecycle

For each external dependency, declare (see [dependency-lifecycle.md](skills/praxis-skill-forge/references/dependency-lifecycle.md)):

```json
{
  "dependencies": {
    "tool-name": {
      "type": "npm",
      "tier": "ENHANCED",
      "install": "npm install -g tool-name",
      "check": "tool-name --version",
      "update": "npm update -g tool-name",
      "platform": "cross-platform",
      "optional": true
    }
  }
}
```

### Cross-Platform Support

- Use Python 3.10+ stdlib only (no pip dependencies for CORE tier)
- Use `pathlib.Path` for all path operations
- Test on macOS, Linux, and Windows
- See [cross-platform-guide.md](skills/praxis-skill-forge/references/cross-platform-guide.md)

## Code Style

- Python: follow PEP 8
- SKILL.md: keep under 500 lines / 5,000 tokens
- Every line must change behavior (no no-ops)
- Comments in English, user-facing text in any language

## Commit Messages

**Do not add AI agent Co-Authored-By tags.** Write commit messages as a human author only. This applies to all AI tools (Claude, Codex, Copilot, GPT, Gemini, etc.).

## Pull Request Process

1. Ensure your skill follows the structure above
2. Run `python3 scripts/quick_validate.py` if available
3. Update README.md skill table if adding a new skill
4. Target the `main` branch

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
