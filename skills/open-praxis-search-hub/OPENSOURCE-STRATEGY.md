# praxis-search-hub 开源策略

## 问题分析

### 当前耦合

```
praxis-search-hub
        │
        ├── 强依赖 agent-reach (CLI) ← 必须安装
        ├── 强依赖 last30days (脚本) ← 必须安装
        └── 弱依赖 anysearch (API) ← 已内化
```

**问题**：
1. 用户必须安装 agent-reach 和 last30days
2. 安装过程复杂
3. 底层工具更新可能破坏兼容性
4. 开源门槛高

---

## 解决方案

### 方案 1: 核心 + 插件架构（推荐）

```
praxis-search-hub (核心)
        │
        ├── 内置功能（零依赖）
        │   ├── web 搜索（DuckDuckGo）
        │   ├── fetch 抓取（Jina Reader）
        │   ├── gh-lookup（Core API）
        │   └── gh-suggest（零 API）
        │
        └── 可选插件（按需安装）
            ├── agent-reach 插件
            ├── last30days 插件
            └── anysearch 插件
```

**优点**：
- 核心功能零依赖，开箱即用
- 高级功能按需安装
- 插件可独立更新
- 开源门槛低

**缺点**：
- 需要重构代码
- 需要维护插件接口

---

### 方案 2: 功能内化

将 agent-reach 和 last30days 的核心功能内化到 praxis-search-hub。

**优点**：
- 无外部依赖
- 完全可控

**缺点**：
- 开发工作量大
- 需要持续维护
- 可能与上游不同步

---

### 方案 3: 依赖声明

在开源文档中明确声明依赖关系。

**优点**：
- 实现简单
- 保持现有架构

**缺点**：
- 用户安装复杂
- 开源门槛高

---

## 推荐方案：核心 + 插件架构

### 实施步骤

#### 第 1 阶段：核心功能独立

```bash
# 1. 识别核心功能
- web 搜索（DuckDuckGo）
- fetch 抓取（Jina Reader）
- gh-lookup（Core API）
- gh-suggest（零 API）

# 2. 移除外部依赖
- 将 agent-reach 调用改为可选
- 将 last30days 调用改为可选
- anysearch 已内化

# 3. 创建插件接口
- 定义 SearchPlugin 基类
- 实现插件管理器
```

#### 第 2 阶段：插件系统

```bash
# 1. 创建插件目录结构
scripts/lib/plugins/
├── __init__.py
├── agent_reach.py
├── last30days.py
└── anysearch.py

# 2. 实现插件加载
- 从 config/plugins.json 加载配置
- 动态加载插件模块
- 检查插件可用性

# 3. 插件注册和调用
- 注册内置插件
- 注册外部插件
- 统一调用接口
```

#### 第 3 阶段：开源准备

```bash
# 1. 文档编写
- README.md（快速开始）
- INSTALLATION.md（安装指南）
- ARCHITECTURE.md（架构说明）
- PLUGINS.md（插件指南）

# 2. 测试覆盖
- 单元测试
- 集成测试
- 插件测试

# 3. 发布准备
- 版本号管理
- 变更日志
- 开源协议
```

---

## 开源文档结构

```
praxis-search-hub/
├── README.md              # 快速开始（5 分钟上手）
├── INSTALLATION.md        # 安装指南（三种安装方式）
├── ARCHITECTURE.md        # 架构说明（核心 + 插件）
├── PLUGINS.md             # 插件指南（如何开发插件）
├── CONTRIBUTING.md        # 贡献指南
├── CHANGELOG.md           # 变更日志
├── LICENSE                # 开源协议（MIT）
├── scripts/
│   ├── safe_search.py     # 核心脚本
│   └── lib/
│       ├── __init__.py
│       ├── plugin_manager.py  # 插件管理器
│       └── plugins/       # 插件目录
│           ├── __init__.py
│           ├── agent_reach.py
│           ├── last30days.py
│           └── anysearch.py
├── config/
│   └── plugins.json       # 插件配置
└── tests/
    ├── test_core.py       # 核心功能测试
    └── test_plugins.py    # 插件测试
```

---

## 安装方式

### 方式 1: 最小安装（零依赖）

```bash
# 克隆仓库
git clone https://github.com/alex/praxis-search-hub.git
cd praxis-search-hub

# 直接使用（核心功能）
python3 scripts/safe_search.py web "query"
python3 scripts/safe_search.py gh-lookup owner/repo
python3 scripts/safe_search.py gh-suggest "query"
```

