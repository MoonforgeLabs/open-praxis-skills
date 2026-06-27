#!/usr/bin/env bash
# Git post-commit hook: 提醒同步到 org 和 pub 仓库
# 安装: cp scripts/post-commit-reminder.sh .git/hooks/post-commit && chmod +x .git/hooks/post-commit

echo ""
echo -e "\033[1;33m📦 别忘了同步到下游仓库：\033[0m"
echo "  bash scripts/sync-repos.sh          # 同步全部"
echo "  bash scripts/sync-repos.sh --check  # 只检查"
echo ""
