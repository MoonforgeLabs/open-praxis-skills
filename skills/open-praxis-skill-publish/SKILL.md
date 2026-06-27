---
name: open-praxis-skill-publish
description: >
  Prepare a skill for three-channel distribution — personal (praxis-),
  internal GitLab (praxis-org-), and public GitHub (praxis-pub-). Audit
  dependencies, rename, generate install docs, and verify standalone
  usability. Use when the user wants to publish a skill externally.
---

# Alex Open Source Prep

End-to-end workflow for making a skill distributable across three channels.

## Three-Channel Naming

> **详细配置**: 查看 [CHANNELS.md](CHANNELS.md) 获取完整的仓库地址和发布流程

| Channel | Prefix | Example | Destination | Repo Name | Remote URL |
|---------|--------|---------|-------------|-----------|------------|
| Personal | `praxis-` | `praxis-translate` | `skills/praxis-skills/` | — | `git@github.com:MoonforgeLabs/praxis-skills.git` |
| Internal (GitLab) | `org-praxis-` | `org-praxis-translate` | `myCode/org/org-praxis-skills/` | `org-praxis-skills` | `git@git.n.xiaomi.com:ai-labs/org-praxis-skills.git` |
| Open Source (GitHub) | `open-praxis-` | `open-praxis-translate` | `myCode/open/open-praxis-skills/` | `open-praxis-skills` | `git@github.com:MoonforgeLabs/open-praxis-skills.git` |

All three versions can coexist on the same machine (`~/.claude/skills/`).

## When to Use

- Publishing a skill to internal GitLab (`org/skills/`)
- Publishing a skill to public GitHub (`public/skills/`)
- Making a skill self-contained so it works outside the praxis-skills collection
- Reviewing which skills are ready to ship vs. which need surgery

## Prerequisites

Before starting, know:
- **Target channel**: `org` (internal GitLab) OR `public` (GitHub) OR both
- **Target skill**: the specific skill folder to prepare (e.g., `praxis-translate`)

## Workflow

### Phase 0: Scrub — 擦除创作过程资产

**核心原则**：发布出去的 skill 是**黑盒**。用户只需要知道"怎么用"，不需要知道"怎么造的"。以下内容属于你的核心竞争力，必须在发布前彻底清除。

**0.1 移除创作元工具引用**

搜索并删除所有对以下内部工具的引用：

| 内部工具 | 暴露了什么 | 处理方式 |
|----------|-----------|---------|
| `praxis-skill-forge` | skill 的创建/治理方法论 | 删除所有引用，包括 SKILL.md、scripts、references 中的提及 |
| `intake-rubric.md` | 需求评估标准 | 删除引用和内联的评分逻辑 |
| `capability-tiers` | 能力分层演进策略 | 删除 CORE/ENHANCED/ADVANCED 分层说明，除非用户需要了解降级路径 |
| `praxis-knowledge-radar` | 知识管理和学习编排方法论 | 删除引用 |
| `praxis-skill-publish` | 发布流程本身 | 删除引用 |
| `auto_classify_tiers.py` | 自动分层脚本 | 删除引用和脚本文件 |
| `source-notes.md` | 创作来源记录 | 删除整个文件和引用 |
| `dependency-lifecycle.md` | 依赖生命周期管理 | 删除引用（保留对用户有用的安装说明） |
| `skill-architecture.md` | skill 架构设计方法论 | 删除引用 |

搜索方式：
```bash
# 搜索 SKILL.md 和 references/ 中的所有创作元工具引用
grep -rn "praxis-skill-forge\|intake-rubric\|capability-tier\|praxis-knowledge-radar\|praxis-learning-radar\|praxis-skill-publish\|auto_classify\|source-notes\|dependency-lifecycle\|skill-architecture" SKILL.md references/
```

**0.2 移除创作过程痕迹**

| 痕迹类型 | 示例 | 处理方式 |
|----------|------|---------|
| 创作简报引用 | "See creative brief in ..." | 删除整个段落 |
| 审核记录 | "Reviewed by curator on ..." | 删除 |
| 设计决策注释 | "We chose X over Y because ..." | 删除，只保留最终方案 |
| 迭代历史 | "Previously this was called ..." | 删除 |
| 内部工作流 | "Run curator intake first ..." | 删除 |
| 能力演进说明 | "CORE tier uses stdlib, ENHANCED adds ..." | 除非用户需要了解降级行为，否则删除 |

