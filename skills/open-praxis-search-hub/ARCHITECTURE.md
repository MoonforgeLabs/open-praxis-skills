# praxis-search-hub 架构设计

## 设计原则

1. **核心功能内置**：关键搜索功能不依赖外部工具
2. **扩展功能插件化**：高级功能通过插件实现
3. **渐进式增强**：基础功能开箱即用，高级功能可选安装

## 架构图

```
praxis-search-hub (核心)
        │
        ├── 内置功能（零依赖）
        │   ├── web 搜索（DuckDuckGo）
        │   ├── fetch 抓取（Jina Reader）
        │   ├── gh-lookup（Core API）
        │   └── gh-suggest（零 API）
        │
        ├── 可选插件（需安装）
        │   ├── agent-reach 插件
        │   │   ├── bili (B站)
        │   │   ├── opencli (小红书/头条)
        │   │   └── ...
        │   │
        │   ├── last30days 插件
        │   │   └── deep-research
        │   │
        │   └── anysearch 插件
        │       └── 垂直搜索
        │
        └── 配置层
            └── config/plugins.json
```

## 插件接口

### 搜索插件接口

```python
class SearchPlugin:
    """搜索插件基类"""
    
    name: str
    description: str
    version: str
    
    def is_available(self) -> bool:
        """检查插件是否可用"""
        raise NotImplementedError
    
    def search(self, query: str, **kwargs) -> dict:
        """执行搜索"""
        raise NotImplementedError
    
    def get_capabilities(self) -> list:
        """获取插件能力列表"""
        raise NotImplementedError
```

### 插件注册

```python
# config/plugins.json
{
  "plugins": {
    "agent-reach": {
      "enabled": true,
      "path": "~/.agents/skills/agent-reach",
      "commands": ["bili", "opencli"]
    },
    "last30days": {
      "enabled": true,
      "path": "~/.agents/skills/last30days",
      "commands": ["last30days.py"]
    },
    "anysearch": {
      "enabled": true,
      "api_endpoint": "https://api.anysearch.com/mcp",
      "api_key_env": "ANYSEARCH_API_KEY"
    }
  }
}
```

## 开源策略

### 1. 核心功能（必须）

- web 搜索（DuckDuckGo）
- fetch 抓取（Jina Reader）
- gh-lookup（Core API）
- gh-suggest（零 API）

**安装**：开箱即用，零依赖

### 2. 扩展功能（可选）

- B站/小红书/头条搜索（需 agent-reach）
- 深度研究（需 last30days）
- 垂直搜索（需 anysearch API）

**安装**：按需安装，有明确说明

### 3. 高级功能（插件）

- 自定义搜索源
- 自定义分析器
- 自定义导出格式

**安装**：插件市场或手动安装

---

## 开源文档结构

```
praxis-search-hub/
├── README.md              # 快速开始
├── INSTALLATION.md        # 安装指南
├── ARCHITECTURE.md        # 架构说明
├── PLUGINS.md             # 插件指南
├── CONTRIBUTING.md        # 贡献指南
├── LICENSE                # 开源协议
├── scripts/
│   ├── safe_search.py     # 核心脚本
│   └── lib/
│       ├── anysearch.py   # AnySearch 集成
│       └── plugins/       # 插件目录
└── config/
    └── plugins.json       # 插件配置
```

## 安装方式

### 方式 1: 最小安装（零依赖）

```bash
# 克隆仓库
git clone https://github.com/alex/praxis-search-hub.git

# 直接使用
python3 scripts/safe_search.py web "query"
python3 scripts/safe_search.py gh-lookup owner/repo
```

### 方式 2: 完整安装（所有功能）

```bash
# 克隆仓库
git clone https://github.com/alex/praxis-search-hub.git

# 安装依赖
./scripts/install_deps.sh

# 配置插件
./scripts/setup_plugins.sh
```

### 方式 3: 插件安装（按需）

```bash
# 安装特定插件
./scripts/install_plugin.sh agent-reach
./scripts/install_plugin.sh last30days
./scripts/install_plugin.sh anysearch
```

---

## 依赖管理

### 核心依赖（内置）

- Python 3.8+
- requests（可选，用于 API 调用）

### 扩展依赖（可选）

- agent-reach（B站/小红书/头条搜索）
- last30days（深度研究）
- gh CLI（GitHub 操作）

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
    "anysearch-skill": ">=2.1.0"
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

