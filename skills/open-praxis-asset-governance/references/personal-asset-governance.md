# Personal Asset Governance

This document defines how Alex's reusable AI/coding assets are classified, stored, secured, and restored.

## Core Principle

Separate capability, implementation, configuration, secrets, and runtime output.

Also separate access, intelligence, and monitoring:

```text
Access Layer        = raw information access/transcription/formatting
Intelligence Layer  = filtering, synthesis, judgment, and reports
Monitoring Layer    = long-running tracking of selected targets
```

Example mapping:

| Layer | Example |
|---|---|
| Access | Agent-Reach, WebFetch, Browser |
| Intelligence | `praxis-news-aggregator`, `praxis-url-to-markdown` |
| Monitoring | `github-project-watchtower` |

Access-layer tools should not own analysis logic. Intelligence-layer Skills should not reimplement complex access tooling. Monitoring-layer tools should not become generic news/research systems.

```text
praxis-skills                  = capability assets
standalone tool repositories = tool implementation assets
praxis-local-configs           = encrypted configuration assets
local profile backup         = emergency plaintext key/secret backup
runtime reports/state        = local runtime output
```

Do not mix these layers. Skills should not contain secrets. Tool repositories should not contain machine-specific secrets. Configuration repositories should not contain reusable Skill logic unless it is purely bootstrap logic.

## Asset Layers

| Layer | Repository / Location | Purpose | Examples |
|---|---|---|---|
| Capability assets | `mooncreek/praxis-skills` | Reusable AI workflows and Skill instructions | `praxis-github-watchtower`, `praxis-news-aggregator`, translation/diagram/report Skills |
| Tool assets | Standalone project repositories | Runnable code and documentation for real tools | `mooncreek/github-project-watchtower` |
| Configuration assets | `mooncreek/praxis-local-configs` | Machine/project configuration, encrypted `.env`, bootstrap scripts | `projects/*/secrets.env.enc`, host profiles, install scripts |
| Emergency plaintext backup | Local-only private folder | Recovery keys and emergency credential backup | `<local-private-profile-backup>` |
| Runtime output | Local project directories | Reports, state, logs, caches | `reports/`, `state/`, `logs/` |

## What Goes Where

### `mooncreek/praxis-skills`

Store reusable procedures that Codex/Claude can invoke.

Good candidates:

- A repeatable workflow.
- A troubleshooting playbook.
- A decision framework.
- A report generation pattern.
- Instructions for operating an existing tool.

Allowed:

- `SKILL.md`
- Public-safe references.
- Generic helper scripts.
- Templates that contain no real secrets.

Forbidden:

- `.env`
- Tokens, webhook URLs, API keys.
- SOPS age private keys.
- `secrets.env.enc` from personal config repositories.
- Local plaintext backup paths or contents.
- Runtime `reports/`, `state/`, `logs/`.

### Standalone Tool Repositories

Store actual runnable projects.

Example: `mooncreek/github-project-watchtower`.

Allowed:

- Source code.
- Config examples.
- Non-secret docs.
- Launchd/GitHub Actions templates.
- Test fixtures that contain no secrets.

Forbidden:

- Real `.env`.
- Real tokens/webhooks/API keys.
- Generated local reports or state.

### `mooncreek/praxis-local-configs`

Store local machine/project configuration and recovery automation.

Allowed:

- Encrypted secrets such as `secrets.env.enc`.
- `.sops.yaml` with public age recipients.
- `bootstrap.sh`, `install.sh`, `verify.sh`.
- Host profiles.
- Non-secret templates.
- Operational docs.

Forbidden:

- Plaintext tokens/webhooks/API keys.
- SOPS age private keys.
- Runtime reports/state/logs.

### Local Profile Backup

Local-only emergency backup path:

```text
<local-private-profile-backup>
```

Allowed:

- `<sops-age-key-backup>`
- `<local-secrets-backup>`
- Recovery instructions.

Rules:

- Never commit this folder.
- Never copy it into public repositories.
- Treat it as highly sensitive plaintext.
- If the device is lost, assume these secrets are compromised and rotate them.

### Runtime Output

Keep runtime output out of Git unless explicitly intended as documentation.

Examples:

- `reports/`
- `state/`
- `logs/`
- caches
- local database files

## Decision Rules

Use these questions when deciding where a new asset belongs.

1. Is it a reusable AI workflow or playbook?
   - Put it in `praxis-skills`.
2. Is it runnable application/tool code?
   - Put it in its own tool repository.
3. Is it machine-specific configuration or `.env` material?
   - Put it in `praxis-local-configs`, encrypted if sensitive.
4. Is it a secret required to decrypt other secrets?
   - Keep it in a password manager or local-only emergency backup, not Git.
5. Is it generated output?
   - Keep it local, ignore it in Git, or publish intentionally as a report artifact.

## New Skill Checklist

Before adding a Skill to `praxis-skills`:

- [ ] It contains no real secrets.
- [ ] It contains no local-only sensitive path contents.
- [ ] It uses generic variables for local paths when needed.
- [ ] `SKILL.md` frontmatter uses Codex-compatible keys only: `name`, `description`.
- [ ] It includes enough workflow detail to be useful without private context.
- [ ] It is registered in the plugin manifest if needed.
- [ ] It is synced to local Codex/Claude skill directories after release.

## New Tool Repository Checklist

Before creating or publishing a tool repository:

- [ ] Add `.gitignore` for `.env`, state, reports, logs, and caches.
- [ ] Provide `config.example.env` instead of real `.env`.
- [ ] Put real local config in `praxis-local-configs`.
- [ ] Document install, run, verify, and recovery steps.
- [ ] Decide whether a companion Skill should be added to `praxis-skills`.

## New Configuration Checklist

Before adding project config to `praxis-local-configs`:

- [ ] Store plaintext templates separately from secrets.
- [ ] Encrypt secrets with `sops + age`.
- [ ] Verify decrypt/install scripts do not print secret values.
- [ ] Add a `verify.sh` for restored config.
- [ ] Document which real project path receives the config.

## Device Loss Response

If a device is lost or suspected compromised:

1. Revoke GitHub/GitLab tokens.
2. Rotate Feishu webhooks.
3. Rotate LLM/API provider keys.
4. Generate a new SOPS age key.
5. Re-encrypt all `*.enc` files with the new recipient.
6. Update `praxis-local-configs` and push.
7. Restore onto a new device using the new key.

If local plaintext backup files may have been exposed, treat all credentials in them as compromised.

## Naming Guidance

- Skills: `praxis-<capability>`.
- Tool repositories: concise project names, one tool per repo.
- Config project folders: match the tool repository name.
- Host profiles: stable machine nickname, for example `praxis-macbook`.

## Current Asset Map

| Asset | Location | Classification |
|---|---|---|
| `praxis-github-watchtower` | `mooncreek/praxis-skills` | Capability asset |
| `github-project-watchtower` | `mooncreek/github-project-watchtower` | Tool asset |
| Watchtower `.env` encrypted backup | `mooncreek/praxis-local-configs` | Configuration asset |
| SOPS age key backup | `<local-private-profile-backup>` | Local emergency plaintext backup |
