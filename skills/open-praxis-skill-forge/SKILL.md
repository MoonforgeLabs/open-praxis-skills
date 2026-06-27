---
name: open-praxis-skill-forge
description: >
  Create, curate, evaluate, adapt, deduplicate, merge, split, and maintain agent skills.
  Use when the user asks to create a new skill, import or improve existing skills, review
  skill candidates, decide whether skills should merge or split, absorb writing-great-skills
  principles, track upstream reference sources, mine mattpocock/skills, awesome-claude-skills,
  awesome-claude-code, agency-agents, ECC, last30days-skill, anysearch-skill, or create a
  skill governance/backlog/update plan. Also triggers on: 创建技能, 创建 skill, 导入 skill,
  评估 skill, 合并 skill, 拆分 skill, 改进 skill, skill 命名, skill 发布, skill 依赖,
  skill 版本, skill 验证, skill 文档, skill 测试, skill 兼容性.
---

# Alex Skill Forge

Meta-skill for creating, governing, evaluating, and maintaining agent skills.

## When to Use

- Creating a new skill from scratch
- Importing or adapting an external skill
- Evaluating skill quality and readiness
- Deciding whether to merge or split skills
- Improving skill descriptions and documentation
- Checking skill dependencies and compatibility
- Preparing skills for publishing
- Running consistency and compliance checks

## Areas

- `skill-forge`: Meta-skill for creating, governing, evaluating, and maintaining agent skills
- `skill-creation`: Skill creation, curation, and official-skill alignment
- `skill-ecosystem`: Useful external skill ecosystems
- `skill-publishing`: Skill publishing and distribution

## Quick Reference

| Command | Description |
|---------|-------------|
| `python3 scripts/quick_validate.py <skill>` | Validate SKILL.md format |
| `python3 scripts/eval_runner.py <skill>` | Evaluate trigger accuracy |
| `python3 scripts/check_consistency.py <skill>` | Check SKILL.md vs actual functionality |
| `python3 scripts/check_open_source_readiness.py <skill>` | Check publishing readiness |
| `python3 scripts/improve_description.py <skill>` | Improve skill description |
| `python3 scripts/package_skill.py <skill>` | Package skill for distribution |
| `python3 scripts/auto_classify_tiers.py <skill>` | Classify capability tiers |
| `python3 scripts/install_skill.sh <skill>` | Install skill locally |
| `python3 scripts/link-skills.sh` | Link skills to Claude |
| `python3 scripts/doctor.sh` | Check skill health |
| `python3 scripts/bump-version.sh <skill>` | Bump skill version |

## Scripts

| Script | Tier | Description |
|--------|------|-------------|
| `quick_validate.py` | CORE | Validate SKILL.md format and structure |
| `eval_runner.py` | CORE | Evaluate trigger phrase accuracy |
| `check_consistency.py` | CORE | Check SKILL.md matches actual functionality |
| `check_open_source_readiness.py` | CORE | Check skill is ready for publishing |
| `improve_description.py` | ENHANCED | Improve skill description using AI |
| `package_skill.py` | ENHANCED | Package skill for distribution |
| `auto_classify_tiers.py` | ENHANCED | Auto-classify capability tiers |
| `install_skill.sh` | ENHANCED | Install skill locally |
| `link-skills.sh` | ENHANCED | Link skills to Claude |
| `scripts/doctor.sh` | ENHANCED | Check skill health and dependencies |
| `scripts/bump-version.sh` | ENHANCED | Bump skill version |
| `scripts/link-skills.sh` | ENHANCED | Link skills to Claude |

## Public / Private Boundary

Use `<WORKSPACE>/praxis-local-configs/docs/moonforge-public-private-boundary.md` before absorbing any external or internal Skill idea. Classify each candidate as `public-core`, `public-extension`, `private-config`, `private-knowledge`, or `sensitive-secret`.

Default rule: reusable workflow patterns may become public extensions; Alex-specific paths, account state, private sources, generated reports, and secrets must be templated, moved private, or excluded.

## Default Paths

- Skill repo: `PRAXIS_SKILLS_DIR` or `/Users/alex/Documents/myCode/skills/praxis-skills`
- Skill folders: `skills/<skill-name>/`
- Required docs: `README.md`, `docs/skill-taxonomy.md`, `.claude-plugin/marketplace.json`
- Vendor backup: `skills/<skill-name>/references/vendor/` with `vendor-manifest.yaml`

Never copy secrets, local credentials, private logs, or vendor-specific tokens into `praxis-skills`.

## Skill Quality Lens

