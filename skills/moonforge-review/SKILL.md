---
name: moonforge-review
description: Run Moonforge weekly review, monthly architecture review, and improvement backlog triage across github-project-watchtower, Agent-Reach, praxis-local-configs, praxis-skills, daily reports, fork sync, launchd jobs, tokens, digital workforce, knowledge fabric, and monitored inspiration repositories such as Odysseus, ECC, last30days-skill, agency-agents, awesome-claude-skills, awesome-claude-code, and awesome-selfhosted.
---

# Moonforge Review

Run structured reviews of Moonforge as Alex's personal AI OS and future open-source AI OS, and turn monitored project ideas into concrete improvements.

## Inputs

Prefer these local artifacts when available:

- `github-project-watchtower/reports/YYYY-MM-DD/latest-moonforge-status.md`
- `github-project-watchtower/reports/YYYY-MM-DD/latest-intelligence-daily.md`
- `github-project-watchtower/reports/YYYY-MM-DD/latest-summary.md`
- `github-project-watchtower/repos.yaml`
- `praxis-local-configs/docs/moonforge-architecture.md`
- `praxis-skills/README.md` and `praxis-skills/docs/skill-taxonomy.md`

If the status snapshot is stale or missing, run:

```bash
cd /Users/alex/Documents/myWork/openCode/github-project-watchtower
.venv/bin/python scripts/moonforge_status.py
```

## Moonforge Radar boards

During reviews, classify findings into these boards when relevant:

- GitHub Radar
- AI / Agent Radar
- AI OS Competitive Radar
- Skill Radar
- Market Radar
- Knowledge Intake Radar
- Moonforge Health Radar

Use `/Users/alex/Documents/myWork/openCode/praxis-local-configs/docs/moonforge-radar.md` as the product-level reference.

## Public / Private Boundary

Use `/Users/alex/Documents/myWork/openCode/praxis-local-configs/docs/moonforge-public-private-boundary.md` as the governance reference. Every review should classify findings with:

- `visibility`: `public-core`, `public-extension`, `private-config`, `private-knowledge`, or `sensitive-secret`.
- `open_source_action`: keep, template, redact, extract-interface, move-private, or discard.
- `destination`: Moonforge core, praxis-skills, praxis-local-configs, praxis-learning, myWiki, watchtower, or local-only.

Default principle: Moonforge accumulates public reusable AI OS capability; Alex-specific paths, accounts, private docs, reports, and runtime state remain private context.

## Weekly Review

Use `references/review-checklists.md#weekly-review`.

Focus on:

- Whether Moonforge itself is stable, observable, recoverable, and low-noise.
- Which Radar boards produced useful signals, noise, or required Alex participation.
- Whether current work moves Moonforge toward a broader AI OS rather than a single watchtower, search, or agent-frontend tool.
- Daily report noise and missed signals.
- GitHub candidates worth long-term monitoring.
- B站、小红书、国内科技媒体关键词 adjustments.
- Fork sync failures, conflicts, or PAT permission problems.
- Recent `github-project-watchtower` reports if the user asks for analysis.

## Monthly Architecture Review

Use `references/review-checklists.md#monthly-architecture-review`.

Focus on:

- Recovery docs and local config accuracy.
- Duplicate, stale, or archive-ready skills.
- Launchd schedules, backfill scripts, and notification health.
- Agent-Reach fork changes that might be upstream PR candidates.
- Plaintext backup, token rotation, and security boundaries.

## Inspiration Backlog

Use `references/inspiration-map.md` to translate monitored repositories into local improvements.

Default backlog order:

1. Skill governance and safe absorption.
2. Intelligence clustering, entity tracking, and low-noise briefs.
3. Moonforge control plane for job switches, safe modes, and recovery notes.
4. Moonforge status dashboard and recovery inventory.
5. Codebase understanding and architecture maps.
6. Agent role workflows for recurring reviews.
7. Self-hosted service and token/security inventory.

## Output Shape

Keep reviews action-oriented:

- `Status`: healthy, degraded, or needs attention.
- `Scope`: classify findings as Moonforge OS, Watchtower, Agent-Reach, Skill, config/recovery, search gateway, future control plane, or a Moonforge Radar board.
- `Visibility`: classify public/private boundary and open-source action.
- `Findings`: concrete issues with source file/report references.
- `Actions`: small next steps with owner implied as Alex/Codex.
- `Candidates`: repos, skills, or workflows to add, watch, or skip.
