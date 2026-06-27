# Git Workflow Patterns

Source: obra/superpowers finishing-a-development-branch + using-git-worktrees

## Branch Finishing

Detect environment → determine base branch → present options (merge/PR/squash/keep) → cleanup

## Worktree Isolation

Use for: feature isolation, parallel implementation, testing without affecting main workspace.

Setup: `git worktree add .worktrees/feature-xyz -b feature-xyz`
Cleanup: only clean `.worktrees/` or `worktrees/` dirs. Never delete with uncommitted changes.

Detection: `$GIT_DIR != $GIT_COMMON_DIR` → in a linked worktree.