**0.3 移除内部脚本和配置**

检查 `scripts/` 目录，删除：
- 仅服务于创作流程的脚本（如 `auto_classify_tiers.py`、`install_skill.sh`）
- 内部验证脚本（如 `quick_validate.py`、`vendor_sync.py`）
- 内部配置文件（如 `vendor-manifest.yaml`、`deps-manifest.json`）

保留：
- 用户运行时需要的脚本（如数据处理、格式转换）
- 安装/部署脚本（如 `install.sh`）

**0.4 清理 references/ 目录**

| 文件 | 处理 |
|------|------|
| `intake-rubric.md` | 删除 |
| `source-notes.md` | 删除 |
| `dependency-lifecycle.md` | 删除，提取有用的安装说明到 SKILL.md |
| `capability-tiers.md` | 删除，除非 skill 有降级路径需要说明 |
| `skill-architecture.md` | 删除 |
| `skill-file-checklist.md` | 删除（这是 curator 的检查清单） |
| `cross-platform-guide.md` | 保留（对用户有用） |
| `templates.md` | 保留（对用户有用） |

**0.5 验证清除完整性**

```bash
# 最终检查：确保没有创作痕迹残留
grep -rn "curator\|intake\|capability-tier\|knowledge-radar\|learning-radar\|skill-architecture\|source-notes\|auto_classify\|skill creation\|skill development\|creative brief" SKILL.md references/ scripts/
```

输出应该为空。如果有残留，逐一清理。

**0.6 输出：Scrub 报告**

```
## Scrub Report: praxis-xxx

### Removed References
- [x] praxis-skill-forge (N mentions)
- [x] intake-rubric.md (N mentions)
- [x] capability-tiers (N mentions)
- ...

### Removed Files
- [x] references/intake-rubric.md
- [x] scripts/auto_classify_tiers.py
- ...

### Removed Sections
- [x] "Capability Tier System" section in SKILL.md
- [x] "Curator Governance" section in SKILL.md
- ...

### Verified Clean
- [x] grep returns zero matches for blocked terms
```

---

### Phase 1: Audit

Scan the target skill and produce a dependency report.

**1.1 External tool dependencies**

Search SKILL.md and references/ for:
- CLI tools: `brew install`, `which`, `command -v`, direct binary invocations
- Python packages: `pip install`, `import` statements in scripts/
- Node packages: `npm install`, `require()`
- System tools: `sips`, `open`, `pbcopy`, macOS-only commands

For each, record:

| Field | Example |
|-------|---------|
| Name | `yt-dlp` |
| Type | cli / pip / npm / system |
| Install cmd | `brew install yt-dlp` |
| Used in | SKILL.md step 3, scripts/fetch.py |
| Required vs optional | required — skill cannot function without it |
| Platform | macOS only / cross-platform / Linux only |

**1.2 Cross-skill dependencies**

Search SKILL.md for:
- `/praxis-*` slash-command references
- File path references to `../praxis-*/` or absolute paths into other skill folders
- Prose mentions of other skills by name

For each, record:

| Field | Example |
|-------|---------|
| Name | `praxis-youtube-transcript` |
| How referenced | `/praxis-youtube-transcript` slash command |
| Used for | Fetching video transcripts |
| Required vs optional | optional — user can provide .srt manually |
| Inline-able? | yes — core logic is 5 lines of yt-dlp commands |

**1.3 Private/local dependencies**

Search for:
- Absolute paths to user home (`~/.`, `/Users/alex/`)
- References to private repos (`praxis-local-configs`, `praxis-learning`)
- Environment variables (`$PRAXIS_SKILLS_DIR`, `$WATCHTOWER_*`)
- Claude-specific paths (`~/.claude/`, `.claude-plugin/`)

For each, record whether it can be:
- **Templated**: replace with env var or placeholder
- **Removed**: the reference is not needed for standalone use
- **Documented**: add to "Private setup" section

