# GitHub Token Permissions

Use a fine-grained personal access token for fork synchronization.

## Minimal permissions

Repository access:

- Recommended: `Only select repositories`
- Select every fork repository that the watcher should sync.
- Use `All repositories` only when operational convenience is more important than least privilege.

Repository permissions:

- `Contents`: `Read and write`
- `Metadata`: `Read-only` default

Usually unnecessary:

- `Actions`
- `Administration`
- `Secrets`
- `Variables`
- `Pull requests`, unless the tool creates PRs

## Why Contents write is required

GitHub's `merge-upstream` API writes upstream changes into the fork branch. The token must cover the target fork repository and allow contents writes.

## Common errors

`Resource not accessible by personal access token` usually means:

- Token does not include the target fork repository.
- Token lacks `Contents: Read and write`.
- Token owner/repository selection is wrong.
- Token expired or the local `.env` still uses an old token.

`This branch is out-of-date` means the fork is behind upstream. A correctly authorized watcher can usually sync it unless there are conflicts.
