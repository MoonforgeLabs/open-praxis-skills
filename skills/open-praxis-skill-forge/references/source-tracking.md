# Source Tracking

Use this when a skill is inspired by an external tool, repo, paper, framework, article, or skill ecosystem.

## Required Source Notes File

Default path:

`skills/<skill-name>/references/source-notes.md`

Use a more specific reference file only when the skill already has a focused source ledger.

## Template

```markdown
# Source Notes

## Upstream Sources

| Source | URL | License | Observed Version | Borrowed Pattern | Local Adaptation | Watch For |
|---|---|---|---|---|---|---|
| Example | https://github.com/org/repo | MIT/unknown | commit/date/tag | What idea was studied | How Alex adapted it | Releases, README changes, new APIs |

## Boundary

- What is adapted, not copied:
- What is intentionally excluded:
- Private/local assumptions kept out of public skill files:

## Update Cadence

- Review cadence:
- Update trigger:
- Last reviewed:
```

## Rules

- Prefer commit, tag, release, or retrieval date over vague source names.
- Record unknown licenses explicitly as `unknown`; do not assume.
- Track source drift only for sources that influence behavior, not casual inspiration.
- Summarize borrowed patterns in your own words.
- Keep raw private notes, credentials, account state, and personal data out of source notes.
