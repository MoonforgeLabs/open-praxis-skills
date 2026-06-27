---
name: open-praxis-agent-reach-ops
description: Operate Agent-Reach as the access-layer tool for giving AI agents internet/platform access, transcription, formatting, health checks, and skill registration. Use when the user mentions Agent-Reach, agent-reach setup/install/configure/doctor/watch/transcribe/format/skill, browser/platform access, transcription via Groq/OpenAI, or asks how Agent-Reach should fit with praxis-news-aggregator, watchtower, praxis-local-configs, Codex, Claude, OpenCode, or OpenHuman.
---

# Alex Agent-Reach Ops

Use this skill to operate Agent-Reach as an access-layer tool. Agent-Reach should collect or transcribe raw information; higher-level Skills should analyze it.

## Role in the Stack

```text
Agent-Reach = Access Layer
praxis-news-aggregator = Intelligence Layer
praxis-github-watchtower = Monitoring Layer
praxis-local-configs = Config Layer
praxis-skills = Capability Layer
```

Do not merge Agent-Reach with news aggregation logic. Treat it as a reusable backend for web/platform access and transcription.

## Commands

### Check installation and platform health

```bash
agent-reach doctor
```

### Interactive setup

```bash
agent-reach setup
```

### Install all optional access channels

Preview first:

```bash
agent-reach install --env=auto --channels all --dry-run
```

Install:

```bash
agent-reach install --env=auto --channels all
```

If `mcporter` or `opencli` installs under a non-standard Node prefix, ensure that Node global bin is on `PATH`, for example:

```bash
export PATH="$HOME/.hermes/node/bin:$PATH"
```

Configure Exa search when `mcporter` is available:

```bash
mcporter config add exa https://mcp.exa.ai/mcp
```

### Configure values

```bash
agent-reach configure <key> <value>
```

If configuration contains tokens or API keys, store recovery material in the private config layer, not in this Skill.

### Install Agent-Reach's own Skill registration

```bash
agent-reach skill --install
```

Remove it:

```bash
agent-reach skill --uninstall
```

### Transcribe media

```bash
agent-reach transcribe <url-or-local-file>
agent-reach transcribe <url-or-local-file> --provider groq -o transcript.md
agent-reach transcribe <url-or-local-file> --provider openai -o transcript.md
```

Use this when `praxis-news-aggregator`, `praxis-youtube-transcript`, or research workflows need audio/video text.

### Format platform API output

```bash
agent-reach format <input>
```

Use this to clean platform output before passing it to analysis Skills.

### Scheduled health check

```bash
agent-reach watch
```

Use this in launchd or other scheduled checks when Agent-Reach is part of an automated workflow.

### Check for updates

```bash
agent-reach check-update
agent-reach version
```

## Integration Rules

### With praxis-news-aggregator

Use Agent-Reach as fallback or enhancement for data acquisition:

1. WebSearch / WebFetch.
2. Agent-Reach for hard-to-fetch pages, platform access, audio/video transcription, or formatted platform output.
3. Browser automation if interaction is required.
4. User-provided raw content.

`praxis-news-aggregator` should still own source selection, filtering, synthesis, and candidate recommendations.

### With github-project-watchtower

Agent-Reach should not manage fork sync or repository monitoring. It may help inspect web pages or release notes that watchtower reports link to.

### With praxis-local-configs

Store Agent-Reach recovery configuration in `praxis-local-configs` if it includes machine-specific settings, tokens, or API keys. Do not commit those values to `praxis-skills`.

## Security Rules

- Do not print tokens, cookies, API keys, or browser-extracted secrets.
- Do not store Agent-Reach config or tokens in this Skill.
- If the device is lost, rotate any Agent-Reach-related tokens/API keys stored locally.
- Keep this Skill as operating procedure only.

## Troubleshooting

1. Run `agent-reach doctor`.
2. Run `agent-reach version` and `agent-reach check-update`.
3. Confirm required provider keys are configured outside the Skill.
4. For transcription failures, retry with explicit `--provider groq` or `--provider openai`.
5. For agent integration issues, reinstall with `agent-reach skill --install`.

## Optional Channel Notes

- GitHub uses `gh CLI`; run `gh auth login` if GitHub is not fully available.
- YouTube uses `yt-dlp` and is usually zero-config.
- RSS/Atom is usually zero-config via `feedparser`.
- Web pages can use Jina Reader.
- Exa semantic search needs `mcporter` configured.
- Twitter/X, Reddit, and Xiaohongshu can use OpenCLI but require the Chrome extension and relevant browser login state.
- Xiaoyuzhou transcription needs a Groq or OpenAI key.
- Xueqiu needs browser login/cookies.
- LinkedIn full functionality needs a LinkedIn MCP backend.
