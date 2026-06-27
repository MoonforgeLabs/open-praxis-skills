# Initial Mainline Tasks

Seed these as `inbox` or `next` items when Alex asks to initialize the radar.

| Area | Title | References |
|---|---|---|
| code-understanding | AI代码理解工作流：CodeGraph + Understand-Anything 双工具协同重塑 | CodeGraph, Understand-Anything |
| patent-skills | 专利撰写 skill 改造 | mott skills |
| rag-docs | RAG 与文档处理 skill 改造 | praxis-document-export, praxis-diagram, microsoft/markitdown, HKUDS/RAG-Anything, openPencil |
| search-skills | 搜索 skill 改造 | praxis-search-hub, addyosmani/agent-skills |
| skill-creation | 创建 skill 工作流改造 ✅ | praxis-skill-forge, mott skills, anthropics/skills |

### skill-creation 任务详情

**状态：** ✅ learned（核心能力已落地）

**已完成：**
- ✅ 10 个来源深度内化：mattpocock/skills, anthropics/skills, obra/superpowers, affaan-m/ECC, gsd-build/get-shit-done, ComposioHQ/awesome-claude-skills, hesreallyhim/awesome-claude-code, msitarzewski/agency-agents, mvanhorn/last30days-skill, anysearch-skill
- ✅ 39 个 reference 文件：skill architecture, description format, verification patterns, hook patterns, eval methodology, role templates, research patterns, runtime config, knowledge architecture, workspace audit, package management, design gate, skill writing TDD, persuasion principles, git workflow, naming validation, marketplace registration, eval advanced, sprawl detection, load theory 等
- ✅ 9 个工具脚本：quick_validate.py, eval_runner.py, improve_description.py, package_skill.py, link-skills.sh, doctor.sh, bump-version.sh, auto_classify_tiers.py, install_skill.sh
- ✅ 三版本命名体系：alex- (个人), alex-org- (内部 GitLab), alex-pub- (公开 GitHub)
- ✅ 改名：alex-skill-curator → praxis-skill-forge

**待增强（非阻塞）：**
- ⬜ CI/CD 集成（GitHub Actions 跑 quick_validate + eval_runner）
- ⬜ Shell lint（ShellCheck 检查 scripts/*.sh）
- ⬜ Dashboard（skill 健康仪表盘，可选）

**能力同步：**
```bash
python3 scripts/radar_enhanced.py sync skill-creation
```
| daily-news | 每日新闻与监控 skill 改造 | praxis-github-watchtower, praxis-agent-reach-ops, praxis-news-aggregator, praxis-youtube-clipper, moonforge-intake |
| ai-os | 个人 AI OS 改造 | moonforge, deerflow, tauri, OpenHarness, fay, openapi, IBM cuga, Omnigent, everOs, ollama/ollama |
| knowledge-base | 个人知识库改造 | awesome-architecture |
| skill-ecosystem | 有用 skill 生态整合 | addyosmani/agent-skills, mott skills, superpowers, ECC |
| business-skills | business skill 改造 | 短视频, 小红书, bytedance/UI-TARS-desktop, Open-Generative-AI, Pixelle, FinceptTerminal, calesthio/OpenMontage |
| stocks | 股票类型处理 | TradingAgents |
| design-tools | AI 设计工具生态整合 | claude-design, UI-TARS-desktop, Codex-Product-Design |
| digital-human | 数字人与虚拟形象 | Fay, OpenTalking |
| content-distribution | 多平台内容分发工作流 | ai-marketing-agent |
