"""Environment utilities for praxis-search-hub."""

import os
import shutil
from pathlib import Path
from typing import Any


def env_bool(name: str, default: bool) -> bool:
    """Get boolean value from environment variable."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def max_limit() -> int:
    """Get maximum result limit from environment."""
    try:
        return max(1, int(os.getenv("PRAXIS_SEARCH_MAX_LIMIT", "10")))
    except ValueError:
        return 10


def clamp_limit(limit: int) -> int:
    """Clamp limit to valid range."""
    return max(1, min(limit, max_limit()))


def command_path(name: str) -> str | None:
    """Find command in PATH."""
    return shutil.which(name)


def skill_exists(path: Path) -> bool:
    """Check if skill file exists."""
    return path.exists() and path.is_file()
