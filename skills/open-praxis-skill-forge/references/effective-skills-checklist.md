# Effective Skills Checklist

Sources: Anthropic best-practices, Skill Creator plugin, mattpocock/skills, obra/superpowers

Use this checklist as the final validation gate before publishing or updating a skill.

## Frontmatter

- [ ] `name` ≤ 64 chars, lowercase + digits + hyphens only, no leading/trailing/double hyphens
- [ ] `name` matches parent directory name
- [ ] `description` ≤ 1,536 chars — `awk '/^description:/{getline; print length}' SKILL.md`
- [ ] `description` includes WHAT the skill does AND WHEN to use it
- [ ] `description` uses third person ("Processes files" not "I can help")
- [ ] `description` has a leading word (verb) at the start
- [ ] `description` contains specific trigger phrases users would actually say
- [ ] No XML/HTML tags in description

## SKILL.md Body

- [ ] Under 500 lines — `wc -l SKILL.md`
- [ ] Under 5,000 tokens — `wc -c SKILL.md` (÷4 ≈ tokens)
- [ ] No time-sensitive information (or marked with expiry date)
- [ ] Consistent terminology throughout
- [ ] File references are one level deep (no reference → reference → reference)
- [ ] Each step has a checkable completion criterion
- [ ] Gotchas section present (highest-value content)
- [ ] Common mistakes section present with fixes

## Structure

- [ ] Overview: 1-2 core principles
- [ ] When to Use: symptoms and use cases, no workflow
- [ ] Core Steps: ordered actions with completion criteria
- [ ] Quick Reference: table or bullets for at-a-glance lookup
- [ ] Gotchas: corrects agent's default mistakes
- [ ] Common Mistakes: failure modes with fixes
- [ ] References: links to external files with one-line purpose

## Consistency Check (SKILL.md vs Actual Functionality)

- [ ] Every command in SKILL.md has a corresponding script file
- [ ] Every script file is documented in SKILL.md
- [ ] Command examples in SKILL.md match actual script syntax
- [ ] Trigger phrases in description match actual functionality
- [ ] Dependencies listed in SKILL.md match deps-manifest.json
- [ ] Capability tiers (CORE/ENHANCED/ADVANCED) match actual implementation
- [ ] Status model in SKILL.md matches actual status values in scripts
- [ ] Area list in SKILL.md matches actual area values in scripts
- [ ] No orphaned scripts (scripts not referenced in SKILL.md)
- [ ] No missing scripts (scripts referenced in SKILL.md but not found)

**Validation Commands**:
```bash
# Run consistency check
python3 scripts/check_consistency.py <skill-path>

# Check trigger phrase accuracy
python3 scripts/eval_runner.py <skill-path>

# Check SKILL.md line count
wc -l SKILL.md

# Quick validation
python3 scripts/quick_validate.py <skill-path>
```

## No-Op Check

- [ ] Every line would change agent behavior if removed
- [ ] No "be thorough", "write good code", "consider edge cases" without specifics
- [ ] No duplicate meanings across sections
- [ ] Weak phrases replaced with strong leading words or deleted

## Progressive Disclosure

- [ ] Core instructions in SKILL.md
- [ ] Branch-specific details in references/
- [ ] Large reference files (>300 lines) have table of contents
- [ ] No reference chain deeper than 1 level

## Description Quality (SDO - Skill Discovery Optimization)

- [ ] Starts with "Use when..." or equivalent trigger condition
- [ ] Does NOT describe the workflow (only the trigger)
- [ ] 100-200 chars is the sweet spot
- [ ] Includes key terms users would search for
- [ ] Not too broad ("Helps with projects") or too narrow (never triggers)

## Scripts

- [ ] Solve problems rather than punt to Claude
- [ ] Error handling is explicit and helpful
- [ ] No "voodoo constants" — all values justified
- [ ] Required packages listed and verified available
- [ ] Scripts have clear documentation
- [ ] No Windows-style paths (all forward slashes)
- [ ] Critical operations have validation steps
- [ ] Quality-critical tasks have feedback loops
- [ ] Non-interactive (no stdin prompts)
- [ ] `--help` documents usage

## Dependencies

- [ ] All dependencies classified as required/recommended/optional
- [ ] `vendor-manifest.yaml` is up to date
- [ ] `vendor/` backup matches manifest
- [ ] Fallback behavior documented for each dependency
- [ ] No private credentials in backup

## Source Tracking

- [ ] All external sources documented in source-notes.md
- [ ] Upstream URL, version/commit, license recorded
- [ ] What was NOT copied is stated with reason
- [ ] `last_checked` date is within 90 days

## Cross-Platform Support

- [ ] Uses Python install script (`install.py`) instead of Bash (`install.sh`)
- [ ] Uses `pathlib.Path` for all path operations (not `os.path`)
- [ ] Uses `os.symlink` for creating symlinks (handles Windows junction)
- [ ] Provides `check_dependencies.py` for users to verify installation
- [ ] Tested on macOS, Linux, and Windows (or documented known issues)
- [ ] No platform-specific code without fallback (e.g., `sys.platform` checks)
- [ ] File permissions only set on macOS/Linux (not Windows)

