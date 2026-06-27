# 三渠道发布配置

## 📊 渠道总览

| 渠道 | 前缀 | 用途 | 仓库 | 可见性 |
|------|------|------|------|--------|
| **Personal** | `praxis-` | 个人使用 | `MoonforgeLabs/praxis-skills` | 私有 |
| **Internal** | `org-praxis-` | 公司内部 | `ai-labs/org-praxis-skills` | 内部 |
| **Open Source** | `open-praxis-` | 开源发布 | `MoonforgeLabs/open-praxis-skills` | 公开 |

---

## 🔗 仓库地址

### 1. Personal（个人）

**用途**: 个人开发和测试

**仓库信息**:
- **GitHub**: `https://github.com/MoonforgeLabs/praxis-skills.git`
- **SSH**: `git@github.com:MoonforgeLabs/praxis-skills.git`
- **本地路径**: `~/Documents/myCode/skills/praxis-skills/`
- **安装路径**: `~/.claude/skills/praxis-xxx/`

**特点**:
- 包含所有 skill（包括内部工具）
- 包含创作过程资产
- 包含私有配置和密钥
- 不对外发布

**推送命令**:
```bash
cd ~/Documents/myCode/skills/praxis-skills
git push origin main
```

---

### 2. Internal（公司内部）

**用途**: 公司内部使用，包含商业逻辑

**仓库信息**:
- **GitLab**: `https://git.n.xiaomi.com/ai-labs/org-praxis-skills.git`
- **SSH**: `git@git.n.xiaomi.com:ai-labs/org-praxis-skills.git`
- **本地路径**: `~/Documents/myCode/org/org-praxis-skills/`
- **安装路径**: `~/.claude/skills/org-praxis-xxx/`

**特点**:
- 只包含可发布的 skill
- 移除创作过程资产
- 包含公司内部依赖
- 需要内网访问

**推送命令**:
```bash
cd ~/Documents/myCode/org/org-praxis-skills
git push gitlab main
```

**Skill 命名**:
```
praxis-translate → org-praxis-translate
praxis-diagram → org-praxis-diagram
```

---

### 3. Open Source（开源）

**用途**: 对外开源，社区使用

**仓库信息**:
- **GitHub**: `https://github.com/MoonforgeLabs/open-praxis-skills.git`
- **SSH**: `git@github.com:MoonforgeLabs/open-praxis-skills.git`
- **本地路径**: `~/Documents/myCode/open/open-praxis-skills/`
- **安装路径**: `~/.claude/skills/open-praxis-xxx/`

**特点**:
- 只包含 CORE 层 skill
- 移除所有内部依赖
- 移除私有路径
- 完全独立可用

**推送命令**:
```bash
cd ~/Documents/myCode/open/open-praxis-skills
git push origin main
```

**Skill 命名**:
```
praxis-translate → open-praxis-translate
praxis-diagram → open-praxis-diagram
```

---

## 📋 发布流程

### 完整发布流程

```
1. 在 praxis-skills 中开发和测试
   ↓
2. 用 praxis-skill-publish 评估
   - Phase 0: Scrub（擦除创作过程资产）
   - Phase 1-5: 验证和测试
   ↓
3. 在 release-manifest.json 的 approved 中注册
   ↓
4. 运行 sync-repos.sh 同步到下游仓库
   ↓
5. 分别推送到各渠道仓库
```

### 分步发布流程

#### Step 1: 准备发布

```bash
# 检查 skill 是否准备好
python3 scripts/quick_validate.py /path/to/skill

# 检查是否有敏感信息
grep -rn "/Users/alex\|PRAXIS_SKILLS_DIR\|praxis-skill-forge" SKILL.md
```

#### Step 2: 选择目标渠道

| Skill 类型 | Personal | Internal | Public |
|-----------|----------|----------|--------|
| 个人工具 | ✅ | ❌ | ❌ |
| 公司内部 | ✅ | ✅ | ❌ |
| 开源发布 | ✅ | ✅ | ✅ |
| 元工具（forge/publish） | ✅ | ❌ | ❌ |

#### Step 3: 复制并重命名

```bash
# 复制到 Internal 渠道
cp -r skills/praxis-skills/praxis-xxx/ ~/Documents/myCode/org/org-praxis-skills/org-praxis-xxx/

# 复制到 Open Source 渠道
cp -r skills/praxis-skills/praxis-xxx/ ~/Documents/myCode/open/open-praxis-skills/open-praxis-xxx/
```

#### Step 4: 渠道适配

**Internal 渠道**:
```bash
# 重命名目录
mv praxis-xxx org-praxis-xxx

# 更新 SKILL.md 中的引用
sed -i '' 's/praxis-/org-praxis-/g' SKILL.md

# 移除创作过程资产
# - praxis-skill-forge
# - intake-rubric
# - capability-tiers
# - knowledge-radar
```

**Open Source 渠道**:
```bash
# 重命名目录
mv praxis-xxx open-praxis-xxx

# 更新 SKILL.md 中的引用
sed -i '' 's/praxis-/open-praxis-/g' SKILL.md

# 移除所有内部依赖
# - 移除 org-praxis-* 引用
# - 移除私有路径
# - 移除公司内部工具
```

#### Step 5: 验证发布

```bash
# 验证命名
grep -r "praxis-" SKILL.md | grep -v "praxis-org-" | grep -v "praxis-pub-"

# 验证无敏感信息
grep -rn "/Users/alex\|PRAXIS_SKILLS_DIR" SKILL.md

# 验证独立运行
# 在干净环境中测试 skill
```