Apply `references/writing-great-skills.md` before creating, merging, splitting, or expanding a skill. Treat predictability as the root goal: the same task should follow the same process across runs.

Use this default decision order:

1. Prune no-op or duplicated text until every line changes behavior (see `references/no-op-detection.md`).
2. Merge overlapping skills when one router or leading word reduces cognitive load.
3. Split only when a branch has a distinct leading word or later steps cause premature completion.
4. Push branch-specific details into references; keep `SKILL.md` as steps plus essential rules.
5. Make each step end with a checkable completion criterion.
6. Validate token budget: SKILL.md < 500 lines / < 5,000 tokens, description < 1,536 chars (see `references/token-budget.md`).
7. Write description using SDO format: "Use when [trigger]" not "This skill does..." (see `references/description-format.md`).
8. Run final checklist from `references/effective-skills-checklist.md`.

## Intake Workflow

1. Identify the source repository, upstream URL, license context, version or commit, and the concrete user job it improves.
2. Classify the candidate with `references/intake-rubric.md`.
3. Assess source credibility: official team > community curated > individual > AI-generated.
4. Search existing `praxis-skills` names, descriptions, and source notes for overlap.
5. Decide `merge`, `update`, `new skill`, `reference only`, or `skip`; prefer merge/update when the user would not remember another invocation.
6. Decide invocation model: `user-invoked` (explicit `/skill-name`) vs `model-invoked` (auto-triggered by description match). Default to user-invoked for workflows with side effects.
7. If praxis-skills exceeds 30 skills, consider namespace routing (group into `<namespace>-<skill>` with router skills) to reduce token overhead.
8. Prefer adapting the workflow into Alex's style over copying entire external prompts.
9. If any source inspired the result, add or update source notes using `references/source-tracking.md`.
10. For every external dependency, create or update `references/vendor-manifest.yaml` and back up to `references/vendor/` (see `references/vendor-manifest.md`).
11. **Mark capability tiers** for each command/feature using the CORE/ENHANCED/ADVANCED convention (see `references/capability-tiers.md`):
    - `CORE`: Python stdlib only, zero external deps
    - `ENHANCED`: optional CLI tools, graceful degradation when missing
    - `ADVANCED`: external skills, authenticated APIs, or heavy dependencies
    - Store tiers in `CAPABILITY_TIERS` dict in the main script, or in `deps-manifest.json`
    - This enables `praxis-skill-publish` to auto-trim for open-source release
12. **Declare dependency lifecycle** for every external dependency (see `references/dependency-lifecycle.md`):
    - Each dependency must have: `install`, `check`, `update`, `check-latest` commands
    - Skill files managed by skills.sh, CLI tools by package manager (npm/pipx/brew)
    - If a dependency has both CLI and skill file, declare BOTH separately
    - For skills with >3 dependencies, create `update-deps.sh` following praxis-search-hub pattern
    - Add lifecycle info to `deps-manifest.json` under `dependencies` section
13. **Verify file checklist** (see `references/skill-file-checklist.md`):
    - `SKILL.md` + `deps-manifest.json` always required
    - `setup.sh` required if ENHANCED/ADVANCED deps exist
    - `update-deps.sh` required if >3 external deps
    - Scripts use Python 3.10+ stdlib, `pathlib.Path`, not `os.path`
14. Update README, taxonomy, and marketplace manifest when a new model-invoked skill is added.
15. Validate with `quick_validate.py` and run any bundled scripts if scripts were added.

## Implementation Workflow

When creating or materially updating a skill, use this sequence:

1. Run curator governance: decide duplicate, merge, split, reference-only, or new skill.
2. Apply the quality lens above: no-op pruning, leading word, completion criteria, token budget.
3. Write SKILL.md using this structure:
   - **Overview**: 1-2 core principles.
   - **When to Use**: symptoms and use cases (no workflow here).
   - **Core Pattern / Execution Steps**: ordered actions, each with a checkable completion criterion.
   - **Quick Reference**: table or bullets for at-a-glance lookup.
   - **Gotchas**: highest-value content — corrects mistakes the agent would make without prompting.
   - **Common Mistakes**: known failure modes with fixes.
   - **References**: links to `references/` files with one-line purpose.
   - **🚀 Quick Start**: complete installation and usage instructions (see `references/installation-template.md`).
