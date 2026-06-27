# Skill File Checklist

每个 skill 必须包含的文件清单。Curator intake 时逐项检查。

## 必需文件

| 文件 | 作用 | 所有 skill |
|------|------|-----------|
| `SKILL.md` | 主指令文件（含 frontmatter） | ✅ 必需 |
| `deps-manifest.json` | 依赖声明 + 层级 + 生命周期 | ✅ 必需 |

## 条件文件

| 文件 | 何时需要 | 说明 |
|------|---------|------|
| `setup.sh` | 有 ENHANCED/ADVANCED 依赖 | 分层安装脚本（CORE/ENHANCED/ADVANCED） |
| `update-deps.sh` | 外部依赖 >3 个 | 依赖更新脚本 |
| `scripts/*.py` | 需要辅助脚本 | Python 3.10+，尽量用 stdlib |
| `scripts/install.py` | 需要跨平台安装 | 替代 install.sh（Windows 兼容） |
| `references/vendor-manifest.yaml` | 有外部依赖 | 依赖备份清单 |
| `hooks/hooks.json` | 需要 hook 采集 | Claude Code hook 配置 |

## 可选文件

| 文件 | 作用 |
|------|------|
| `QUICKSTART.md` | 快速入门指南 |
| `README.md` | skill 级文档（通常 SKILL.md 足够） |
| `references/*.md` | 参考文档（设计决策、格式规范等） |

## Curator Intake 检查

创建新 skill 时，逐项确认：

- [ ] `SKILL.md` 存在，frontmatter 有 `name` 和 `description`
- [ ] `deps-manifest.json` 存在，包含 `tiers` 和 `dependencies` 字段
- [ ] 如果有 ENHANCED/ADVANCED 依赖 → `setup.sh` 存在
- [ ] 如果外部依赖 >3 个 → `update-deps.sh` 存在
- [ ] 所有脚本用 Python 3.10+ stdlib（CORE 层无 pip 依赖）
- [ ] 路径用 `pathlib.Path`，不用 `os.path`
- [ ] 安装脚本优先用 `install.py` 而非 `install.sh`

## 跨平台兼容

| 平台 | Python | fcntl | 路径分隔符 | 换行符 |
|------|--------|-------|-----------|--------|
| macOS | ✅ 3.10+ | ✅ | `/` | `\n` |
| Linux | ✅ 3.10+ | ✅ | `/` | `\n` |
| Windows | ✅ 3.10+ | ❌ | `\` | `\r\n` |

Windows 注意事项：
- `fcntl` 不可用 → 限流功能降级
- 路径用 `pathlib.Path` 自动处理
- 安装脚本用 `.py` 不用 `.sh`
- 换行符用 `encoding="utf-8"` 和 `newline=""` 处理
