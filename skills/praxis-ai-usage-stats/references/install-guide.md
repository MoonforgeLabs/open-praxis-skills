# Installation Guide

## Claude Code
```bash
# 运行安装脚本
python3 scripts/install.py
```

## Codex
```bash
# 创建软连接
ln -s <skill-path> ~/.codex/skills/praxis-ai-usage-stats
```

## 手动安装
如果自动安装失败，可以手动创建软连接：
```bash
ln -s <skill-path> ~/.claude/skills/praxis-usage-stats
ln -s <skill-path> ~/.codex/skills/praxis-ai-usage-stats
```
