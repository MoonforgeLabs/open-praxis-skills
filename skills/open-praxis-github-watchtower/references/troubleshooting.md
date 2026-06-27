# Troubleshooting

## No Feishu message received

1. Confirm the watcher printed a successful webhook response, usually HTTP 200 and body code 0.
2. Confirm `.env` has `NOTIFY_CHANNEL=feishu` and a valid webhook URL.
3. Confirm Feishu Flow branch condition matches `source=github-project-watchtower` and `event_type=github_daily_report`.
4. Confirm the message node displays fields such as `title` and `summary` instead of an unintended raw object.

## Fork sync failed

Open the latest summary and per-repo report. For token errors:

- Target fork must be included in repository access.
- `Contents: Read and write` must be enabled.
- `.env` must contain the current token.

For merge conflicts, report the repo and ask the user whether to resolve manually. Do not force-push by default.

## Duplicate runs

Repeated runs are usually safe. They may generate extra timestamped report directories and send another notification. State files should prevent already-seen upstream commits from being reported as new.

## Dry run

`--dry-run` should generate reports without performing fork writes. Fork sync may show `dry_run` status.

## Secret hygiene

Never copy public Skill files from a local configuration backup directory. Keep plaintext backups, age private keys, `.env`, and encrypted project secrets outside public Skill repositories.