**1.4 Output: dependency report**

Print a structured report:

```
## Dependency Report: praxis-xxx

### External Tools (X total)
| Name | Type | Required | Install | Platform |
|------|------|----------|---------|----------|

### Cross-Skill (X total)
| Name | Required | Inline-able | Fallback |
|------|----------|-------------|----------|

### Private/Local (X total)
| Reference | Action | Notes |
|-----------|--------|-------|

### Verdict
- [ ] Zero external deps → ready to ship
- [ ] External deps only → add prerequisites section
- [ ] Cross-skill deps → need fallback or inlining
- [ ] Private deps → need templating or removal
```

### Phase 2: Classify

Based on the audit, assign the skill to a readiness tier:

| Tier | Criteria | Action needed |
|------|----------|---------------|
| A — Ship now | Zero deps, or only system-builtins | Just add README |
| B — Add prerequisites | Has CLI/pip deps, no cross-skill | Add Prerequisites section + frontmatter metadata |
| C — Surgery needed | Has cross-skill or private deps | Inline, add fallbacks, or mark private-only |
| D — Not suitable | Deeply entangled with private infra | Do not open-source |

If the skill is Tier C, decide per dependency:

| Dependency complexity | Decision |
|----------------------|----------|
| Cross-skill logic ≤ 10 lines | **Inline** — copy the essential commands into this skill |
| Cross-skill logic > 10 lines, optional | **Fallback** — declare optional, document manual alternative |
| Cross-skill logic > 10 lines, required | **Bundle** — ship both skills together, or do not separate |
| Private repo reference | **Template** — replace with `<YOUR_CONFIG_PATH>` placeholder |

### Phase 3: Transform

Apply changes to the skill files.

**3.0 Read capability tiers (if present)**

Many skills have a `CAPABILITY_TIERS` dict in their main script, or a `deps-manifest.json` file. These define which commands/features belong to which tier:

| Tier | Meaning | Open-source action |
|------|---------|-------------------|
| `CORE` | Python stdlib only, zero deps | Keep as-is |
| `ENHANCED` | Optional CLI tools | Keep, add graceful degradation |
| `ADVANCED` | External skills or auth | Remove or stub |

To read:
```bash
# From a Python script with CAPABILITY_TIERS
python3 scripts/<skill>.py tiers

# From deps-manifest.json
cat deps-manifest.json | python3 -m json.tool
```

If the skill has tiers, use them to guide the transformation:
- `CORE` tier → already Tier A (ship now)
- `ENHANCED` tier → Tier B (add prerequisites, document degradation)
- `ADVANCED` tier → Tier C or D (inline, fallback, or remove)

This replaces manual dependency classification for skills that have pre-marked tiers.

**3.1 Add dependency metadata to frontmatter**

```yaml
metadata:
  distribution:
    channel: github | internal
    standalone: true | false
  dependencies:
    cli:
      - name: yt-dlp
        install: "brew install yt-dlp"
        required: true
    python:
      - name: pysrt
        install: "pip install pysrt"
        required: false
        fallback: "字幕处理降级为手动编辑"
    skills:
      - name: open-praxis-youtube-transcript
        required: false
        fallback: "手动提供 .srt 字幕文件"
```

Rules:
- `required: true` = skill cannot complete its core workflow without it
- `required: false` = skill works with degraded experience
- Every `required: false` must have a `fallback` explaining the degraded path
- List required deps before optional deps

**3.2 Add Prerequisites section to SKILL.md**

Insert after the frontmatter and title, before the first workflow section:

```markdown
## Prerequisites

Required:
\`\`\`bash
brew install yt-dlp
\`\`\`

Optional (enhances functionality):
\`\`\`bash
pip install pysrt
\`\`\`

If optional tools are missing, the skill will note degraded behavior and continue.
```

Rules:
- Required tools first, optional second
- Include the exact install command, not just the tool name
- Note platform-specific caveats (e.g., "macOS only", "ffmpeg-full vs ffmpeg")
- If zero deps, write "No external dependencies."

**3.3 Inline cross-skill logic (when ≤ 10 lines)**

