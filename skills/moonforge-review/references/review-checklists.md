# Review Checklists

## Weekly Review

1. Read the latest Moonforge status snapshot.
2. Read the latest intelligence daily report and inspect `聚类热点` plus `建议动作`.
3. Check whether GitHub/AI/stock daily reports contain too much repeated or low-value noise.
4. Review GitHub candidates suggested by the intelligence report; add only durable candidates to `repos.yaml`.
5. Check B站、小红书、国内科技媒体 sections for keyword drift, spammy creators, or missing entities.
6. Inspect watchtower summary for fork sync failures, merge conflicts, or token permission errors.
7. If there are significant changes, summarize what should be changed before the next scheduled run.

## Monthly Architecture Review

1. Compare `praxis-local-configs/docs/moonforge-architecture.md` with the current workspace layout.
2. Review `praxis-skills` for duplicate, stale, too-broad, or archive-ready skills.
3. Confirm `github-project-watchtower` launchd plists, backfill scripts, reports, and notification paths still match reality.
4. Review Agent-Reach fork changes and identify upstream PR candidates.
5. Check token handling, plaintext backups, encrypted backups, and recovery boundaries.
6. Review monitored inspiration repositories and update the improvement backlog.
7. End with a short action list, not a long essay.

## Channel Health Checks

- GitHub: candidate quality, duplicate repos, fork sync health, PAT permissions.
- AI media: repeated tutorial spam, missing entities, source coverage.
- B站: creator quality, title spam, search keyword drift.
- 小红书: login health, high-like noise, creator reliability.
- Domestic tech media: site list freshness and SEO spam.
- Agent-Reach: `agent-reach doctor`, channel status, upstream changes.