4. Write description in third person, imperative mood: `[What] + [When to use]`. Target 100-200 chars, max 1,536 chars. Front-load the leading word.
5. Classify every dependency as `required`, `recommended`, or `optional`. Add to `references/vendor-manifest.yaml`.
6. If an external source influenced the result, add or update source notes.
7. **Cross-platform support**: ensure skill works on macOS, Linux, and Windows (see `references/cross-platform-guide.md`).
   - Use Python install script (`install.py`) instead of Bash (`install.sh`).
   - Use `pathlib.Path` for all path operations.
   - Use `os.symlink` for creating symlinks (handles Windows junction automatically).
   - Provide `check_dependencies.py` for users to verify installation.
8. **Classify capability tiers** using `auto_classify_tiers.py`:
   - Run: `python3 ~/.claude/skills/praxis-skill-forge/scripts/auto_classify_tiers.py --skill <skill-name>`
   - Review auto-classification results
   - Confirm or correct tier assignments (CORE/ENHANCED/ADVANCED)
   - Save to `capability-tiers.json` in skill directory
   - This enables `praxis-skill-publish` to auto-trim for open-source release
9. Run `quick_validate.py` on every changed skill folder, and run bundled scripts when scripts were added.
10. Before ending, run the post-change prompt below.

## Dependency Handling

When a skill depends on another skill or local capability:

Classify dependencies:
- `required`: the skill cannot complete its core workflow without it.
- `recommended`: the skill works with a fallback, but quality or consistency is lower.
- `optional`: only a branch or enhancement needs it.

For every dependency:

1. Document it in the skill body or a reference file with impact and fallback behavior.
2. Add to `references/vendor-manifest.yaml` and back up to `references/vendor/` (see `references/vendor-manifest.md`).
3. Before installing, check target runtime directories for required and recommended dependencies.
4. If missing, ask whether to install or sync it too.
5. If unavailable, state the degraded behavior before finishing.
6. Never copy private credentials, runtime caches, or generated user data.

## Source Tracking Rules

When a skill references external tools, repos, frameworks, prompts, papers, or another skill ecosystem:

1. Create or update `skills/<skill-name>/references/source-notes.md` unless tracked in a more specific file.
2. Record upstream URL, owner, license if known, observed version or commit/date, borrowed patterns, local adaptations, and what to watch for upstream.
3. State what was not copied and why.
4. Add follow-up review cadence only for sources likely to change meaningfully.
5. Never imply endorsement of upstream work; describe local adaptation plainly.
6. Track staleness: add `last_checked` date and mark stale if not verified within 90 days.

## Absorption Rules

- Keep `SKILL.md` concise and self-contained (< 500 lines, < 5,000 tokens).
- Use only portable frontmatter: `name` and `description` (plus optional `metadata`).
- Put longer checklists, source notes, or candidate inventories in `references/`.
- Preserve attribution and update-tracking metadata in references.
- For every external dependency, maintain `references/vendor-manifest.yaml` and `references/vendor/` backup.
- Do not vendor large external skill libraries wholesale.
- If a source is an awesome list, absorb classification and discovery workflows first.

## Post-Change Prompt

After every skill creation or material skill update, explicitly ask:

- Push to remote repository now?
- Install or sync to Codex local skills now?
- Install or sync to Claude local/plugin skills now?
- Install or sync to OpenHuman skills now?
- Install or sync any required or recommended skill dependencies now?
- Verify `references/vendor-manifest.yaml` and `references/vendor/` are up to date?
- If this skill is published externally (GitHub or internal marketplace), run `/praxis-skill-publish` to verify standalone usability before pushing?

Do not push or install automatically unless the user already requested it.

## Fallbacks

- If `references/writing-great-skills.md` is unavailable, continue with the compact quality lens in this `SKILL.md`.
- If `references/effective-skills-checklist.md` is unavailable, use the inline checklist in `references/writing-great-skills.md`.
- If `skill-creator` plugin is unavailable, continue with local praxis-skills compatibility rules.
- If `quick_validate.py` is unavailable, manually verify YAML frontmatter, paths, and registration.

## When Mining Known Sources

