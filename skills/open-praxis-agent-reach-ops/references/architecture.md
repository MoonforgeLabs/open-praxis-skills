# Agent-Reach Architecture Notes

Agent-Reach is an access-layer tool. It should be reusable by multiple Skills.

## Good Uses

- Fetching or accessing difficult web/platform content.
- Formatting raw platform API output.
- Transcribing audio/video URLs or local media files.
- Running health/update checks for access infrastructure.
- Installing Agent-Reach's own agent skill registration.

## Bad Uses

- Replacing news analysis logic.
- Owning GitHub repository monitoring.
- Storing token recovery material in a public or generic Skill.
- Mixing platform credentials into `praxis-skills`.

## Long-Term Flow

```text
Agent-Reach collects/transcribes raw material
  -> praxis-news-aggregator filters and synthesizes
  -> github-project-watchtower tracks selected repos
  -> praxis-asset-governance decides where outputs/assets live
```

## Configuration Pattern

Agent-Reach capability setup has three layers:

1. CLI/tool installation: `agent-reach`, optional CLIs, `mcporter`, `opencli`.
2. Local runtime config: browser extension, cookies, provider keys, proxy.
3. Governance docs: store recovery instructions in `praxis-local-configs`; keep operating procedure in `praxis-skills`.

Do not store cookies, tokens, or provider keys in this Skill.
