# 跨平台支持指南

## 概述

所有 skill 应该支持 macOS、Linux、Windows 三个平台。

## 要求

### 1. 安装脚本

**必须使用 Python 安装脚本**（`install.py`），而不是 Bash 脚本（`install.sh`）。

**原因**：
- Python 是跨平台的
- 用户已经需要安装 Python（skill 本身需要）
- 不需要额外的 Bash 环境

**示例结构**：
```
skill-name/
├── scripts/
│   ├── install.py          # 跨平台安装脚本
│   ├── check_dependencies.py  # 依赖检查
│   └── ...
└── SKILL.md
```

### 2. 路径处理

**必须使用 `pathlib.Path`**，而不是 `os.path`。

**正确**：
```python
from pathlib import Path

db_path = Path.home() / ".skill-name" / "data.db"
```

**错误**：
```python
import os

db_path = os.path.expanduser("~/.skill-name/data.db")
```

### 3. 软连接创建

**使用 `os.symlink`**，并处理 Windows 特殊情况：

```python
def create_symlink(target: Path, link_path: Path) -> bool:
    """创建软连接（跨平台）"""
    try:
        if sys.platform == "win32":
            # Windows 尝试使用 junction（不需要管理员权限）
            try:
                os.symlink(target, link_path, target_is_directory=True)
            except OSError:
                import subprocess
                subprocess.run(["mklink", "/J", str(link_path), str(target)],
                             shell=True, check=True)
        else:
            # macOS/Linux
            os.symlink(target, link_path)
        return True
    except OSError as e:
        print(f"❌ 创建软连接失败: {e}")
        return False
```

### 4. 文件权限

**只在 macOS/Linux 上设置权限**：

```python
def set_permissions(scripts_dir: Path):
    """设置脚本执行权限"""
    if sys.platform == "win32":
        # Windows 不需要设置执行权限
        return

    for script in scripts_dir.glob("*.py"):
        script.chmod(0o755)
```

### 5. Hook 配置

**支持多个 runtime 的 hook**：

- Claude Code: `~/.claude/settings.json`
- Codex: `~/.codex/skills/skill-name/hooks/hooks.json`
- OpenHuman: 根据需要配置

## SKILL.md 模板

每个 skill 的 SKILL.md 应该包含以下安装说明：

```markdown
## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/MoonforgeLabs/praxis-skills.git
cd praxis-skills/skills/skill-name
```

### 2. 安装（跨平台）

**macOS / Linux:**
```bash
python3 scripts/install.py
```

**Windows:**
```powershell
python scripts/install.py
```

**安装脚本会自动：**
- ✅ 创建软连接到 Claude Code、Codex、OpenHuman
- ✅ 配置必要的 hook
- ✅ 设置脚本执行权限

### 3. 检查依赖状态

```bash
python3 scripts/install.py --check
```

### 4. 开始使用

```bash
python3 scripts/usage_stats.py today
```
```

## 检查清单

创建 skill 时，检查以下项目：

- [ ] 使用 Python 安装脚本（`install.py`）
- [ ] 使用 `pathlib.Path` 处理路径
- [ ] 支持 macOS、Linux、Windows
- [ ] SKILL.md 包含完整的安装说明
- [ ] 提供依赖检查脚本（`check_dependencies.py`）
- [ ] 测试所有平台（或说明已知问题）

## 示例

参考 `praxis-ai-usage-stats` skill：
- `scripts/install.py` - 跨平台安装脚本
- `scripts/check_dependencies.py` - 依赖检查
- `SKILL.md` - 完整的安装说明
- `CROSS_PLATFORM.md` - 跨平台兼容性说明
