# Installation Guide

## Claude Code（已自动工作）
- Hook `log-tool-usage.sh` 自动记录到 `~/.claude/tool-usage.log`
- Skill 通过 praxis-skills 插件发现

## Codex
```bash
ln -sf ~/skills/praxis-skills/skills/praxis-ai-usage-stats ~/.codex/skills/praxis-ai-usage-stats
```
配合 AGENTS.md 规则让 agent 主动调 `log_usage.py` 记录 skill 使用。

## OpenCode / OpenHuman / Moonforge
```bash
ln -sf ~/skills/praxis-skills/skills/praxis-ai-usage-stats <runtime-skills-dir>/praxis-ai-usage-stats
```
如果 runtime 支持 hook，可配置类似 Claude 的自动记录；否则使用 `log_usage.py` 手动记录。
