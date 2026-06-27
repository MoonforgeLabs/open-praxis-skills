# Skill Intake Rubric

Use this rubric before absorbing an external skill, agent, command, hook, or workflow into `praxis-skills`.

## Score

Rate each dimension from 0 to 2.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Repeated local use | One-off curiosity | Occasional use | Weekly or recurring task |
| Alex fit | Generic or off-domain | Useful with adaptation | Directly supports Alex workflows |
| Portability | Tied to one vendor/tool | Has fallbacks | Markdown-first, tool-light |
| Safety | Requires secrets/risky actions | Manageable with guardrails | No sensitive state needed |
| Distinctness | Duplicates an existing skill | Partly overlaps | Clearly fills a gap |
| Maintainability | Large or brittle | Medium effort | Small, clear, easy to test |

## Decision

- 10-12: absorb now.
- 7-9: add to watchlist or backlog; absorb only if the user has an active task.
- 0-6: skip unless the user explicitly asks.

## Required Notes

For each candidate, record:

- Source repository and URL.
- Upstream feature or pattern being borrowed.
- Local target skill name or existing skill to update.
- Why it is not a duplicate.
- Any tools, accounts, browser sessions, or API keys needed.
- Validation command or manual test.

## Common Absorption Patterns

- Awesome list -> add taxonomy, discovery checklist, or watchtower candidates.
- Agent persona library -> add role checklist to a workflow skill.
- Tool-specific prompt -> rewrite as portable procedure with fallbacks.
- Script-heavy skill -> keep the concept, add only scripts that can be tested locally.
- Research skill -> extract entity tracking, evidence scoring, clustering, and brief format.
