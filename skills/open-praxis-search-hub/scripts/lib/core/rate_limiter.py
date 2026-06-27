"""GitHub rate limiter for praxis-search-hub."""

import fcntl
import json
import time
from pathlib import Path
from typing import Any

from .constants import RATE_LIMIT_STATE, GH_MIN_INTERVAL, GH_SESSION_MAX, GH_REMAINING_FLOOR, GH_ETAG_TTL


class GitHubRateLimiter:
    """File-based rate limiter safe across multiple concurrent sessions."""

    def __init__(self) -> None:
        self.state_path = RATE_LIMIT_STATE
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_calls = 0

    def _load_state(self) -> dict[str, Any]:
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {"last_call_ts": 0.0, "etag_cache": {}, "remaining": 30, "reset_ts": 0}

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def acquire(self) -> tuple[bool, str]:
        """Try to acquire permission for a GitHub API call. Returns (ok, reason)."""
        # Session-level limit
        if self.session_calls >= GH_SESSION_MAX:
            return False, f"Session limit reached ({GH_SESSION_MAX} calls). Start a new session to continue."

        # File-locked cross-process check
        lock_path = self.state_path.with_suffix(".lock")
        with open(lock_path, "w") as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_EX)
            try:
                state = self._load_state()
                now = time.time()

                # Minimum interval
                elapsed = now - state.get("last_call_ts", 0)
                if elapsed < GH_MIN_INTERVAL:
                    wait = GH_MIN_INTERVAL - elapsed
                    return False, f"Rate limit: wait {wait:.1f}s (min interval {GH_MIN_INTERVAL}s)"

                # Check if server told us to back off
                remaining = state.get("remaining", 30)
                reset_ts = state.get("reset_ts", 0)
                if remaining < GH_REMAINING_FLOOR and now < reset_ts:
                    wait = reset_ts - now
                    return False, f"GitHub rate limit low (remaining={remaining}), reset in {wait:.0f}s"

                # All checks passed — record the call
                state["last_call_ts"] = now
                self._save_state(state)
                self.session_calls += 1
                return True, "ok"
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)

    def get_etag(self, url: str) -> str | None:
        """Get cached ETag for a URL if still fresh."""
        lock_path = self.state_path.with_suffix(".lock")
        with open(lock_path, "w") as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_EX)
            try:
                state = self._load_state()
                entry = state.get("etag_cache", {}).get(url)
                if entry and time.time() - entry.get("ts", 0) < GH_ETAG_TTL:
                    return entry.get("etag")
                return None
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)

    def update_from_response(self, url: str, headers: dict[str, str], etag: str | None = None) -> None:
        """Update shared state from GitHub response headers."""
        lock_path = self.state_path.with_suffix(".lock")
        with open(lock_path, "w") as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_EX)
            try:
                state = self._load_state()
                # Update rate limit info
                remaining = headers.get("x-ratelimit-remaining")
                reset = headers.get("x-ratelimit-reset")
                if remaining is not None:
                    state["remaining"] = int(remaining)
                if reset is not None:
                    state["reset_ts"] = int(reset)
                # Update ETag cache
                if etag:
                    cache = state.setdefault("etag_cache", {})
                    cache[url] = {"etag": etag, "ts": time.time()}
                # Prune old ETags
                now = time.time()
                state["etag_cache"] = {
                    k: v for k, v in state.get("etag_cache", {}).items()
                    if now - v.get("ts", 0) < GH_ETAG_TTL * 2
                }
                self._save_state(state)
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)

    def get_cached_response(self, url: str) -> Any:
        """Get cached response body for a URL (used with ETag 304)."""
        lock_path = self.state_path.with_suffix(".lock")
        with open(lock_path, "w") as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_EX)
            try:
                state = self._load_state()
                entry = state.get("etag_cache", {}).get(url)
                if entry and time.time() - entry.get("ts", 0) < GH_ETAG_TTL:
                    return entry.get("body")
                return None
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)

    def store_cached_response(self, url: str, body: Any) -> None:
        """Store response body alongside ETag for 304 cache hits."""
        lock_path = self.state_path.with_suffix(".lock")
        with open(lock_path, "w") as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_EX)
            try:
                state = self._load_state()
                cache = state.setdefault("etag_cache", {})
                entry = cache.get(url, {})
                entry["body"] = body
                cache[url] = entry
                self._save_state(state)
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)


# Global rate limiter instance
_gh_limiter = GitHubRateLimiter()