If a cross-skill dependency provides simple, self-contained logic:
- Copy the essential commands/instructions into this skill's workflow steps
- Add a comment: `<!-- Inlined from praxis-xxx for standalone use -->`
- Remove the `/skill-name` reference

**3.4 Add fallback paths (when not inlining)**

For each optional cross-skill dependency, add a fallback block in the relevant workflow step:

```markdown
#### If praxis-youtube-transcript is installed:
Run `/praxis-youtube-transcript <url>` to auto-fetch the transcript.

#### If not installed:
1. Install yt-dlp: `brew install yt-dlp`
2. Run: `yt-dlp --write-auto-sub --sub-lang en --skip-download <url>`
3. Use the generated .vtt file directly
```

**3.5 Template private references**

Replace hardcoded private paths:

| Before | After |
|--------|-------|
| `<WORKSPACE>/praxis-local-configs/...` | `<YOUR_WORKSPACE>/docs/moonforge-public-private-boundary.md` |
| `$PRAXIS_SKILLS_DIR` | `<SKILLS_REPO_DIR>` |
| `~/.claude/skills/` | `<AGENT_SKILLS_DIR>` |

Add a note: "Replace `<PLACEHOLDER>` with your actual path."

**3.6 Remove internal-only content**

Strip from the public version:
- References to `praxis-local-configs` (private config repo)
- References to `quick_validate.py` (internal validation script)
- References to `vendor-manifest.yaml` (internal backup system)
- Internal-only post-change prompts (push to remote, sync to Codex, etc.)
- Hardcoded personal paths that cannot be templated

**3.7 Rename for target channel**

When copying to `org/skills/` or `public/skills/`, rename the skill:

| Source | Target | Rename |
|--------|--------|--------|
| `skills/praxis-skills/praxis-translate/` | `org/skills/praxis-org-translate/` | `praxis-` → `praxis-org-` |
| `skills/praxis-skills/praxis-translate/` | `public/skills/praxis-pub-translate/` | `praxis-` → `praxis-pub-` |

Rename checklist:
- [ ] Directory name: `praxis-xxx/` → `praxis-org-xxx/` or `praxis-pub-xxx/`
- [ ] SKILL.md frontmatter `name:` field
- [ ] SKILL.md body: all `/praxis-xxx` references → `/praxis-org-xxx` or `/praxis-pub-xxx`
- [ ] SKILL.md body: update cross-skill references to match target channel prefix
- [ ] scripts/: update any hardcoded skill name references
- [ ] hooks/hooks.json: update paths if present
- [ ] install.sh: update skill name if present

Cross-skill reference rules in the target version:
- Internal (`praxis-org-`): can reference other `praxis-org-*` skills
- Public (`praxis-pub-`): must include fallback for any `praxis-pub-*` reference not in the distribution

### Phase 4: Generate

Create distribution artifacts. See `references/templates.md` for full templates.

**4.1 Generate skill-level README.md**

Use the README template from `references/templates.md`. Replace `{SKILL_NAME}` with the target channel name (e.g., `praxis-org-translate`).

**4.2 Generate repo INSTALL.md**

Generate if publishing 2+ skills. Use the INSTALL.md template from `references/templates.md`.

**4.3 Create delta-tracker.yaml**

Create or update `skills/praxis-skills/dist/delta-tracker.yaml` with the entry for this skill. Use the template from `references/templates.md`.

**4.4 Validate plugin.json / marketplace.json**

If publishing to a marketplace:
- Ensure the skill is registered in `.claude-plugin/plugin.json` or equivalent
- Description in plugin matches frontmatter description
- No references to non-existent skills

### Phase 5: Verify

Run these checks before marking the skill as ready:

**5.1 Standalone test**

Simulate a fresh user:
- [ ] Read only SKILL.md — can you understand what the skill does?
- [ ] Follow Prerequisites — do the install commands work?
- [ ] Run the core workflow without any other praxis-* skills installed — does it complete?
- [ ] If optional deps are missing — does the fallback path work?

**5.2 Naming consistency**

