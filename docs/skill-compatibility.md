# Skill Compatibility Guide

This repository aims to keep Alex skills portable across mainstream coding agents and skill/plugin runtimes, including Codex, Claude Code, OpenCode, Gemini CLI, and other Markdown-skill compatible tools.

## Compatibility Goals

A skill should be:

- Markdown-first.
- Useful even when optional helper scripts are unavailable.
- Safe to install into multiple agents.
- Free of hard dependencies on one proprietary runtime unless explicitly documented.
- Free of secrets and machine-specific credentials.

## Lowest Common Denominator

Use this baseline for every `SKILL.md`:

```yaml
---
name: praxis-example
description: Clear trigger-oriented description. Include what the skill does and when to use it.
---
```

Avoid frontmatter keys that are not broadly supported, especially:

```yaml
version: 0.1.0
```

Codex validation currently accepts `name` and `description` as the safest portable baseline. Keep extra metadata in README, plugin manifests, or separate agent-specific files instead of `SKILL.md` frontmatter.

## Repository Layout

Preferred layout:

```text
skills/<skill-name>/
├── SKILL.md
├── references/        # optional public-safe docs
├── scripts/           # optional helper scripts
└── assets/            # optional templates/assets
```

Keep the Skill usable after reading only `SKILL.md`. References and scripts should improve reliability, not be mandatory for basic reasoning.

## Cross-Agent Rules

### Codex

- Requires conservative frontmatter.
- Validate with `quick_validate.py` when available.
- Avoid assuming Claude-only tools or directives.
- Prefer explicit shell commands and file paths.

### Claude Code

- Can install via Claude plugin manifest.
- Register skills in `.claude-plugin/marketplace.json`.
- Keep `SKILL.md` portable even if the plugin manifest has richer metadata.

### OpenCode / Gemini CLI / Other Agents

- Assume they can read Markdown instructions but may not support plugin-specific metadata.
- Keep workflow steps explicit and tool-agnostic.
- Avoid referencing unavailable tool names as requirements.
- Provide fallback manual steps when scripts or MCP tools are unavailable.

## Script Rules

Bundled scripts should:

- Be optional helpers, not the only source of truth.
- Use environment variables for local paths.
- Avoid hard-coded usernames, private paths, or secrets.
- Fail clearly with actionable messages.
- Avoid printing secret values.

## Secret Rules

Never include these in `praxis-skills`:

- `.env`
- tokens
- webhook URLs
- API keys
- SOPS age private keys
- encrypted personal project secrets such as `secrets.env.enc`
- runtime reports, state, logs, or caches

Put sensitive project config in a private config repository such as `praxis-local-configs`, encrypted when appropriate.

## Local Path Rules

Prefer environment variables:

```bash
WATCHTOWER_PROJECT_DIR
WATCHTOWER_CONFIG
WATCHTOWER_LAUNCHD_LABEL
WATCHTOWER_PLIST_PATH
```

If a local path is needed for examples, mark it as an example and avoid making it the only supported path.

## New Skill Checklist

Before committing a new skill:

- [ ] `SKILL.md` has only portable frontmatter: `name`, `description`.
- [ ] The description includes trigger words and use cases.
- [ ] The body is useful without private context.
- [ ] Any references are public-safe or private-safe for the repository visibility.
- [ ] Any scripts use environment variables for local paths.
- [ ] No secrets or local plaintext backup files are included.
- [ ] The skill is registered in `.claude-plugin/marketplace.json` if needed.
- [ ] The skill validates in Codex when possible.
- [ ] The skill is synced to local Codex and Claude install directories after release.

## Installation Targets

Current local install targets (统一使用软连接):

```text
Claude:     ~/.claude/skills/<skill-name>         # 软连接（ln -s）
Codex:      ~/.codex/skills/<skill-name>          # 软连接（ln -s）
OpenHuman:  ~/.openhuman/skills/<skill-name>      # 软连接（ln -s）
```

安装方式：统一使用软连接指向 `skills/praxis-skills/skills/<skill-name>`
- 源文件更新后自动生效，无需手动同步
- 所有 agent 共享同一份源文件，节省磁盘空间

批量安装命令：
```bash
# 安装所有 alex skills 到三个 agent
for src in /Users/alex/Documents/myCode/skills/praxis-skills/skills/praxis-*/; do
  name=$(basename "$src")
  for dir in ~/.claude/skills ~/.codex/skills ~/.openhuman/skills; do
    target="$dir/$name"
    if [ -L "$target" ]; then
      echo "→ $name (已有)"
    elif [ -d "$target" ]; then
      rm -rf "$target" && ln -s "$src" "$target" && echo "✓ $name (替换)"
    else
      ln -s "$src" "$target" && echo "✓ $name (新建)"
    fi
  done
done
```

安装后验证：
```bash
# 验证三个 agent 的软连接数量
echo "Claude: $(ls -la ~/.claude/skills/ | grep '^l.*praxis-' | wc -l)"
echo "Codex: $(ls -la ~/.codex/skills/ | grep '^l.*praxis-' | wc -l)"
echo "OpenHuman: $(ls -la ~/.openhuman/skills/ | grep '^l.*praxis-' | wc -l)"
```
