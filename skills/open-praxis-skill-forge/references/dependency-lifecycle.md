# Dependency Lifecycle Convention

Every skill that has external dependencies MUST declare how they are installed, checked, and updated.
Used by: praxis-skill-forge (intake), praxis-skill-publish (audit), praxis-search-hub (reference implementation).

## Required Metadata

For each external dependency, declare:

| Field | Example | Required |
|-------|---------|----------|
| name | `mcporter` | ✅ |
| type | `npm` / `pipx` / `brew` / `skills.sh` / `git` / `system` | ✅ |
| install | `npm install -g mcporter` | ✅ |
| check | `mcporter --version` | ✅ |
| update | `npm update -g mcporter` | ✅ |
| check-latest | `npm info mcporter version` | recommended |
| platform | `cross-platform` / `macos` / `linux` / `windows` | ✅ |
| tier | `CORE` / `ENHANCED` / `ADVANCED` | ✅ |
| optional | `true` / `false` | ✅ |

## Dependency Types and Update Commands

| Type | Install | Check | Update | Check Latest |
|------|---------|-------|--------|-------------|
| **npm** | `npm install -g <pkg>` | `<cmd> --version` | `npm update -g <pkg>` | `npm info <pkg> version` |
| **pipx** | `pipx install <pkg>` | `<cmd> --version` | `pipx upgrade <pkg>` | `pip index versions <pkg>` |
| **brew** | `brew install <cmd>` | `<cmd> --version` | `brew upgrade <cmd>` | `brew info <cmd>` |
| **skills.sh** | `npx skills add <owner>/<repo>` | `grep version SKILL.md` | `npx skills update <name>` | `gh api repos/<owner>/<repo>/releases/latest` |
| **git** | `git clone <url> <dir>` | `git log --oneline -1` | `cd <dir> && git pull` | `git fetch && git log origin/main -1` |
| **system** | (pre-installed) | `<cmd> --version` | N/A (OS managed) | N/A |
| **env var** | `export KEY=value` | `echo $KEY` | N/A | N/A |

## Skill File vs CLI Separation

Some dependencies have TWO parts:

```
agent-reach
├── CLI (pipx)     → pipx upgrade agent-reach
└── Skill (skills.sh) → npx skills update agent-reach

last30days
└── Skill (skills.sh) → npx skills update last30days

mcporter
└── CLI (npm)      → npm update -g mcporter
```

**Rule**: If a dependency has both a CLI and a skill file, BOTH must be declared separately.

## Where to Declare

### Option A: In deps-manifest.json (preferred)

```json
{
  "dependencies": {
    "mcporter": {
      "type": "npm",
      "tier": "ENHANCED",
      "install": "npm install -g mcporter",
      "check": "mcporter --version",
      "update": "npm update -g mcporter",
      "check_latest": "npm info mcporter version",
      "platform": "cross-platform",
      "optional": true
    }
  }
}
```

### Option B: In update-deps.sh (for skills with many deps)

Each dependency has a `check_update` call:

```bash
MCP_CUR=$(mcporter --version 2>/dev/null)
MCP_LATEST=$(npm info mcporter version 2>/dev/null)
check_update "mcporter" "ENHANCED" "$MCP_CUR" "$MCP_LATEST" "npm update -g mcporter"
```

## Curator Checklist (Intake Step 12)

When creating or updating a skill with external dependencies:

- [ ] Every dependency has install/check/update commands documented
- [ ] `deps-manifest.json` includes `dependencies` section with lifecycle info
- [ ] Skill file dependencies use `skills.sh` (not manual copy)
- [ ] CLI dependencies use appropriate package manager (npm/pipx/brew)
- [ ] `update-deps.sh` or equivalent exists for skills with >3 dependencies
- [ ] Update commands are tested and working
- [ ] Platform-specific caveats documented (e.g., fcntl Windows)

## Reference Implementation

praxis-search-hub has a complete `update-deps.sh` that demonstrates:

1. **Version check**: compare current vs latest for each dependency
2. **Tier-aware**: only check/update dependencies in the target tier
3. **Check-only mode**: `--check` flag for dry-run
4. **Dual-layer update**: CLI via package manager + skill files via skills.sh
5. **Error handling**: track success/failure counts

Copy this pattern for any skill with external dependencies.