| 来源 | 挖什么 | 内化状态 | Reference 文件 |
|------|--------|---------|---------------|
| `mattpocock/skills` | design philosophy, no-op detection, router skill, context/cognitive load theory, sprawl detection, leading word theory | ✅ 已内化 | `writing-great-skills.md`, `no-op-detection.md`, `skill-architecture.md`, `load-theory.md`, `sprawl-detection.md` |
| `anthropics/skills` | eval methodology, progressive disclosure, naming validation, marketplace registration, anti-overfitting, benchmark aggregation | ✅ 已内化 | `skill-evaluation.md`, `token-budget.md`, `naming-validation.md`, `marketplace-registration.md`, `eval-advanced.md` |
| `obra/superpowers` | SDO description format, debugging patterns, brainstorming gate, plan contracts, subagent dispatch, skill writing TDD, persuasion principles, git workflow | ✅ 已内化 | `description-format.md`, `verification-patterns.md`, `design-gate.md`, `skill-writing-tdd.md`, `persuasion-principles.md`, `git-workflow.md` |
| `affaan-m/ECC` | workspace governance, verification loops, continuous learning, selective install, autonomous loops, knowledge architecture, workspace audit, package management | ✅ 已内化 | `verification-patterns.md`, `continuous-learning.md`, `selective-install.md`, `knowledge-architecture.md`, `workspace-audit.md`, `package-management.md` |
| `gsd-build/get-shit-done` | thin-orchestrator, namespace routing, wave execution | ✅ 已内化 | `skill-architecture.md` |
| `ComposioHQ/awesome-claude-skills` | categories, app-automation patterns, quality signals, MCP architecture | ✅ 已内化 | `skill-categorization.md`, `app-automation.md` |
| `hesreallyhim/awesome-claude-code` | hooks, CSV metadata tracking, resource evaluation | ✅ 已内化 | `hook-patterns.md`, `metadata-tracking.md`, `resource-evaluation.md` |
| `msitarzewski/agency-agents` | role templates (review, research, quality, reality-check) | ✅ 已内化 | `role-templates.md` |
| `mvanhorn/last30days-skill` | entity-based research, evidence clustering, brief generation, watchlists | ✅ 已内化 | `research-patterns.md` |
| `anysearch-skill` | runtime.conf persistence, multi-runtime CLI, batch search, offline doc command | ✅ 已内化 | `runtime-config.md` |
| `anysearch-skill` | runtime.conf persistence, multi-runtime CLI, batch search, offline doc command | ✅ 已内化 | `runtime-config.md` |

## Output Shape

For an intake or review, report:

- `Keep`: candidates to absorb now.
- `Watch`: candidates worth monitoring but not localizing yet.
- `Skip`: duplicates, low-fit, risky, or too vendor-specific candidates.
- `Merge / split decision`: whether to merge, split, or create new.
- `Source notes`: upstream references to add or update.
- `Vendor manifest`: dependencies to back up and track.
- `Next edits`: exact files to create or update.

For new skills, use names under `praxis-` unless the user requests a different namespace.

## Evaluation Workflow

When the user asks to evaluate or benchmark a skill:

1. Run the skill against 3+ real-world scenarios.
2. Grade each run: does the output meet the skill's stated completion criteria?
3. Check description trigger accuracy: test with 5 queries that should trigger and 5 that should not.
4. Run the `references/effective-skills-checklist.md` validation.
5. Run `check_consistency.py` to verify SKILL.md matches actual functionality.
6. Report pass rate, identified issues, and improvement suggestions.
7. For A/B comparison, run both versions against the same eval set and compare.

### Consistency Check

Use `scripts/check_consistency.py` to verify SKILL.md matches actual functionality:

```bash
python3 scripts/check_consistency.py <skill-path>
```

Checks performed:
- Every command in SKILL.md has a corresponding script file
- Every script file is documented in SKILL.md
- Trigger phrases in description match actual functionality
- Status values in SKILL.md match actual status values in scripts
- Area values in SKILL.md match actual area values in scripts
- No orphaned scripts (scripts not referenced in SKILL.md)
- No missing scripts (scripts referenced in SKILL.md but not found)

### Open-Source Readiness Check

Use `scripts/check_open_source_readiness.py` to verify a skill is ready for publishing:

```bash
python3 scripts/check_open_source_readiness.py <skill-path>
```

Checks performed:
- No blocked terms (praxis-skill-forge, intake-rubric, capability-tier, etc.)
- No internal scripts (auto_classify_tiers.py, quick_validate.py, etc.)
- No internal references (intake-rubric.md, source-notes.md, etc.)
- LICENSE file exists
- README.md exists
- Installation documentation exists
- Dependencies documented
- Cross-platform compatibility
- No private data (passwords, tokens, API keys, local paths)

**Readiness Tiers**:
- **A — Ship now**: Zero deps, or only system-builtins
- **B — Add prerequisites**: Has CLI/pip deps, no cross-skill
- **C — Surgery needed**: Has cross-skill or private deps
- **D — Not suitable**: Deeply entangled with private infra

**Why check early**:
- Avoid rework when publishing
- Ensure consistency from the start
- Catch issues before they become embedded
- Make publishing a simple process, not a major refactor
