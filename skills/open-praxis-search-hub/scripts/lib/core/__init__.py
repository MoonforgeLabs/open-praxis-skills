"""Core infrastructure for praxis-search-hub."""

from .constants import (
    USER_AGENT,
    AGENT_REACH_SKILL,
    LAST30DAYS_SKILL,
    RATE_LIMIT_STATE,
    GH_MIN_INTERVAL,
    GH_SESSION_MAX,
    GH_REMAINING_FLOOR,
    GH_ETAG_TTL,
    CAPABILITY_TIERS,
)

from .env import (
    env_bool,
    max_limit,
    clamp_limit,
    command_path,
    skill_exists,
)

from .audit import (
    audit,
    response,
    skipped,
    run_command,
)

from .rate_limiter import (
    GitHubRateLimiter,
    _gh_limiter,
)

from .http import (
    fetch_json,
    _http_get,
    _http_get_json,
)

__all__ = [
    # Constants
    "USER_AGENT",
    "AGENT_REACH_SKILL",
    "LAST30DAYS_SKILL",
    "RATE_LIMIT_STATE",
    "GH_MIN_INTERVAL",
    "GH_SESSION_MAX",
    "GH_REMAINING_FLOOR",
    "GH_ETAG_TTL",
    "CAPABILITY_TIERS",
    # Environment
    "env_bool",
    "max_limit",
    "clamp_limit",
    "command_path",
    "skill_exists",
    # Audit
    "audit",
    "response",
    "skipped",
    "run_command",
    # Rate limiter
    "GitHubRateLimiter",
    "_gh_limiter",
    # HTTP
    "fetch_json",
    "_http_get",
    "_http_get_json",
]
