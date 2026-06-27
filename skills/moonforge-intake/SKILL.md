---
name: moonforge-intake
description: Capture Alex's links, ideas, documents, project candidates, reminders, and quick observations into Moonforge Radar intake without executing engineering work directly. Use when Alex says “收进 Moonforge”, “以后研究”, “这个值得看”, “帮我记一下”, “加入 Radar”, or asks OpenHuman to capture an item for Moonforge triage.
license: MIT
metadata:
  provided_for: openhuman
  version: 0.1.0
  author: Alex
  platforms: [macos]
  moonforge:
    visibility: public-extension
    outputs: private-knowledge
    runtime_support:
      openhuman: native
      codex: handoff
      moonforge: intake-source
  prerequisites:
    paths:
      - /Users/alex/Documents/myWork/openCode/moonforge/radar-intake/inbox/openhuman
---
# Moonforge Intake

Use this Skill in OpenHuman when Alex says things like:

- “收进 Moonforge”
- “这个以后研究”
- “这个链接值得看”
- “帮我记一下这个想法”
- “这个项目对 Moonforge 可能有用”
- “后面让 Codex 搞”
- “加入 Radar / 加入观察 / 沉淀一下”

## Role

OpenHuman is not the engineering executor here. Its value is low-friction capture at the moment Alex notices something.

Do:

1. Capture the raw link, idea, file path, screenshot note, project name, or short task.
2. Normalize it into a Moonforge intake item.
3. Classify initial `radar_board`, `visibility`, `open_source_action`, and `destination`.
4. Write a JSON intake file under Moonforge inbox.
5. Tell Alex what was captured and what the next action should be.

Do not:

- Modify repositories.
- Run GitHub automation.
- Export private documents automatically.
- Add monitoring targets without confirmation.
- Store tokens, cookies, or private keys.
- Pretend the task is completed when only an intake item was created.

## Output Location

Default inbox:

```text
/Users/alex/Documents/myWork/openCode/moonforge/radar-intake/inbox/openhuman
```

Use `scripts/create_intake.py` to create an intake item.

## Quick Commands

```bash
python3 scripts/create_intake.py \
  --title "PixelRAG visual RAG idea" \
  --type idea \
  --content "Use PixelRAG as downstream visual index for document exports" \
  --tags ai-os,visual-rag,moonforge \
  --radar-board "Knowledge Intake Radar" \
  --visibility private-knowledge \
  --open-source-action extract-interface \
  --destination moonforge-backlog
```

For a URL:

```bash
python3 scripts/create_intake.py \
  --title "Interesting agent project" \
  --type link \
  --url "https://example.com" \
  --content "Worth evaluating for Moonforge" \
  --tags agent,github,moonforge
```

## Classification Defaults

| Input | radar_board | visibility | destination |
| --- | --- | --- | --- |
| GitHub project | GitHub Radar | public-extension or private-config | watchtower or moonforge-backlog |
| AI/agent article | AI / Agent Radar | private-knowledge | praxis-learning or myWiki |
| Moonforge architecture idea | AI OS Competitive Radar | public-core | moonforge-backlog |
| Skill idea | Skill Radar | public-extension | praxis-skills backlog |
| Personal/company doc | Knowledge Intake Radar | private-knowledge | myWiki |
| Token/config issue | Moonforge Health Radar | private-config or sensitive-secret | praxis-local-configs |

If unsure, use conservative defaults:

```yaml
radar_board: Knowledge Intake Radar
visibility: private-knowledge
open_source_action: move-private
destination: moonforge-inbox
```

## Handoff Rules

- If the next action is code/config/repo work, hand off to Codex with a concise task summary.
- If the next action is document export, suggest `praxis-document-export` but do not export automatically unless Alex asks.
- If the next action is learning, suggest `praxis-knowledge-radar` (includes learning orchestration).
- If the next action is monitoring, ask for confirmation before adding a target.
- If the next action is public Moonforge work, mark `visibility=public-core` or `public-extension` only after checking for private context.

## Public / Private Boundary

Use:

```text
/Users/alex/Documents/myWork/openCode/praxis-local-configs/docs/moonforge-public-private-boundary.md
```

Never store secret values. If Alex mentions credentials, summarize only that a secret exists and route it to secure handling.
