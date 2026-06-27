---
name: open-praxis-github-watchtower
description: Operate a local GitHub Project Watchtower-style repository monitor for tracking upstream GitHub changes, syncing forks, scanning fork candidates, generating Markdown/TXT/HTML reports, sending Feishu Flow notifications, diagnosing GitHub PAT permissions, and managing macOS launchd schedules. Use when the user mentions GitHub repo monitoring, GitHub daily or weekly reports, fork sync, merge-upstream, Feishu webhook reports, GitHub PAT permissions, watchtower, or scheduled repository change tracking.
---

# Alex GitHub Watchtower

Operate a local GitHub repository monitor that tracks upstream changes, syncs forks, generates reports, and sends notifications.

## Configuration

Resolve paths and labels from environment variables first:

| Variable | Default | Purpose |
|---|---|---|
| `WATCHTOWER_PROJECT_DIR` | `$PWD` | Local watchtower project directory |
| `WATCHTOWER_CONFIG` | `repos.yaml` | Repository config file |
| `WATCHTOWER_LAUNCHD_LABEL` | `com.praxis.github-watchtower` | macOS launchd label |
| `WATCHTOWER_PLIST_PATH` | `$HOME/Library/LaunchAgents/$WATCHTOWER_LAUNCHD_LABEL.plist` | launchd plist path |

A compatible project should provide:

```text
scripts/watch.py
repos.yaml
.env
reports/
state/
```

Never print or commit secrets from `.env`. Do not expose GitHub tokens, GitLab tokens, Feishu webhook URLs, LLM keys, SOPS age private keys, or plaintext local backups.

## Standard Workflows

### Run the watcher once

Use the bundled script:

```bash
bash skills/praxis-github-watchtower/scripts/run-watchtower.sh
```

Dry run:

```bash
bash skills/praxis-github-watchtower/scripts/run-watchtower.sh --dry-run
```

The script runs:

```bash
.venv/bin/python scripts/watch.py --config "$WATCHTOWER_CONFIG" --mode local --sync-forks --scan-forks
```

After a run, inspect `reports/YYYY-MM-DD/latest-summary.txt` or `latest-summary.md`. If notifications are enabled, confirm webhook response success.

Feishu-friendly summaries should include GitHub repository URLs next to repository names, especially in changed repositories, attention items, fork candidates, and no-change lists.

### Diagnose fork sync failures

1. Read the latest summary.
2. Open the per-repo report for failed repositories.
3. If the error says `Resource not accessible by personal access token`, check that the fine-grained PAT includes the fork repository and has `Contents: Read and write`.
4. If GitHub reports merge conflicts, report them; do not force-push or auto-resolve unless the user explicitly asks.

### Add monitored repositories

Edit `repos.yaml` in the watchtower project. Prefer explicit upstream and fork mappings. Run a dry run before a formal run.

### Manage macOS schedule

Use `references/launchd-operations.md`. Validate plist files with `plutil -lint` before loading.

### Configure Feishu Flow

Use `references/feishu-flow-fields.md`. Send full JSON payloads and configure Feishu Flow to display selected fields such as `title` and `summary`.

### Configure GitHub token permissions

Use `references/github-token-permissions.md`. Keep permissions minimal.

## Safety Rules

- Do not include `.env`, `secrets.env.enc`, `reports/`, `state/`, plaintext token backups, or age private keys in public Skill repositories.
- Treat any local plaintext backups as private machine files only.
- Keep the Skill generic; project-specific paths should be examples or environment-variable defaults, not hard requirements.
