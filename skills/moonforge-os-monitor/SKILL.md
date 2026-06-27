---
name: moonforge-os-monitor
description: Run Moonforge AI OS monitoring across runtime adapters, ToolRouter, Skill OS, Knowledge Fabric, Connector Registry, Cloudflare/edge public-demo strategy, OpenHands, ai-engineering-from-scratch, Agent-Reach, watched AI OS repos, and Moonforge action queues. Use when the user asks for Moonforge OS monitoring, AI OS radar, OS health, inspiration absorption, or turning monitored signals into Moonforge design/actions.
---

# Moonforge OS Monitor

AI OS-specific monitoring orchestrator. It turns relevant watchtower reports, learning sources, and external projects into Moonforge architecture decisions, acceptance criteria, and action items.

## Boundaries

- This Skill monitors Moonforge as an AI OS, not Alex's personal learning or investing interests.
- Use `praxis-personal-monitor` for personal signals.
- Use `praxis-knowledge-radar` for daily learning notes and knowledge management.
- Moonforge receives only reviewed, OS-relevant outputs: design decisions, action queue items, module checklists, or inspiration backlog entries.

## Inputs

Prefer local sources:

- `moonforge/docs/inspiration-backlog.md`
- `moonforge/docs/ecosystem-absorption.md`
- `moonforge/docs/ai-engineering-learning-sources.md`
- `moonforge/docs/article-intake-radar.md`
- `moonforge/docs/cloudflare-edge-strategy.md`
- `moonforge/reports/latest/`
- `github-project-watchtower/repos.yaml` entries with `scope: moonforge-os` or `scope: both`
- `github-project-watchtower/reports/YYYY-MM-DD/`

Key monitored sources include OpenHands, ai-engineering-from-scratch, Agent-Reach, awesome-claude-skills, awesome-claude-code, Agency Agents, Cloudflare-style edge patterns, coding agents, RAG frameworks, and browser/desktop agents.

## Monitoring Workflow

1. Read Moonforge docs and latest reports.
2. Filter signals to OS-relevant categories:
   - Runtime / ToolRouter
   - Skill OS / Capability Hub
   - Knowledge Fabric / SearchRouter
   - Connector Registry
   - Public demo / Edge strategy
   - Digital Workforce
   - Code intelligence and coding agents
   - Security, permissions, and governance
3. Compare watched projects against Moonforge's current docs and action queue.
4. Classify each signal: absorb now, watch, skip, or move to Alex Learning first.
5. Produce concrete outputs: doc edit, design decision, checklist, action queue item, or watchtower scope change.

## Output Shape

- `OS status`: healthy / needs attention / blocked.
- `Signals`: repo/source -> Moonforge module mapping.
- `Absorb now`: small concrete changes.
- `Watch`: candidates needing more evidence.
- `Skip`: hype, duplicate, or poor fit.
- `Actions`: file paths and next edits.
- `Safety`: privacy, licensing, and public-demo boundaries.
