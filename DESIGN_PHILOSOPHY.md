# Alex Skills 设计理念

本文档记录 praxis-skills 项目中核心 skill 的设计理念和设计原则。

## 目录

- [praxis-skill-forge](#praxis-skill-forge) - Skill 管理元技能
- [praxis-ai-usage-stats](#praxis-ai-usage-stats) - AI 使用统计
- [praxis-search-hub](#praxis-search-hub) - 安全搜索网关
- [通用设计原则](#通用设计原则)

---

## praxis-skill-forge

**定位**：管理所有 skill 的元技能（meta-skill）

### 核心理念

1. **治理优先**
   - 先评估，再创建
   - 避免重复 skill
   - 优先合并/更新，而非新建

2. **质量驱动**
   - 每行代码都必须改变行为
   - 消除无用内容（no-op）
   - 控制 token 预算（SKILL.md < 500 行）

3. **可发现性**
   - 描述符前置触发词
   - 第三人称祈使句
   - 100-200 字符最佳

4. **跨平台兼容**
   - Python 安装脚本（非 Bash）
   - pathlib.Path 处理路径
   - os.symlink 创建软连接

5. **层级划分**
   - CORE: Python 标准库，零依赖
   - ENHANCED: 可选 CLI，优雅降级
   - ADVANCED: 外部 skill/API，需移除

### 设计决策

| 决策 | 理由 |
|------|------|
| 使用 Python 安装脚本 | 跨平台兼容（macOS/Linux/Windows） |
| 软连接而非复制 | 一处修改，多处同步 |
| 自动分类+用户确认 | 科学判定 + 人工把关 |
| 层级划分 | 支持开源裁剪 |

---

## praxis-ai-usage-stats

**定位**：跨 Runtime 的 AI 工具使用统计

### 核心理念

1. **数据隐私**
   - 100% 本地存储
   - 不上传任何数据
   - Token 脱敏
   - Context 截断（200 字符）

2. **实时捕获**
   - PostToolUse hook 自动记录
   - 零延迟，不阻塞 Claude
   - 失败时降级到文件日志

3. **多 Runtime 支持**
   - Claude Code
   - Codex
   - Gemini CLI
   - 统一数据模型

4. **自动迁移**
   - 安装后自动迁移历史数据
   - 查询时自动检测并迁移
   - 用户无需手动操作

5. **可视化**
   - Markdown 终端报告
   - 交互式 HTML 报告
   - 无需服务器，双击打开

### 设计决策

| 决策 | 理由 |
|------|------|
| SQLite 存储 | 轻量、跨平台、无需配置 |
| 自动迁移 | 用户体验，无需手动 --migrate |
| 交互式 HTML | 无需服务器，支持筛选 |
| 成本估算 | 帮助用户了解 API 花费 |
| 健康评分 | 综合评估使用模式 |

### 数据流

```
Claude Code 调用工具
  → PostToolUse hook 触发
    → hook_collect.py 捕获
      → SQLite 数据库
        → usage_stats.py 查询
          → Markdown/HTML 报告
```

---

## praxis-search-hub

**定位**：统一搜索网关，处理风控、限流、审计

### 核心理念

1. **账号安全优先**
   - GitHub flagged 期间默认禁用
   - 显式解除风控后才恢复
   - 不绕路猛搜

2. **按渠道分级**
   - RSS / 官方网页优先
   - 搜索 API 次之
   - 登录态平台谨慎使用

3. **集中审计**
   - 每次搜索记录日志
   - 不记录 token
   - 可追溯

4. **显式降级**
   - 渠道禁用时返回"已跳过"
   - 不伪造结果
   - 不绕路调用

5. **可恢复**
   - GitHub 解除 flagged 后
   - 通过配置开关逐步恢复

### 设计决策

| 决策 | 理由 |
|------|------|
| 默认禁用 GitHub 搜索 | 保护账号安全 |
| 搜索网关模式 | 统一入口，便于审计 |
| 显式降级 | 用户知道哪些功能不可用 |
| 配置开关 | 灵活控制各渠道 |

### 搜索优先级

```
1. RSS / 官方网页（零风险）
2. Exa 语义搜索（低风险）
3. GitHub API（需风控）
4. 登录态平台（谨慎使用）
```

---

## 通用设计原则

### 1. 跨平台兼容

**要求**：
- ✅ Python 安装脚本（`install.py`）
- ✅ `pathlib.Path` 处理路径
- ✅ `os.symlink` 创建软连接
- ✅ 提供 `check_dependencies.py`

**原因**：用户可能在 macOS、Linux、Windows 上使用

### 2. 安装说明

**要求**：
- ✅ SKILL.md 包含 `🚀 Quick Start`
- ✅ 跨平台安装命令
- ✅ 依赖检查示例
- ✅ 使用示例

**模板**：参考 `references/installation-template.md`

### 3. 层级划分

**要求**：
- ✅ 每个命令/功能有层级标记
- ✅ CORE: Python 标准库，零依赖
- ✅ ENHANCED: 可选 CLI，优雅降级
- ✅ ADVANCED: 外部 skill/API，需移除

**工具**：`auto_classify_tiers.py`（自动分类+用户确认）

### 4. 数据隐私

**要求**：
- ✅ 本地存储，不上传
- ✅ Token 脱敏
- ✅ Context 截断
- ✅ 用户可控

### 5. 优雅降级

**要求**：
- ✅ 依赖不存在时跳过，不崩溃
- ✅ 返回"已跳过"，不伪造结果
- ✅ 提供恢复路径

### 6. 可审计

**要求**：
- ✅ 操作日志
- ✅ 不记录敏感信息
- ✅ 可追溯

---

## 开源策略

### 层级与开源

| 层级 | 开源策略 | 说明 |
|------|---------|------|
| CORE | ✅ 保留 | 零依赖，直接开源 |
| ENHANCED | ✅ 保留 + 文档 | 优雅降级，文档说明 |
| ADVANCED | ❌ 移除 | 外部依赖，裁剪 |

### 开源检查清单

- [ ] 所有命令有层级标记
- [ ] ENHANCED 有降级文档
- [ ] ADVANCED 有移除路径
- [ ] 跨平台安装脚本
- [ ] 完整的安装说明
- [ ] 依赖检查脚本

---

## 更新日志

- **2026-06-26**: 初始版本，记录三个核心 skill 的设计理念
