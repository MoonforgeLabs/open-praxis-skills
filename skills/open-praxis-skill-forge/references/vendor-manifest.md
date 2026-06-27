# Vendor Manifest 规范

## 目的

为每个 skill 的外部依赖保留本地备份 + 可追踪 manifest，防止上游删除、闭源或改协议。

## 原则

- 不止声明依赖，必须保留备份
- 备份和 manifest 保持同步
- 上游消失时，从 vendor 目录恢复

## 目录结构

```
skills/<skill-name>/
├── SKILL.md
├── scripts/
└── references/
    ├── vendor-manifest.yaml      ← 依赖清单
    └── vendor/                   ← 备份目录
        ├── <dep-name>/
        │   ├── VERSION           ← 来源、日期、说明
        │   └── <备份文件>
        └── formats/              ← 运行时格式文档
            └── <format-name>.md
```

## vendor-manifest.yaml 格式

```yaml
dependencies:
  - name: <依赖名称，kebab-case>
    type: <pip | cli | hook | skill | runtime-format | config>
    source: <来源 URL 或路径>
    description: <一句话说明>
    install_path: <实际安装路径，可选>
    backup_path: <vendor 内的相对路径>
    backup_version: <日期 YYYY-MM-DD 或版本号>
    fallback_note: <降级说明>
```

## 类型定义

| type | 说明 | 备份内容 |
|------|------|----------|
| `pip` | Python 包 | wheel/tar.gz 或源码 |
| `cli` | 命令行工具 | 可执行文件 + 依赖 |
| `hook` | 运行时 hook 脚本 | 脚本文件 |
| `skill` | 其他 skill 的 SKILL.md + references | 整个 skill 目录 |
| `runtime-format` | 运行时日志/API 格式 | 格式文档（不可备份 API 本身） |
| `config` | 配置文件 | 配置文件副本 |

## VERSION 文件格式

每个 vendor 子目录下必须有 VERSION 文件：

```
source: <原始路径或 URL>
backup_date: YYYY-MM-DD
description: <一句话说明>
```

## 工作流

### 创建新 skill 时
1. 识别所有外部依赖（pip 包、CLI 工具、hook、其他 skill、运行时格式）
2. 创建 `references/vendor-manifest.yaml`
3. 对每个依赖：复制到 `vendor/<name>/`，创建 `VERSION` 文件
4. 填写 manifest 中每条依赖的 `fallback_note`

### 更新依赖时
1. 对比 manifest 中的 `backup_version` 和上游最新版本
2. 更新备份文件和 `VERSION`
3. 更新 manifest 中的 `backup_version`

### 上游消失时（降级）
1. 读取 manifest 的 `fallback_note`
2. 从 `backup_path` 恢复文件到 `install_path`
3. 验证功能正常

## 检查清单

创建或更新 skill 时，问自己：
- [ ] 这个依赖的上游会消失吗？
- [ ] 如果消失了，skill 还能用吗？
- [ ] 备份是最新的吗？
- [ ] manifest 和实际 vendor 目录一致吗？
- [ ] 每个 vendor 子目录都有 VERSION 文件吗？