- [ ] Directory name matches frontmatter `name:` field
- [ ] Prefix matches target channel (`praxis-org-` for org, `praxis-pub-` for public)
- [ ] No leftover `praxis-` prefix (personal) in the target version
- [ ] Cross-skill references use the correct channel prefix

**5.3 No dangling references**

- [ ] No `/praxis-*` references to skills not included in the distribution
- [ ] No absolute paths to `/Users/alex/` or private repos
- [ ] No references to internal scripts (`quick_validate.py`, `vendor_sync.py`)
- [ ] No `PRAXIS_SKILLS_DIR` or other private env vars without a placeholder

**5.3 Description quality**

- [ ] Description works for the target channel:
  - **GitHub**: trigger-oriented, mentions what + when
  - **Internal**: can reference other praxis-* skills by name
- [ ] Description ≤ 1,536 chars
- [ ] Leading word is a verb

**5.4 Cross-channel compatibility**

If publishing to both channels, generate two versions of:
- Description (GitHub: standalone triggers; Internal: can reference siblings)
- Prerequisites section (GitHub: exhaustive; Internal: assume family installed)
- Fallback paths (GitHub: full fallback; Internal: "use /sibling-skill")

Store internal-only extras in a separate branch or overlay file.

**5.5 No creative process artifacts (核心竞争力保护)**

Run the blocked-term scan. ALL must return zero matches:

```bash
grep -rn "curator\|intake-rubric\|capability-tier\|knowledge-radar\|learning-radar\|skill-architecture\|source-notes\|auto_classify\|skill creation\|skill development\|creative brief\|praxis-skill-forge\|dependency-lifecycle\|skill-file-checklist" \
  SKILL.md references/ scripts/
```

- [ ] Zero matches — no creative process artifacts leaked
- [ ] No references to `praxis-skill-forge` or any curator workflow
- [ ] No `capability-tier` system exposed (CORE/ENHANCED/ADVANCED)
- [ ] No intake rubric or evaluation criteria exposed
- [ ] No task radar or learning radar references
- [ ] No design philosophy or architecture methodology exposed
- [ ] No scripts that only serve the creation process (auto_classify_tiers.py etc.)

**5.6 Local installation (三平台验证)**

发布前必须同步到所有本地 agent（统一使用软连接）：

```bash
# 安装到三个 agent（软连接）
for dir in ~/.claude/skills ~/.codex/skills ~/.openhuman/skills; do
  target="$dir/<skill-name>"
  if [ -L "$target" ]; then
    echo "已有"
  elif [ -d "$target" ]; then
    rm -rf "$target" && ln -s /Users/alex/Documents/myCode/skills/praxis-skills/skills/<skill-name> "$target"
  else
    ln -s /Users/alex/Documents/myCode/skills/praxis-skills/skills/<skill-name> "$target"
  fi
done
```

验证：
- [ ] `~/.claude/skills/<skill-name>` 是软连接且指向正确
- [ ] `~/.codex/skills/<skill-name>` 是软连接且指向正确
- [ ] `~/.openhuman/skills/<skill-name>` 是软连接且指向正确

**Principle**: Published skill = black box. Users know *what* it does and *how* to use it. They never see *how you built it*.

## Output Shape

After completing all phases, report:

```
## Open-Source Prep: praxis-xxx

### Tier: [A/B/C/D]

### Scrub Report (Phase 0)
- [x] Removed N references to praxis-skill-forge
- [x] Removed N references to capability-tiers
- [x] Removed N references to intake-rubric
- [x] Deleted files: references/intake-rubric.md, scripts/auto_classify_tiers.py, ...
- [x] Blocked-term scan: zero matches

### Changes Made
- [x] Added frontmatter metadata.dependencies
- [x] Added Prerequisites section
- [x] Inlined logic from praxis-yyy (5 lines)
- [x] Added fallback for praxis-zzz
- [x] Templated private path: /Users/alex/... → <WORKSPACE>
- [x] Generated README.md

### Verification
- [x] Standalone test passed
- [x] No dangling references
- [x] Description valid

### Ready to ship: YES / NO
### Remaining blockers: (list if NO)
```

### Phase 6: Version Sync

After initial publish, handle ongoing updates across all 3 channels.

**Problem**: You update a skill in `praxis-skills`. The org and public versions are now stale.

