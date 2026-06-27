# open-open-praxis-skills

A portable skill collection for AI coding agents — learning, monitoring, translation, content creation, search governance, and daily productivity.

[![Skills](https://skills.sh/b/MoonforgeLabs/open-open-praxis-skills)](https://skills.sh/MoonforgeLabs/open-open-praxis-skills)

## Highlights

- **30+ skills** covering knowledge, content, visual, developer, and personal operations
- **Zero-dependency core** — most skills use only Python stdlib
- **Cross-agent portable** — works with Claude Code, Codex, OpenCode, Gemini CLI, and more ([compatibility guide](docs/skill-compatibility.md))
- **Tiered architecture** — CORE / ENHANCED / ADVANCED for graceful degradation ([design philosophy](DESIGN_PHILOSOPHY.md))

## Platform Support

| Platform | CORE (零依赖) | ENHANCED (可选 CLI) | ADVANCED (外部 skill) |
|----------|:---:|:---:|:---:|
| **macOS** | ✅ | ✅ | ✅ |
| **Linux** | ✅ | ✅ | ✅ |
| **Windows** | ✅ | ⚠️ 部分 | ❌ |

- **CORE 层**: 纯 Python 标准库，全平台可用
- **ENHANCED 层**: 依赖 CLI 工具（gh、mcporter、opencli），Windows 需手动安装
- **ADVANCED 层**: 依赖 Unix 特性（fcntl）或外部 skill，Windows 不支持
- 详见 [跨平台指南](skills/open-praxis-skill-forge/references/cross-platform-guide.md)

## Installation

### Quick Install (Claude Code)

```bash
# Install from skills.sh
npx skills add MoonforgeLabs/open-open-praxis-skills -g

# Or clone manually
git clone https://github.com/MoonforgeLabs/open-open-praxis-skills.git
cd open-open-praxis-skills
```

### Install a Single Skill

```bash
cd skills/open-praxis-search-hub
bash setup.sh --tier CORE     # Zero dependencies
bash setup.sh --tier ENHANCED # + optional CLI tools
```

### Verify

```bash
python3 ~/.claude/skills/open-praxis-search-hub/scripts/safe_search.py doctor
```

## Skills

Skills are grouped by primary usage scenario. See [Skill Taxonomy](docs/skill-taxonomy.md) for classification rules.

### Knowledge & Research

| Skill | Trigger | What it does | Dependency |
|-------|---------|--------------|------------|
| `open-praxis-news-aggregator` | "每日简报", "tech news" | Fetches and analyzes news from 28 sources (HN, GitHub, HF Papers, Weibo, etc.) with 6 pre-configured daily briefing profiles | WebSearch/WebFetch |
| `open-praxis-search-hub` | "安全搜索", "搜索网关", "GitHub 搜索风控" | Central search-hub gateway with GitHub flagged-account protection, `doctor`, channel switches, audit logs, Agent-Reach routing, and last30days deep-research handoff | `mcporter`, `opencli`, `bili`, last30days optional |
| `open-praxis-url-to-markdown` | "抓取网页", "save page as markdown" | Fetches any URL and converts to clean markdown with frontmatter | WebFetch or curl |
| `open-praxis-youtube-transcript` | "YouTube字幕", "get transcript" | Downloads YouTube transcripts with chapter segmentation and speaker identification | `yt-dlp` |
| `open-praxis-knowledge-radar` | "记录想法", "任务雷达", "还有哪些问题", "学习雷达", "今天学什么" | 知识捕获管线 + 学习编排：文章/链接输入 → 归类入库 → 学习内化 → 应用输出。支持手动输入、钉钉消息自动订阅、URL 自动抓取、每日/每周学习工作流 | Local JSONL store optional |

### Content & Writing

| Skill | Trigger | What it does | Dependency |
|-------|---------|--------------|------------|
| `open-praxis-translate` | "翻译", "translate", "精翻" | Three-mode translation: quick, normal, refined. Supports custom glossaries and terminology consistency | None |
| `open-praxis-format-markdown` | "排版", "format markdown" | Formats articles with frontmatter, headings, bold, lists — without changing content | None |
| `open-praxis-humanizer-zh` | "去AI味", "humanize" | Detects and removes AI writing patterns from Chinese text | None |
| `open-praxis-markdown-to-html` | "转HTML", "markdown to html" | Converts markdown to styled standalone HTML with themes, syntax highlighting, and TOC | None |

### Visual & Media

| Skill | Trigger | What it does | Dependency |
|-------|---------|--------------|------------|
| `open-praxis-diagram` | "画图", "diagram", "flowchart" | Creates dark-themed SVG diagrams: architecture, flowchart, sequence, mind map, timeline, state machine, and more | None |
| `open-praxis-compress-image` | "压缩图片", "compress image" | Compresses images to WebP/PNG/JPEG using the best available tool | `sips`, `cwebp`, ImageMagick, or Sharp |
| `open-praxis-slide-deck` | "做PPT", "create slides" | Generates HTML slide decks with keyboard navigation, speaker notes, and progress bar | None |
| `open-praxis-logo-generator` | "做logo", "design logo" | Generates 6+ professional SVG logo variants with interactive showcase page | None |
| `open-praxis-image-gen` | "生成图片", "generate image" | AI image generation via API or programmatic SVG illustrations | Optional AI image API |
| `open-praxis-infographic` | "信息图", "infographic" | Creates data-driven infographics such as KPI dashboards, timelines, and comparisons | Optional AI image API |
| `open-praxis-image-cards` | "图片卡片", "social card" | Generates styled image cards for social media sharing | Optional AI image API |
| `open-praxis-cover-image` | "封面图", "cover image" | Creates article cover/hero images with gradient, geometric, or minimal styles | Optional AI image API |
| `open-praxis-youtube-clipper` | "视频剪辑", "clip video" | AI-powered YouTube video clipper: downloads, analyzes chapters, clips segments, adds bilingual subtitles | `yt-dlp` + `ffmpeg-full` |

### Developer & Automation

| Skill | Trigger | What it does | Dependency |
|-------|---------|--------------|------------|
| `open-praxis-github-watchtower` | "GitHub日报", "fork sync", "watchtower" | Operates local GitHub repository monitoring, fork synchronization, Feishu reports, and launchd scheduling | Local watchtower project |
| `open-praxis-agent-reach-ops` | "Agent-Reach", "agent-reach doctor", "transcribe" | Operates Agent-Reach as the access-layer tool for web/platform access, transcription, formatting, and health checks | `agent-reach` CLI |
| `open-praxis-personal-monitor` | "个人监控", "personal radar", "AI/股票/媒体监控" | Runs personal monitoring for AI/news/media/investment learning signals without mixing them into Moonforge OS | Watchtower reports optional |
| `moonforge-os-monitor` | "Moonforge OS监控", "AI OS radar", "OS health" | Monitors Moonforge AI OS signals across runtime, Skill OS, Knowledge Fabric, connectors, edge strategy, and watched projects | Moonforge + watchtower optional |

### Personal Operations

| Skill | Trigger | What it does | Dependency |
|-------|---------|--------------|------------|
| `open-praxis-asset-governance` | "放哪个仓库", "配置怎么存", "asset governance" | Classifies personal AI/coding assets and recommends repo, encryption, and recovery treatment | None |
| `open-praxis-skill-design-standard` | Design, review, prune, and refactor reusable Codex/Claude skills. |
| `open-praxis-skill-forge` | "吸收skill", "skill治理", "curate skills" | Evaluates external skills, awesome lists, and agent workflows before adapting them into open-open-praxis-skills | None |
| `moonforge-review` | "周复盘", "月度架构审查", "Moonforge review" | Runs weekly/monthly Moonforge reviews across reports, fork sync, skills, configs, and inspiration repositories | Local reports optional |

## Project Structure

```
open-open-praxis-skills/
├── .claude-plugin/
│   └── marketplace.json      # Plugin manifest
├── docs/
│   ├── skill-compatibility.md # Cross-agent compatibility rules
│   └── skill-taxonomy.md      # Skill categories and classification rules
├── skills/
│   ├── open-praxis-translate/        # SKILL.md
│   ├── open-praxis-url-to-markdown/
│   ├── open-praxis-diagram/
│   ├── open-praxis-compress-image/
│   ├── open-praxis-format-markdown/
│   ├── open-praxis-youtube-transcript/
│   ├── open-praxis-markdown-to-html/
│   ├── open-praxis-infographic/
│   ├── open-praxis-slide-deck/
│   ├── open-praxis-image-gen/
│   ├── open-praxis-image-cards/
│   ├── open-praxis-cover-image/
│   ├── open-praxis-humanizer-zh/     # NEW from op7418
│   ├── open-praxis-logo-generator/   # NEW from op7418
│   ├── open-praxis-youtube-clipper/  # NEW from op7418
│   ├── open-praxis-news-aggregator/ # NEW from cclank
│   ├── open-praxis-search-hub/    # Safe search gateway and GitHub risk controls
│   ├── open-praxis-knowledge-radar/ # 知识捕获管线 + 学习编排
│   ├── open-praxis-github-watchtower/ # GitHub repo monitor operations
│   ├── open-praxis-agent-reach-ops/ # Agent-Reach access-layer operations
│   ├── open-praxis-personal-monitor/ # Personal AI/news/media/investment radar
│   ├── moonforge-os-monitor/ # Moonforge AI OS-specific radar
│   ├── open-praxis-asset-governance/ # Personal asset governance
│   ├── open-praxis-skill-forge/   # External skill intake and governance
│   └── moonforge-review/ # Weekly/monthly Moonforge reviews
├── package.json
└── .gitignore
```

## Customization

Each skill supports user preferences via `EXTEND.md` files. On first use, the skill will prompt you to configure preferences (target language, default settings, etc.) and save them to `~/.open-open-praxis-skills/<skill-name>/EXTEND.md`.

To reconfigure a skill, delete its `EXTEND.md` and the next run will re-trigger setup.

## Adding New Skills

1. Create a directory under `skills/` with your skill name
2. Add a `SKILL.md` file with frontmatter (`name`, `description`) and instructions
3. Register it in `.claude-plugin/marketplace.json` under `plugins[0].skills`

For cross-agent compatibility, do not add unsupported frontmatter keys such as `version` to `SKILL.md`. Keep `SKILL.md` Markdown-first and avoid secrets, local plaintext backups, or agent-specific assumptions unless documented with fallbacks.

## Companion Projects (standalone, not bundled)

These projects are too heavy to include as single SKILL.md files but work great alongside open-open-praxis-skills:

| Project | What it does | How to use |
|---------|-------------|------------|
| **[skill-prompt-generator](https://github.com/huangserva/skill-prompt-generator)** | AI image prompt expert system — 12 skills, 1246 visual elements, 675 community prompts. Generates pro-level prompts for Midjourney/DALL-E/Flux from Chinese descriptions. | `cd ~/skill-prompt-generator && claude` then describe what you want in Chinese |
| **[guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)** | Magazine-style & Swiss-style HTML slide decks with WebGL backgrounds, 22+ layouts. Far more advanced than open-praxis-slide-deck. | `claude plugin install op7418/guizang-ppt-skill` |
| **[dbskill](https://github.com/dontbesilent2025/dbskill)** | Business diagnosis toolkit — 18 skills from 12,307 tweets. Covers business model diagnosis, competitor benchmarking, content strategy, XHS titles, execution coaching, and interactive learning. Includes 4,176 knowledge atoms + 700 real cases. | `claude plugin marketplace add dontbesilent2025/dbskill && claude plugin install dbs@dontbesilent-skills` |
| **[md2wechat-skill](https://github.com/geekjourneyx/md2wechat-skill)** | Markdown to WeChat Official Account HTML — Go rendering engine + 15 built-in themes (apple, cyber, chinese, ocean-calm, etc.). Handles WeChat's CSS restrictions, inline styles, and image adaption. Far better than generic md→html for WeChat publishing. | `claude plugin install geekjourneyx/md2wechat-skill` |
| **[wpsnote-skills](https://github.com/wpsnote/wpsnote-skills)** | Learning + note-taking + content creation system — 35 skills in 5 plugin packs. See [usage guide](#wpsnote-skills-usage) below. | `claude plugin marketplace add wpsnote/wpsnote-skills` then install packs |
| **[summarize](https://github.com/steipete/summarize)** | CLI tool to summarize URLs, PDFs, YouTube videos, podcasts, and local files. Requires an AI API key (Anthropic/OpenAI/etc.). Flags: `--length short\|long`, `--extract` (raw transcript), `--youtube auto`. | `brew install steipete/tap/summarize` then `summarize "https://..."` |

### wpsnote-skills Usage

**Step 1: Add marketplace**

```bash
claude plugin marketplace add wpsnote/wpsnote-skills
```

**Step 2: Install the packs you need** (you don't have to install all 5)

```bash
# Core: note read/write, search, beautify, tag organize
claude plugin install base-skills@wpsnote-skills

# Content creation: writing, WeChat, XHS, short video, paper research
claude plugin install content-skills@wpsnote-skills

# Capture: audio transcript, doc/web import, calendar
claude plugin install capture-skills@wpsnote-skills

# Creative: insight engine, memory recall, novel writing
claude plugin install creative-skills@wpsnote-skills

# Learning: class notes, flashcards, lesson plans, misconception finder
claude plugin install learning-skills@wpsnote-skills
```

**Step 3: Use in Claude Code**

```
# Learning scenarios
"帮我整理这节课的笔记"          → class-note-builder
"把笔记转成闪卡"              → notes-to-flashcards
"找出我的知识盲区"             → prerequisite-gap-finder

# Content creation
"写一篇小红书笔记"             → xiaohongshu-note-creator
"帮我写短视频文案"             → short-video-copywriter
"发布到微信公众号"             → wechat-publisher

# Knowledge management
"整理我的笔记标签"             → tag-organize
"这些笔记之间有什么联系"        → ie-connect-dots
"从这篇论文中提取关键信息"      → paper-researcher
```

## Claude Code Skills 使用手册

### 什么是 Skill？

Skill 是 Claude Code 的扩展机制——一个技能目录，里面放着一套指令，以及可选的模板、示例和脚本。它遵循 [Agent Skills](https://github.com/anthropics/agent-skills) 标准，每个 Skill 至少需要一个 `SKILL.md` 文件。

**Skill vs Slash Commands**

| 对比 | Slash Commands | Skills |
|------|---------------|--------|
| 触发方式 | 手动输入 `/xxx` | Claude 根据上下文自动匹配 |
| 本质 | 固定入口 | 一组可被自动发现和加载的规则 |

### 核心特点

- **按需加载**：只加载与当前请求相关的 Skill，通过匹配 `description` 字段判断相关性，节省上下文预算
- **自动热重载**：修改 Skill 文件后立即生效，无需重启会话
- **命名空间隔离**：手动 Skill 直接用名称（`my-skill`），插件 Skill 用前缀（`document-skills:pdf`）

### Skill 存放位置

| 位置 | 路径 | 适用范围 |
|------|------|---------|
| 个人 | `~/.claude/skills/<skill-name>/SKILL.md` | 所有项目 |
| 项目 | `.claude/skills/<skill-name>/SKILL.md` | 当前项目 |
| 插件 | `~/.claude/plugins/cache/<marketplace>/<plugin>/skills/` | 所有项目（插件市场安装） |

> 每个 Skill 都要有自己的文件夹，不要把 `SKILL.md` 直接扔进 `skills/` 根目录。

### 安装 Skill

**方式 1：插件市场安装**

```bash
claude plugin install document-skills@anthropic-agent-skills
```

**方式 2：克隆整个仓库**

```bash
git clone https://github.com/user/skill-repo.git ~/.claude/skills/skill-repo
```

**方式 3：复制单个 Skill 目录**

```bash
mkdir -p ~/.claude/skills/my-skill
# 将 SKILL.md 和相关文件复制进去
```

**方式 4：npx skills（第三方工具）**

```bash
npx skills find <query>              # 搜索 Skill
npx skills add <owner/repo@skill>    # 安装 Skill
npx skills add <owner/repo@skill> -g -y  # 全局安装，跳过确认
npx skills check                     # 检查更新
npx skills update                    # 更新所有
```

浏览更多 Skill：[skills.sh](https://skills.sh/)

### 创建自定义 Skill

**1. 创建目录和文件**

```bash
mkdir -p ~/.claude/skills/my-skill
```

**2. 编写 `SKILL.md`**

```markdown
---
name: my-skill
description: 描述什么时候使用这个 Skill（包含用户可能说的关键词）
---

你的技能指令...
```

**完整目录结构**

```
my-skill/
├── SKILL.md           # 主指令文件（必需）
├── template.md        # Claude 填写的模板（可选）
├── examples/
│   └── sample.md      # 示例输出（可选）
└── scripts/
    └── validate.sh    # 辅助脚本（可选）
```

**提高触发率的技巧**

- 在 `description` 中包含用户可能说的关键词
- 描述要具体，避免过于宽泛
- 清晰说明使用场景

### 使用 Skill

**自动触发**：Claude 根据你的请求和 Skill 的 `description` 自动匹配，无需手动指定。

**手动触发**：在提示里直接点名，例如：

```
Use the PDF skill to extract the form fields from this file.
```

### 更新与卸载

**手动更新**

```bash
# 直接编辑
code ~/.claude/skills/my-skill/SKILL.md

# 从 Git 更新
cd ~/.claude/skills/skill-repo && git pull
```

**插件更新**

```bash
claude plugin update <plugin>@<marketplace>
```

**卸载**

```bash
# 手动安装的
rm -rf ~/.claude/skills/<skill-name>

# 插件安装的
claude plugin uninstall <plugin>@<marketplace>
```

### 安全使用第三方 Skill

**风险类型**

| 风险 | 说明 |
|------|------|
| 数据泄露 | 脚本读取并上传 `~/.ssh/`、API Key 等敏感信息 |
| 命令注入 | 恶意脚本执行 `rm -rf` 等破坏性命令 |
| 供应链攻击 | 流行 Skill 的维护者账号被盗，植入恶意代码 |

**安装前检查清单**

1. **验证来源**：stars > 100、有持续更新、维护者信誉良好
2. **阅读 `SKILL.md` 全文**：检查是否有可疑外部链接或敏感权限
3. **审查 `scripts/` 目录**：警惕 `curl`/`wget` 下载、`rm` 删除、访问敏感目录
4. **检查社区反馈**：搜索 GitHub Issues 中的安全相关讨论
5. **优先用官方插件**：经过审核，有版本管理和问责机制

## Credits

- Skill architecture inspired by [baoyu-skills](https://github.com/JimLiu/baoyu-skills) by Jim Liu (宝玉)
- Humanizer, Logo Generator, YouTube Clipper adapted from [op7418](https://github.com/op7418) (歸藏)
- News Aggregator adapted from [cclank/news-aggregator-skill](https://github.com/cclank/news-aggregator-skill)

## License

MIT

## Adapted Productivity And Engineering Skills

| Skill | Purpose |
|---|---|
| `open-praxis-grill-me` | Run a user-invoked plan/design pressure-test interview. |
| `open-praxis-grilling` | Reusable one-question-at-a-time plan/design interrogation loop. |
| `open-praxis-handoff` | Compact a session into a handoff for another agent or future session. |
| `open-praxis-teach` | Teach a skill or concept over multiple stateful sessions. |
| `open-praxis-debugger` | Diagnose bugs and regressions with reproduce-minimize-hypothesize-instrument-fix loop. |
| `open-praxis-codebase-design` | Design deep modules, small interfaces, clean seams, and testable architecture. |
| `open-praxis-domain-modeling` | Build glossaries, ubiquitous language, and domain ambiguity maps. |
| `open-praxis-tdd` | Run behavior-first red-green-refactor development loops. |
| `open-praxis-to-prd` | Turn a conversation or idea into a concise PRD. |
| `open-praxis-to-issues` | Break a PRD or plan into vertical executable issues. |
| `open-praxis-issue-triage` | Triage issues or backlog items into agent-ready next actions. |
| `open-praxis-prototype` | Build throwaway prototypes to answer product, UI, API, or state questions. |
| `open-praxis-code-review` | Review diffs against project standards and the originating spec. |
| `open-praxis-git-guardrails` | Design guardrails against dangerous git operations in agent workflows. |
| `open-praxis-edit-article` | Edit long-form writing for structure, clarity, and flow. |
| `open-praxis-writing-fragments` | Capture raw writing fragments before imposing structure. |
| `open-praxis-writing-shape` | Shape notes or drafts into publishable articles. |
| `open-praxis-exercise-scaffold` | Scaffold learning exercises with problems, solutions, and explainers. |
