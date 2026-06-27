# Source Notes

## Upstream Sources

| Source | URL | License | Observed Version | Borrowed Pattern | Local Adaptation | Watch For |
|---|---|---|---|---|---|---|
| Matt Pocock `writing-great-skills` | https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-great-skills/SKILL.md | MIT | Retrieved 2026-06-25 via GitHub/Skill Vault | Predictability, invocation load, router skills, information hierarchy, split/merge criteria, pruning, leading words, failure modes | Distilled into `references/writing-great-skills.md` and added curator workflow gates for merge/split/source tracking | Changes to invocation taxonomy, glossary, split criteria, pruning guidance |
| OpenAI `skill-creator` | Local `/Users/alex/.codex/skills/.system/skill-creator/SKILL.md` | Local bundled guidance | Retrieved 2026-06-25 | Concise SKILL.md, frontmatter constraints, progressive disclosure, validation | Kept compatibility with `name`/`description` frontmatter and `quick_validate.py` validation | Updates to validation rules or `agents/openai.yaml` expectations |
| `praxis-skills` existing curator practice | Local `skills/praxis-skill-forge` | Private/local | Retrieved 2026-06-25 | Intake rubric, public/private boundary, README/taxonomy/manifest updates | Extended existing flow rather than replacing it | Drift between README, taxonomy, marketplace manifest, and skill folders |

## Boundary

- What is adapted, not copied: concepts and decision criteria for writing predictable skills.
- What is intentionally excluded: upstream glossary text, full upstream prompt text, package tooling, and any assumptions not needed by Alex workflows.
- Private/local assumptions kept out of public skill files: credentials, account state, private reports, and local-only source content beyond path references.

## Update Cadence

- Review cadence: monthly, or before a major praxis-skills refactor.
- Update trigger: upstream `mattpocock/skills` changes to `writing-great-skills`, OpenAI skill validation changes, or recurring confusion about which Alex skill to invoke.
- Last reviewed: 2026-06-25.