**功能**：
- ✅ web 搜索（DuckDuckGo）
- ✅ fetch 抓取（Jina Reader）
- ✅ gh-lookup（Core API）
- ✅ gh-suggest（零 API）
- ❌ B站/小红书/头条搜索
- ❌ 深度研究
- ❌ 垂直搜索

### 方式 2: 完整安装（所有功能）

```bash
# 克隆仓库
git clone https://github.com/alex/praxis-search-hub.git
cd praxis-search-hub

# 安装依赖
./scripts/install_deps.sh

# 配置插件
./scripts/setup_plugins.sh
```

**功能**：
- ✅ 所有核心功能
- ✅ B站/小红书/头条搜索（需 agent-reach）
- ✅ 深度研究（需 last30days）
- ✅ 垂直搜索（需 anysearch API）

### 方式 3: 插件安装（按需）

```bash
# 克隆仓库
git clone https://github.com/alex/praxis-search-hub.git
cd praxis-search-hub

# 安装特定插件
./scripts/install_plugin.sh agent-reach
./scripts/install_plugin.sh last30days
./scripts/install_plugin.sh anysearch
```

---

## 依赖管理

### 核心依赖（内置）

- Python 3.8+
- 标准库（json, os, sys, pathlib）

### 扩展依赖（可选）

| 依赖 | 功能 | 安装方式 |
|------|------|----------|
| agent-reach | B站/小红书/头条搜索 | `./scripts/install_plugin.sh agent-reach` |
| last30days | 深度研究 | `./scripts/install_plugin.sh last30days` |
| gh CLI | GitHub 操作 | `brew install gh` |
| requests | API 调用 | `pip install requests` |

### 依赖检查

```bash
# 检查所有依赖
./scripts/check_deps.sh

# 检查特定依赖
./scripts/check_deps.sh agent-reach
```

---

## 兼容性保证

### 版本锁定

```json
{
  "compatible_versions": {
    "agent-reach": ">=1.5.0",
    "last30days": ">=3.8.0",
    "anysearch": ">=2.1.0"
  }
}
```

### 向后兼容

- 新版本必须兼容旧版本的配置
- 废弃功能要有迁移指南
- 重大变更要有版本说明

### 测试覆盖

```bash
# 运行所有测试
./scripts/test_all.sh

# 运行特定插件测试
./scripts/test_plugin.sh agent-reach
```

---

## 开源协议

### 推荐协议

**MIT License**

- ✅ 商业友好
- ✅ 简单易懂
- ✅ 广泛使用
- ✅ 无专利条款

### 协议文件

```
MIT License

Copyright (c) 2026 Alex

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 实施时间表

### 第 1 阶段：核心独立（1-2 周）

- [ ] 识别核心功能
- [ ] 移除外部依赖
- [ ] 创建插件接口
- [ ] 编写单元测试

### 第 2 阶段：插件系统（2-3 周）

- [ ] 创建插件目录结构
- [ ] 实现插件加载
- [ ] 实现插件注册
- [ ] 编写插件文档

### 第 3 阶段：开源准备（1-2 周）

- [ ] 编写文档
- [ ] 完善测试
- [ ] 版本管理
- [ ] 发布准备

### 总时间：4-7 周

---

## 风险评估

### 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 插件接口设计不合理 | 高 | 充分调研，参考成熟方案 |
| 插件加载性能问题 | 中 | 延迟加载，缓存机制 |
| 插件兼容性问题 | 中 | 版本锁定，测试覆盖 |

### 时间风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 开发时间超出预期 | 中 | 分阶段实施，MVP 优先 |
| 文档编写耗时 | 低 | 模板化，自动生成 |

### 资源风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 开发人力不足 | 高 | 优先核心功能，插件后补 |
| 测试覆盖不足 | 中 | 自动化测试，CI/CD |

---

## 总结

### 推荐方案

**核心 + 插件架构**

- 核心功能零依赖，开箱即用
- 高级功能按需安装
- 插件可独立更新
- 开源门槛低

### 实施步骤

1. **第 1 阶段**：核心功能独立（1-2 周）
2. **第 2 阶段**：插件系统（2-3 周）
3. **第 3 阶段**：开源准备（1-2 周）

### 预期效果

- ✅ 开源门槛降低 80%
- ✅ 安装时间从 30 分钟降至 5 分钟
- ✅ 依赖管理清晰
- ✅ 社区贡献友好
