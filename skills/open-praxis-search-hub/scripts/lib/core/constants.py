"""Core constants and configuration for praxis-search-hub."""

from pathlib import Path

# User agent for HTTP requests
USER_AGENT = "praxis-search-hub/0.5"

# Skill paths
AGENT_REACH_SKILL = Path.home() / ".agents/skills/agent-reach/SKILL.md"
LAST30DAYS_SKILL = Path.home() / ".agents/skills/last30days/SKILL.md"

# Rate limit config
RATE_LIMIT_STATE = Path.home() / ".praxis-search-hub/ratelimit.json"
GH_MIN_INTERVAL = 3.0        # seconds between GitHub calls (20/min, safe margin under 30/min)
GH_SESSION_MAX = 10          # max GitHub calls per session
GH_REMAINING_FLOOR = 10      # pause when x-ratelimit-remaining drops below this
GH_ETAG_TTL = 900            # ETag cache TTL in seconds (15 min)

# Capability tiers
CAPABILITY_TIERS = {
    # ── CORE: zero dependencies ──
    "status":       {"tier": "CORE", "deps": [], "desc": "Show gateway status"},
    "doctor":       {"tier": "CORE", "deps": [], "desc": "Dependency health check"},
    "ratelimit":    {"tier": "CORE", "deps": ["fcntl"], "desc": "Rate limiter state"},
    "gate":         {"tier": "CORE", "deps": [], "desc": "Search strategy analysis"},
    "backends":     {"tier": "CORE", "deps": [], "desc": "Show active backends"},
    "gh-suggest":   {"tier": "CORE", "deps": [], "desc": "Generate search URLs/commands"},
    "web":          {"tier": "CORE", "deps": [], "desc": "Web search (auto-fallback chain)"},
    "fetch":        {"tier": "CORE", "deps": [], "desc": "URL content extraction"},
    "research":     {"tier": "CORE", "deps": [], "desc": "Multi-source research pipeline"},
    "catalog":      {"tier": "CORE", "deps": [], "desc": "Research memory"},
    # ── ENHANCED: optional CLI tools ──
    "gh-lookup":    {"tier": "ENHANCED", "deps": ["gh"], "desc": "Single repo lookup"},
    "social":       {"tier": "ENHANCED", "deps": ["opencli|bili"], "desc": "Social media search"},
    # ── ADVANCED: external skills or auth ──
    "github-repos": {"tier": "ADVANCED", "deps": ["GITHUB_TOKEN"], "desc": "GitHub repo search (authenticated)"},
    "github-code":  {"tier": "ADVANCED", "deps": ["GITHUB_TOKEN"], "desc": "GitHub code search (authenticated)"},
    "deep-research":{"tier": "ADVANCED", "deps": ["last30days"], "desc": "Deep research via last30days"},
}
