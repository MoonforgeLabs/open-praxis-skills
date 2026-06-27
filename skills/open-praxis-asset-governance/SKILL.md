---
name: open-praxis-asset-governance
description: Decide where Alex's personal AI/coding assets should live and how they should be secured. Use when the user asks whether something should become a Skill, tool repository, local config, encrypted secret, plaintext backup, report artifact, or GitHub project; when discussing praxis-skills, praxis-local-configs, github-project-watchtower, personal asset management, secret storage, SOPS/age backups, or machine recovery.
---

# Alex Asset Governance

Use this skill to classify assets and recommend the correct storage location, repository, and security treatment.

## Primary Rule

Separate capability, implementation, configuration, secrets, and runtime output.

For Moonforge, also apply the Public Core vs Private Context boundary from `<WORKSPACE>/praxis-local-configs/docs/moonforge-public-private-boundary.md`.

Also separate access, intelligence, and monitoring:

```text
Access Layer        = tools that collect raw information, e.g. Agent-Reach, WebFetch, Browser
Intelligence Layer  = Skills that filter, analyze, and synthesize, e.g. praxis-news-aggregator
Monitoring Layer    = tools that track chosen targets over time, e.g. github-project-watchtower
```

Do not merge access-layer tools into intelligence-layer Skills. Let access tools fetch/transcribe/format raw material, and let analysis Skills decide meaning and next actions.

```text
praxis-skills                  = capability assets
standalone tool repositories = tool implementation assets
praxis-local-configs           = encrypted configuration assets
local profile backup         = emergency plaintext key/secret backup
runtime reports/state        = local runtime output
```

## Decision Workflow

Ask these questions in order:

1. Is it a reusable AI workflow, troubleshooting playbook, or repeatable operating procedure?
   - Put it in `mooncreek/praxis-skills` as `praxis-<capability>`.
   - If it operates an access-layer tool such as Agent-Reach, keep it as an ops Skill such as `praxis-agent-reach-ops`.
2. Is it runnable application/tool code?
   - Put it in a standalone tool repository.
3. Is it machine-specific configuration, `.env`, launchd config, or bootstrap logic?
   - Put it in `mooncreek/praxis-local-configs`.
4. Does it contain tokens, webhooks, API keys, or passwords?
   - Store encrypted in `praxis-local-configs` with `sops + age`, or in a local-only emergency backup if the user explicitly wants plaintext.
5. Is it an age private key or emergency secret backup?
   - Do not commit to Git. Keep in password manager or local-only backup.
6. Is it generated output such as reports, state, logs, or cache?
   - Keep local or publish intentionally as an artifact; do not commit by default.
7. Is it a long-running monitor or scheduler?
   - Use a standalone tool repository plus an operating Skill, not a Skill-only implementation.

## Repository Responsibilities

| Destination | Use For | Never Put |
|---|---|---|
| `mooncreek/praxis-skills` | reusable Skills and public-safe playbooks | `.env`, token, webhook, age key, `secrets.env.enc`, reports/state |
| tool repos | runnable code, docs, examples, templates | real `.env`, real credentials, local runtime state |
| `mooncreek/praxis-local-configs` | encrypted config, bootstrap scripts, host profiles | plaintext secrets, age private key |
| local profile backup | emergency plaintext recovery files | anything intended for Git |

## Response Style

When the user asks where something belongs, answer with:

1. **Classification**: capability / tool / config / secret / runtime output.
2. **Destination**: exact repo or local path.
3. **Security**: public-safe, private, encrypted, or local-only plaintext.
4. **Next action**: create Skill, create repo, encrypt config, update docs, or ignore runtime output.

## Canonical Reference

The source-of-truth governance document lives in:

```text
mooncreek/praxis-local-configs/docs/personal-asset-governance.md
```

Use the bundled `references/personal-asset-governance.md` for a public-safe version of the governance rules. If a private local config repository is available, prefer its `docs/personal-asset-governance.md` as the source of truth.

## Safety Rules

- Do not print secret values.
- Do not copy local plaintext backup files into public repositories.
- Do not put `secrets.env.enc` into `praxis-skills`; encrypted project config belongs to `praxis-local-configs`.
- If the user asks for plaintext backup, place it only in a user-specified local-only path and warn that device loss means credential rotation.