## Installation & Usage Documentation

- [ ] SKILL.md includes "🚀 Quick Start" section
- [ ] Installation steps are clear and complete:
  - [ ] Clone repository
  - [ ] Run install script (cross-platform)
  - [ ] Check dependencies
  - [ ] Start using
- [ ] Cross-platform install commands provided:
  - [ ] macOS/Linux: `python3 scripts/install.py`
  - [ ] Windows: `python scripts/install.py`
- [ ] `install.py --check` shows dependency status
- [ ] Example output of dependency check shown
- [ ] Common usage examples provided
- [ ] Configuration options documented (if any)
- [ ] Troubleshooting section included (if applicable)

## Verification (if skill has multi-step workflows)

- [ ] Each step has a checkable completion criterion
- [ ] Verification runs before claiming completion (not just "looks good")
- [ ] Structured verification report format (PASS/FAIL per check)

## Open-Source Readiness (for publishing)

**Run `scripts/check_open_source_readiness.py <skill-path>` to verify.**

### Blocked Terms (must be zero)

- [ ] No references to `praxis-skill-forge`
- [ ] No references to `intake-rubric`
- [ ] No references to `capability-tier`
- [ ] No references to `praxis-knowledge-radar` or `praxis-learning-radar`
- [ ] No references to `praxis-skill-publish`
- [ ] No references to `auto_classify`
- [ ] No references to `source-notes`
- [ ] No references to `dependency-lifecycle`
- [ ] No references to `skill-architecture`
- [ ] No references to `curator` or `creative brief`

### Internal Scripts (must not exist)

- [ ] No `auto_classify_tiers.py`
- [ ] No `quick_validate.py`
- [ ] No `vendor_sync.py`
- [ ] No `install_skill.sh`
- [ ] No `link-skills.sh`
- [ ] No `doctor.sh`
- [ ] No `bump-version.sh`
- [ ] No `improve_description.py`
- [ ] No `eval_runner.py`
- [ ] No `check_consistency.py`

### Internal References (must not exist)

- [ ] No `intake-rubric.md`
- [ ] No `source-notes.md`
- [ ] No `dependency-lifecycle.md`
- [ ] No `capability-tiers.md`
- [ ] No `skill-architecture.md`
- [ ] No `skill-file-checklist.md`

### Required Files

- [ ] `LICENSE` file exists
- [ ] `README.md` exists with installation docs
- [ ] `deps-manifest.json` exists (if has dependencies)
- [ ] Installation documentation in SKILL.md or README.md

### No Private Data

- [ ] No passwords or secrets in code
- [ ] No API keys or tokens
- [ ] No local paths (e.g., `/Users/alex/...`)
- [ ] No personal information

### Cross-Platform Compatibility

- [ ] Uses `pathlib.Path` instead of `os.path`
- [ ] Platform-specific code has fallback
- [ ] No macOS-only commands without alternatives

**Validation Commands**:
```bash
# Run open-source readiness check
python3 scripts/check_open_source_readiness.py <skill-path>

# Search for blocked terms
grep -rn "praxis-skill-forge\|intake-rubric\|capability-tier" SKILL.md references/

# Search for private data
grep -rn "/Users/\|password\|secret\|token\|api_key" SKILL.md references/ scripts/
```

## Hooks (if skill uses PostToolUse/PreToolUse)

- [ ] Hook has safe defaults (fail open, not fail closed)
- [ ] Hook has explicit disable mechanism
- [ ] Hook side effects are documented
- [ ] Hook performance is acceptable (<5ms for simple checks)

## Runtime Config (if skill has CLI tools)

- [ ] Runtime detection persisted to config file (not repeated every activation)
- [ ] Fallback procedure if config is missing or stale
- [ ] Offline help available (doc command or --help)

## Quality Signals (from awesome-claude-skills)

### High Quality

- [ ] Based on a real use case, not a hypothetical scenario
- [ ] "When to Use" section lists specific trigger scenarios (not vague)
- [ ] Step-by-step procedural instructions with guardrails
- [ ] Concrete examples with actual prompts (User: "..." / Output: "...")
- [ ] Common pitfalls documented with visual markers (✅/❌)
- [ ] Imperative writing style ("To accomplish X, do Y" not "You should do X")
- [ ] Scripts referenced as black boxes, not read into context
- [ ] "When NOT to use" section prevents misuse
- [ ] Attribution to original sources (if adapted)

### Low Quality (Red Flags)

- [ ] ❌ Vague description ("helps you write better")
- [ ] ❌ No concrete examples or trigger conditions
- [ ] ❌ Everything crammed into SKILL.md instead of scripts/references
- [ ] ❌ No differentiation from what the agent already knows natively
- [ ] ❌ Theoretically interesting but no real-world usage evidence
