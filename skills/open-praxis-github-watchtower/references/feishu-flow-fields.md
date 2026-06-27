# Feishu Flow Fields

Send a full JSON payload to Feishu Flow and configure the flow to display selected fields.

## Branch condition

Use a branch dedicated to GitHub Watchtower events:

```text
source = github-project-watchtower
AND event_type = github_daily_report
```

If the same webhook receives unrelated events, put them in separate branches by `source` and `event_type`.

## Recommended message template

Title:

```text
{{title}}
```

Content:

```text
{{summary}}
```

Keep titles generic for multi-repo reports. Put project-specific details in `summary`, `text`, or `content`.

Repository names in `summary` should include direct GitHub URLs so the message is actionable from Feishu, for example:

```text
apache/pulsar（https://github.com/apache/pulsar）
```

Apply this to changed repositories, attention items, fork candidates, and no-change lists.

## Expected payload fields

- `source`
- `project`
- `repo`
- `fork_repo`
- `category`
- `event_type`
- `severity`
- `title`
- `summary`
- `text`
- `content`
- `url`
- `date`
- `time`
- `timezone`
- `run_id`
- `status`
