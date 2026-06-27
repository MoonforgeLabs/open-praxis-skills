# 安装说明模板

## 概述

每个 skill 的 SKILL.md 应该包含清晰、完整的安装说明，让用户可以轻松安装和使用。

## 模板

```markdown
## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/MoonforgeLabs/praxis-skills.git
cd praxis-skills/skills/<skill-name>
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
- ✅ 配置必要的 hook（如果需要）
- ✅ 设置脚本执行权限

### 3. 检查依赖状态

```bash
python3 scripts/install.py --check
```

输出示例：
```
============================================================
📊 <skill-name> 依赖检查报告
============================================================

【软连接】
  ✅ Claude
  ✅ Codex
  ✅ Openhuman

【Hook 配置】
  ✅ Claude Code
  ✅ Codex
  ➖ OpenHuman (不需要)

【数据存储】
  ✅ 数据库

总结: ✅ 6/6 正常
============================================================
```

### 4. 迁移旧数据（可选）

```bash
# 从旧数据迁移（如果需要）
python3 scripts/migrate.py
```

### 5. 开始使用

```bash
# 基本用法
python3 scripts/<main-script>.py

# 查看帮助
python3 scripts/<main-script>.py --help
```

## 📖 详细用法

### 安装选项

```bash
# 安装到所有 runtime（默认）
python3 scripts/install.py

# 只安装到 Claude Code
python3 scripts/install.py --claude

# 只安装到 Codex
python3 scripts/install.py --codex

# 只安装到 OpenHuman
python3 scripts/install.py --openhuman

# 检查依赖状态
python3 scripts/install.py --check
```

### 常用命令

```bash
# 命令 1
python3 scripts/<script>.py <args>

# 命令 2
python3 scripts/<script>.py <args>

# 命令 3
python3 scripts/<script>.py <args>
```

### 配置选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--option1` | value1 | 说明 1 |
| `--option2` | value2 | 说明 2 |
| `--option3` | value3 | 说明 3 |

## 🔧 故障排除

### 问题 1: 描述

**解决方案**：
```bash
# 解决命令
```

### 问题 2: 描述

**解决方案**：
```bash
# 解决命令
```

## 📚 更多信息

- 详细文档: [README.md](README.md)
- 跨平台说明: [CROSS_PLATFORM.md](CROSS_PLATFORM.md)
- 依赖清单: [references/vendor-manifest.yaml](references/vendor-manifest.yaml)
```

## 要求

### 必须包含的内容

1. **克隆仓库** - 明确的仓库地址
2. **安装步骤** - 跨平台安装命令
3. **依赖检查** - 如何验证安装成功
4. **开始使用** - 基本用法示例

### 可选包含的内容

1. **迁移旧数据** - 如果需要迁移
2. **详细用法** - 高级选项和配置
3. **故障排除** - 常见问题和解决方案
4. **更多信息** - 相关文档链接

### 格式要求

1. **使用代码块** - 命令和代码用 ``` 包裹
2. **添加说明** - 每个步骤有简短说明
3. **使用 emoji** - 增加可读性（✅ ❌ ⚠️ 📦 🚀）
4. **表格** - 配置选项用表格展示

## 示例

参考 `praxis-ai-usage-stats` 的 SKILL.md：
- 完整的 5 步安装流程
- 跨平台安装命令
- 依赖检查示例
- 详细用法说明
