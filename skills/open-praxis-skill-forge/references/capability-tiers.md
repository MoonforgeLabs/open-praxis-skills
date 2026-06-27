# Capability Tiers Convention

Shared convention for marking skill capabilities by dependency level.
Used by: praxis-skill-forge (create), praxis-search-hub (runtime), praxis-skill-publish (trim).

## Tiers

| Tier | Color | Meaning | Open-source action |
|------|-------|---------|-------------------|
| **CORE** | 🟢 | Python stdlib only, zero external deps | Keep as-is |
| **ENHANCED** | 🟡 | Optional CLI tools, graceful degradation | Keep, document degradation |
| **ADVANCED** | 🔴 | External skills, auth APIs, heavy deps | Remove or stub |

## Where to Mark

### Option A: In Python script (preferred for scripts with CLI)

```python
CAPABILITY_TIERS = {
    "command-name": {
        "tier": "CORE",           # CORE | ENHANCED | ADVANCED
        "deps": [],                # list of required tools/keys
        "desc": "What it does",
    },
}
```

Expose via CLI:
```bash
python3 scripts/skill.py tiers   # outputs JSON of all tiers
```

### Option B: In deps-manifest.json (preferred for pure SKILL.md skills)

```json
{
  "tiers": {
    "CORE": {
      "commands": ["cmd1", "cmd2"],
      "deps": {"python": ">=3.10", "pip": [], "npm": []}
    },
    "ENHANCED": {
      "commands": ["cmd3"],
      "deps": {"system": ["gh"], "npm": ["tool-name"]}
    },
    "ADVANCED": {
      "commands": ["cmd4"],
      "deps": {"skills": ["other-skill"], "env": ["API_KEY"]}
    }
  }
}
```

## Mapping to Open-Source Readiness

| Capability Tier | → Readiness Tier | Action |
|----------------|-----------------|--------|
| CORE | A — Ship now | Just add README |
| ENHANCED | B — Add prerequisites | Document install + degradation |
| ADVANCED (optional) | C — Surgery needed | Inline or add fallback |
| ADVANCED (required) | D — Not suitable | Do not open-source |

## Example: praxis-search-hub

```
CORE (10):  status, doctor, ratelimit, gate, backends, gh-suggest, web, fetch, research, catalog
ENHANCED (2): gh-lookup (gh CLI), social (opencli/bili)
ADVANCED (3): github-repos (GITHUB_TOKEN), github-code (GITHUB_TOKEN), deep-research (last30days)

Open-source: keep CORE + ENHANCED (12/15), remove ADVANCED
```

## Checklist for Curator

When creating or updating a skill:

- [ ] Every command/feature has a tier assignment
- [ ] `deps` list is accurate (no hidden deps)
- [ ] `ENHANCED` tier has graceful degradation (skipped, not crashed)
- [ ] `ADVANCED` tier has clear removal path for open-source
- [ ] `deps-manifest.json` exists if skill has >3 commands
- [ ] `tiers` command works if skill is a Python script