**Strategy**:

1. **Trivial fixes** (typo, comment): copy to org/public, re-rename, push.
2. **Behavior changes** (new step, changed workflow): re-run Phase 5 verification before pushing to each channel.
3. **Dependency changes** (new dep, removed dep): update README + frontmatter in all channels, re-verify install commands.
4. **Cross-skill reference changes**: if you added a new `/praxis-xxx` reference, the org version needs `/praxis-org-xxx`, the public version needs a fallback.

**delta-tracker.yaml**: maintained in `skills/praxis-skills/dist/`, records:
- Source hash (personal version)
- Last sync date per channel
- Divergence notes (what was trimmed and why)
- Status per channel: `exact_copy` / `adapted` / `excluded`

**Automation**: consider a CI check that:
- Validates frontmatter schema
- Checks for dangling `/praxis-*` references not in the distribution
- Verifies install commands are syntactically correct
- Checks naming prefix matches target channel

### Three-Channel Version Sync

When the same skill exists in all 3 channels, changes flow:

```
praxis-skills (personal)  →  org/skills (internal)  →  public/skills (public)
     源头                    裁剪 + 改名              裁剪 + 改名
```

**Sync strategy**:

1. Always edit the personal version first (`skills/praxis-skills/praxis-xxx/`)
2. Run `sync-check.sh` to detect which org/public versions are stale
3. For each stale version:
   - If the change doesn't affect trimmed content → copy + re-rename
   - If the change touches trimmed content → manually merge the non-trimmed parts
4. Update `delta-tracker.yaml` with new source hash

**When versions diverge significantly**:

If org and public versions need different content (different install targets, different features):

- Maintain separate copies in `org/skills/` and `public/skills/`
- Document the divergence in `delta-tracker.yaml`
- Accept that they are independent — sync only non-conflicting changes

**When to skip a channel**:

| Scenario | Action |
|----------|--------|
| Skill depends on private infra | Skip `public`, keep `org` |
| Skill has no external users | Skip both `org` and `public` |
| Skill is a meta-tool (curator, prep, publish) | Skip both — these expose creation methodology |
| Skill exposes capability-tiers/intake/radar systems | Skip both — these are core competitive advantages |

### Batch Quick Scan

To audit all 48 skills at once without running the full workflow, scan for readiness:

Search every `skills/*/SKILL.md` for:
1. `/praxis-*` cross-skill references (count per skill)
2. `brew install`, `pip install`, `which`, `command -v` (external deps)
3. `/Users/alex/`, `~/.claude/`, `$PRAXIS_SKILLS_DIR` (private paths)
4. `curator\|intake-rubric\|capability-tier\|knowledge-radar\|learning-radar\|skill-architecture` (creative process artifacts)

Output a readiness matrix:

```
| Skill | Tier | Cross-skill refs | CLI deps | Private paths | Creative artifacts | Ready? |
|-------|------|-----------------|----------|---------------|-------------------|--------|
| praxis-translate | A | 0 | 0 | 0 | 0 | ✅ |
| praxis-youtube-clipper | B | 2 | 3 | 0 | 0 | ⚠️ needs fallbacks |
| praxis-skill-forge | D | 0 | 0 | 0 | 12 | ❌ exposes methodology |
```

Use this to decide which skills to prepare first (start with Tier A, then B).

## Gotchas

