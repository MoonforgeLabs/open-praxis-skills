---
name: open-praxis-personal-monitor
description: Run Alex's personal monitoring loop for AI news, investment/stock learning signals, Bilibili/Xiaohongshu/domestic tech media keywords, personal GitHub interests, and learning candidates. Use when the user asks for personal radar, personal monitoring, AI/stock/media monitoring, daily signal quality, or non-Moonforge watchlist triage.
---

# Alex Personal Monitor

Personal monitoring orchestrator for learning, investment observation, media/news noise control, and personal GitHub interests.

## Boundaries

- This Skill is for Alex's personal radar, not Moonforge OS health.
- It can propose items for `praxis-learning`, but should not directly modify Moonforge unless the user explicitly asks.
- Use `moonforge-os-monitor` for AI OS runtime, Skill OS, Connector Registry, Knowledge Fabric, Runtime/ToolRouter, or public-demo monitoring.
- Do not store tokens, cookies, webhook URLs, private reports, or internal links in public notes.

## Inputs

Prefer local sources first:

- `github-project-watchtower/reports/YYYY-MM-DD/latest-intelligence-daily.md`
- `github-project-watchtower/reports/YYYY-MM-DD/latest-github-news-daily.md`
- `github-project-watchtower/repos.yaml` entries with `scope: personal` or `scope: both`
- `praxis-learning/topics/`
- `praxis-learning/actions/backlog.md`

Optional tools:

- `praxis-search-hub` for controlled search.
- `praxis-news-aggregator` for briefs.
- `last30days` for trend validation.
- `praxis-url-to-markdown` and `praxis-youtube-transcript` for source capture.

## Review Workflow

1. Separate personal signals from Moonforge OS signals.
2. Check noise: duplicated topics, hype-only repos, low-value media sources, and stale keywords.
3. Identify learning candidates for `praxis-learning`.
4. Identify investment observations without giving financial advice.
5. Recommend keyword/source changes for Bilibili, Xiaohongshu, domestic tech media, and GitHub.
6. Recommend watchlist changes only when the signal is repeated or strategically useful.

## Output Shape

- `Status`: healthy / noisy / degraded.
- `Signals`: personal learning, investment, AI/product, and media items.
- `Noise`: sources or keywords to reduce.
- `Learning candidates`: items for `praxis-learning`.
- `Watchlist actions`: add/watch/remove candidates.
- `Safety`: privacy and account-risk notes.
