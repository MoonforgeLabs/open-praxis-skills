---
name: open-praxis-handoff
description: Compact the current conversation, project state, decisions, files changed, commands run, blockers, and next steps into a handoff document for another agent or future session.
---

# Alex Handoff

Create a handoff that another agent can continue from without rereading the whole thread.

## Include

- Goal and current status.
- Important decisions and assumptions.
- Files, repos, branches, commits, and artifacts touched.
- Commands run and validation results.
- Open blockers and risks.
- Next recommended steps.
- What not to redo.

## Output

Return a concise Markdown handoff. If the user asks for a file, write it to the current project with a clear name.

Inspired by `mattpocock/skills` `handoff` under MIT License.