#### Step 6: 推送到各渠道

```bash
# Personal
cd ~/Documents/myCode/skills/praxis-skills
git add . && git commit -m "feat(xxx): 描述" && git push origin main

# Internal
cd ~/Documents/myCode/org/org-praxis-skills
git add . && git commit -m "feat(org-praxis-xxx): 描述" && git push gitlab main

# Open Source
cd ~/Documents/myCode/open/open-praxis-skills
git add . && git commit -m "feat(open-praxis-xxx): 描述" && git push origin main
```

---

## 📁 目录结构

### 核心规则

**三个独立的 Git 工程目录**：
1. `skills/praxis-skills/` - Personal 渠道（开发和测试）
2. `org/skills/` - Internal 渠道（公司内部发布）
3. `public/skills/` - Public 渠道（开源发布）

**发布流程**：
1. 在 `skills/praxis-skills/` 中开发和测试
2. 裁剪后复制到 `org/skills/` 或 `public/skills/`
3. 在对应的目录中进行提交和发布

### 目录结构

```
~/Documents/myCode/
├── skills/
│   └── praxis-skills/           # Personal 渠道（开发和测试）
│       └── skills/
│           ├── praxis-translate/
│           ├── praxis-diagram/
│           └── ...
├── org/                         # Internal 渠道（公司内部发布）
│   └── org-praxis-skills/       # 独立的 Git 工程
│       ├── org-praxis-translate/
│       ├── org-praxis-diagram/
│       └── ...
└── open/                        # Open Source 渠道（开源发布）
    └── open-praxis-skills/      # 独立的 Git 工程
        ├── open-praxis-translate/
        ├── open-praxis-diagram/
        └── ...
```

### 各目录职责

| 目录 | 用途 | Git 仓库 | 提交和发布 |
|------|------|---------|-----------|
| `skills/praxis-skills/` | 开发和测试 | `MoonforgeLabs/praxis-skills` | 个人开发 |
| `org/org-praxis-skills/` | 公司内部发布 | `ai-labs/org-praxis-skills` | 公司内部 |
| `open/open-praxis-skills/` | 开源发布 | `MoonforgeLabs/open-praxis-skills` | 公开发布 |

---

## 🔧 自动化脚本

### sync-repos.sh

```bash
#!/bin/bash
# 同步 skill 到下游仓库

SKILL_NAME=$1
TARGET=$2  # org | open | both

# 检查是否在 approved 列表
if ! jq -e ".approved[\"$SKILL_NAME\"]" release-manifest.json > /dev/null; then
    echo "❌ $SKILL_NAME not in approved list"
    exit 1
fi

# 同步到 Internal
if [ "$TARGET" = "org" ] || [ "$TARGET" = "both" ]; then
    echo "📦 Syncing to Internal..."
    cp -r "skills/$SKILL_NAME" ~/Documents/myCode/org/org-praxis-skills/org-${SKILL_NAME}
    cd ~/Documents/myCode/org/org-praxis-skills/org-${SKILL_NAME}
    mv "$SKILL_NAME" "org-${SKILL_NAME}"
    sed -i '' "s/praxis-/org-praxis-/g" SKILL.md
    # 移除创作过程资产
    cd -
fi

# 同步到 Open Source
if [ "$TARGET" = "open" ] || [ "$TARGET" = "both" ]; then
    echo "📦 Syncing to Open Source..."
    cp -r "skills/$SKILL_NAME" ~/Documents/myCode/open/open-praxis-skills/open-${SKILL_NAME}
    cd ~/Documents/myCode/open/open-praxis-skills/open-${SKILL_NAME}
    mv "$SKILL_NAME" "open-${SKILL_NAME}"
    sed -i '' "s/praxis-/open-praxis-/g" SKILL.md
    # 移除所有内部依赖
    cd -
fi

echo "✅ Sync complete"
```

---

## 📊 发布检查清单

### Personal 渠道

- [ ] Skill 通过 quick_validate.py
- [ ] 包含完整的 SKILL.md
- [ ] 包含所有依赖脚本
- [ ] 已添加到 release-manifest.json

### Internal 渠道

- [ ] 已从 Personal 复制
- [ ] 已重命名为 `org-praxis-xxx`
- [ ] 已更新所有引用为 `org-praxis-`
- [ ] 已移除创作过程资产
- [ ] 已移除私有路径
- [ ] 在干净环境中测试通过

### Open Source 渠道

- [ ] 已从 Personal 复制
- [ ] 已重命名为 `open-praxis-xxx`
- [ ] 已更新所有引用为 `open-praxis-`
- [ ] 已移除所有内部依赖
- [ ] 已移除私有路径
- [ ] 已移除公司内部工具
- [ ] 在干净环境中测试通过
- [ ] README 包含安装说明

---

## 🆘 常见问题

### Q: 如何确定 skill 应该发布到哪个渠道？

**A**: 根据 skill 的依赖和用途：
- 依赖私有基础设施 → 只发 Personal
- 依赖公司内部工具 → 发 Personal + Internal
- 完全独立可用 → 发所有渠道

### Q: 如何处理跨 skill 引用？

**A**: 
- Personal: 使用 `praxis-xxx`
- Internal: 使用 `praxis-org-xxx`
- Public: 使用 `praxis-pub-xxx` 或提供 fallback

### Q: 如何同步更新？

**A**: 
1. 先更新 Personal 版本
2. 运行 `sync-repos.sh` 同步到下游
3. 分别推送到各渠道仓库

---

**三渠道发布配置完成！** 🎉
