"""HTTP utilities for praxis-search-hub."""

import json
import os
import urllib.parse
import urllib.request
from typing import Any

from .constants import USER_AGENT
from .rate_limiter import _gh_limiter


def fetch_json(url: str, headers: dict[str, str] | None = None, use_etag: bool = False) -> Any:
    """Fetch JSON from a URL. For GitHub API, supports ETag conditional requests."""
    request_headers = {"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}
    request_headers.update(headers or {})
    is_github = "api.github.com" in url
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token and is_github:
        request_headers["Authorization"] = f"Bearer {token}"

    # ETag conditional request for GitHub
    etag = None
    if use_etag and is_github:
        etag = _gh_limiter.get_etag(url)
        if etag:
            request_headers["If-None-Match"] = etag

    request = urllib.request.Request(url, headers=request_headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            data = json.loads(resp.read().decode("utf-8"))
            # Update rate limiter state from GitHub response
            if is_github:
                new_etag = resp_headers.get("etag")
                _gh_limiter.update_from_response(url, resp_headers, new_etag)
                if use_etag and new_etag:
                    _gh_limiter.store_cached_response(url, data)
            return data
    except urllib.error.HTTPError as exc:
        if exc.code == 304 and use_etag and is_github:
            # Not modified — return cached body (costs zero rate limit)
            cached = _gh_limiter.get_cached_response(url)
            if cached is not None:
                return cached
        raise


def _http_get(url: str, timeout: int = 30) -> str:
    """Fetch text from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _http_get_json(url: str, timeout: int = 30) -> Any:
    """Fetch JSON from a URL."""
    return json.loads(_http_get(url, timeout))
