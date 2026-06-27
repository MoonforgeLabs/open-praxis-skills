# Inspiration Map

Use this map to turn monitored repositories into local improvements.

## Repository Patterns

| Source | Borrow | Local target |
|---|---|---|
| `mvanhorn/last30days-skill` | Entity tracking, multi-source evidence, clustering, brief format, watchlists | `github-project-watchtower/scripts/intelligence_daily.py`; weekly review |
| `affaan-m/ECC` | Workspace status, cross-agent compatibility, verification loops, skill governance | `scripts/moonforge_status.py`; `praxis-skills` docs |
| `pewdiepie-archdaemon/odysseus` | Local-first Moonforge dashboard, memory/docs/tasks/calendar integration | Future workspace dashboard/backlog |
| `Egonex-AI/Understand-Anything` | Codebase maps, function/class/file relationship summaries | Watchtower architecture summaries; CodeGraph-style reports |
| `msitarzewski/agency-agents` | Role-based specialist workflows | Weekly/monthly review roles and checklists |
| `mattpocock/skills` | Small composable skills with focused setup | `praxis-skills` skill design and cleanup |
| `ComposioHQ/awesome-claude-skills` | Skill marketplace taxonomy and app automation categories | Skill candidate discovery and intake rubric |
| `hesreallyhim/awesome-claude-code` | Hooks, commands, agents, templates, Claude Code/Codex ecosystem radar | Candidate skills and workflow improvements |
| `awesome-selfhosted/awesome-selfhosted` | Service taxonomy, inventory discipline, self-hosted categories | Moonforge service/token/recovery inventory |

## Backlog Buckets

### Now

- Keep intelligence daily entity clustering and action suggestions working.
- Maintain `praxis-skill-forge` as the gate for absorbing external skills.
- Maintain `moonforge-review` as the review entrypoint.

### Next

- Add a skill candidate inventory report generated from monitored awesome lists.
- Add source quality scoring for B站、小红书、国内科技媒体.
- Add architecture-map output for important local repos.

### Later

- Build an Moonforge dashboard from status snapshots.
- Add self-hosted service and token inventory with recovery status.
- Add role-based review prompts for security, noise, GitHub candidates, and skill governance.

## Absorption Rule

When a monitored repository produces a useful idea, first decide whether it belongs in:

1. A watchtower script or report.
2. A new or existing `praxis-skills` skill.
3. `praxis-local-configs` documentation.
4. A future dashboard/backlog item.

Only create a new skill when the workflow is reusable outside one repository.
