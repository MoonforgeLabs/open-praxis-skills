# 跨平台兼容性说明

## 支持平台

| 平台 | 状态 | 说明 |
|------|------|------|
| **macOS** | ✅ 完全支持 | 主要开发平台 |
| **Linux** | ✅ 完全支持 | 所有功能都兼容 |
| **Windows** | ✅ 完全支持 | 使用 Python 安装脚本 |

## 依赖项

### Python 依赖

**无外部依赖**，只使用 Python 标准库：

- `sqlite3` - 数据库
- `json` - JSON 处理
- `pathlib` - 跨平台路径处理
- `datetime` - 日期时间处理
- `collections` - 数据结构
- `typing` - 类型注解

**Python 版本要求**：Python 3.8+

### 系统依赖

| 依赖 | macOS | Linux | Windows |
|------|-------|-------|---------|
| Python 3.8+ | ✅ | ✅ | ✅ |
| SQLite3 | ✅ 内置 | ✅ 内置 | ✅ 内置 |
| Bash | ✅ | ✅ | ⚠️ 需要 WSL/Git Bash |
| 软连接 | ✅ | ✅ | ⚠️ 需要管理员权限 |

## 平台特定说明

### macOS

**完全支持**，无特殊配置。

```bash
# 安装
./scripts/install.sh

# 使用
python3 scripts/usage_stats.py today
```

### Linux

**完全支持**，无特殊配置。

```bash
# 安装
./scripts/install.sh

# 使用
python3 scripts/usage_stats.py today
```

### Windows

**完全支持**，使用 Python 安装脚本：

```powershell
# 安装到所有 runtime
python install.py

# 只安装到 Claude Code
python install.py --claude

# 只安装到 Codex
python install.py --codex

# 检查依赖状态
python install.py --check
```

**注意**：Windows 创建软连接可能需要管理员权限，脚本会自动尝试使用 junction 作为备选方案。

## 路径处理

所有路径都使用 `pathlib.Path` 处理，自动适配平台：

```python
from pathlib import Path

# 自动适配 macOS/Linux/Windows
db_path = Path.home() / ".praxis-ai-usage-stats" / "usage.db"
```

## Hook 机制

### Claude Code

**跨平台支持**，通过 `~/.claude/settings.json` 配置：

```json
{
    "hooks": {
        "PostToolUse": [
            {
                "matcher": "Skill|Bash|Read|Write|Edit|Agent",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python3 /path/to/hook_collect.py || true"
                    }
                ]
            }
        ]
    }
}
```

### Codex

**跨平台支持**，通过 `~/.codex/skills/praxis-ai-usage-stats/hooks/hooks.json` 配置：

```json
{
    "hooks": {
        "PostToolUse": [
            {
                "matcher": "Skill|Bash|Read|Write|Edit|Agent",
                "hooks": [
                    {
                        "type": "command",
                        "command": "python3 /path/to/hook_collect.py || true",
                        "async": false
                    }
                ]
            }
        ]
    }
}
```

## 已知问题

### Windows

1. **软连接权限**：需要管理员权限创建软连接
   - 解决方案：使用 WSL 或 Git Bash，或手动复制目录

2. **路径分隔符**：Windows 使用反斜杠 `\`
   - 解决方案：代码中使用 `pathlib.Path`，自动处理

3. **Bash 脚本**：install.sh 是 Bash 脚本
   - 解决方案：使用 WSL、Git Bash，或手动安装

### Linux

无已知问题。

### macOS

无已知问题。

## 测试状态

| 功能 | macOS | Linux | Windows |
|------|-------|-------|---------|
| 安装脚本 | ✅ | ✅ | ⚠️ |
| Hook 捕获 | ✅ | ✅ | ✅ |
| 数据库 | ✅ | ✅ | ✅ |
| 统计查询 | ✅ | ✅ | ✅ |
| 报告生成 | ✅ | ✅ | ✅ |
| 自动清理 | ✅ | ✅ | ✅ |

## 开源建议

如果开源 `praxis-ai-usage-stats`，建议：

1. **文档中说明平台支持**
2. **提供多种安装方式**：
   - 安装脚本（macOS/Linux）
   - 手动安装说明（Windows）
   - WSL/Git Bash 说明（Windows）

3. **测试所有平台**：
   - macOS: 主要测试平台
   - Linux: CI/CD 测试
   - Windows: 社区反馈

4. **依赖说明**：
   - Python 3.8+
   - 无外部依赖
   - SQLite3（内置）