- **创作过程资产 = 核心竞争力**：`praxis-skill-forge`、`capability-tiers`、`intake-rubric`、`knowledge-radar` 等内部工具和方法论**绝不能出现在发布版本中**。这些是你造 skill 的能力，不是 skill 本身的能力。发布版是黑盒——用户能用，但看不到里面的工程方法论。
- **Three channels, three names**: `praxis-xxx` (personal), `praxis-org-xxx` (internal), `praxis-pub-xxx` (public). Never publish a personal-prefixed skill to org/public.
- **Cross-skill references must match channel**: If org version references `praxis-org-translate`, don't leave `praxis-translate` in the body.
- **ffmpeg vs ffmpeg-full**: Standard Homebrew ffmpeg does not include libass. If the skill burns subtitles, it needs `ffmpeg-full`. Document this explicitly.
- **macOS-only tools**: `sips`, `pbcopy`, `open` are macOS-only. If the skill uses them, note platform requirement.
- **Cross-skill ≠ cross-file**: mattpocock/skills uses `/skill-name` prose references, not file links. Follow this pattern — it survives reorganization.
- **Don't over-inline**: If inlining > 10 lines from another skill, consider shipping both together instead. Duplicated logic drifts.
- **Three versions on one machine**: All 3 prefixes can coexist in `~/.claude/skills/`. Use this for testing before publishing.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Listing deps but not providing install commands | Always include the exact `brew install` / `pip install` command |
| Marking everything as `required: true` | Ask: "Does the skill work at all without this?" If yes, mark optional with fallback |
| Copying private paths into public README | Use `<PLACEHOLDER>` and add a note to replace |
| Assuming ffmpeg = ffmpeg-full | Document the exact variant needed |
| Shipping without testing standalone | Simulate a fresh user who has no other praxis-* skills |
| Forgetting to rename when copying to org/public | Always change prefix: `praxis-` → `praxis-org-` or `praxis-pub-` |
| Leaving personal cross-skill refs in org/public version | Search and replace all `/praxis-xxx` to match target channel |
| 发布版中残留创作过程资产（curator、capability-tiers、intake-rubric 等） | 运行 Phase 0 Scrub，grep 检查所有 blocked terms 必须零匹配 |

## Release Workflow

### 发布新 skill 到下游仓库的完整流程

> **详细配置**: 查看 [CHANNELS.md](CHANNELS.md) 获取完整的仓库地址和发布流程

```
1. 在 praxis-skills 中开发和测试
2. 用 praxis-skill-publish 评估（Phase 0 Scrub + Phase 1-5）
   - Phase 0 Scrub 必须先通过（blocked-term scan 零匹配）
   - 然后才进入 Phase 1-5 的依赖审计和验证
3. 在 release-manifest.json 的 approved 中注册
4. bash scripts/sync-repos.sh
5. 自动只同步 approved 的 skill 到 org-praxis-skills 和 open-praxis-skills
6. 分别推送到各渠道仓库
```

### 仓库地址

| 渠道 | 仓库 | 推送命令 |
|------|------|---------|
| **Personal** | `MoonforgeLabs/praxis-skills` | `git push origin main` |
| **Internal** | `ai-labs/org-praxis-skills` | `git push gitlab main` |
| **Open Source** | `MoonforgeLabs/open-praxis-skills` | `git push origin main` |

### release-manifest.json 结构

```json
{
  "approved": {
    "praxis-ai-usage-stats": {
      "approved_by": "praxis-skill-publish",
      "date": "2026-06-26",
      "tier": "A",
      "notes": "100% CORE, zero external deps"
    }
  },
  "pending": ["praxis-search-hub", "praxis-translate"],
  "private_only": ["praxis-agent-reach-ops", "moonforge-*"]
}
```

- `approved`: 已评估通过，会被 sync-repos.sh 同步到下游
- `pending`: 待评估，不同步
- `private_only`: 不适合开源，永远不同步

### 同步命令

```bash
bash scripts/sync-repos.sh              # 只同步 approved 的 skill
bash scripts/sync-repos.sh --check      # 只检查，不执行
bash scripts/sync-repos.sh --org        # 只同步到 org-praxis-skills
bash scripts/sync-repos.sh --open       # 只同步到 open-praxis-skills
bash scripts/sync-repos.sh --all        # 强制同步全部（危险，跳过 manifest）
```

### 注意事项

- **禁止全量同步**：sync-repos.sh 默认只读 release-manifest.json，不会把 praxis-skills 的全部 skill 同步过去
- **评估优先**：每个 skill 必须经过 praxis-skill-publish 评估后才能加入 approved
- **命名规范**：下游仓库的 skill 名称需要加渠道前缀（praxis-org- / praxis-pub-）
- **commit message**：禁止添加 AI agent 的 Co-Authored-By 标记（全局 git hook 已配置）
| Publishing to org/public with personal-prefixed name | The `name:` field must match the directory name and channel prefix |
