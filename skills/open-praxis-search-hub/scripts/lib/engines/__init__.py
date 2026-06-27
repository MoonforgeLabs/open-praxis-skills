"""Built-in search engines for praxis-search-hub (zero dependencies)."""

import json
import re
import urllib.parse
import urllib.request
from typing import Any

from ..core.constants import USER_AGENT
from ..core.http import _http_get, _http_get_json
from ..core.audit import response

# Constants
JINA_READER_URL = "https://r.jina.ai/"
DDG_HTML_URL = "https://html.duckduckgo.com/html/"
GITHUB_API = "https://api.github.com"
NPM_SEARCH_API = "https://registry.npmjs.org/-/v1/search"
BUILTIN_MAX_CHARS = 12000


def _builtin_github_repos(query: str, limit: int) -> dict[str, Any] | None:
    """Search GitHub repos via unauthenticated API (60/hr, Core API, safe)."""
    params = urllib.parse.urlencode({"q": query, "sort": "stars", "order": "desc", "per_page": limit})
    url = f"{GITHUB_API}/search/repositories?{params}"
    data = _http_get_json(url)
    if not data or "items" not in data:
        return None
    results = []
    for item in data["items"][:limit]:
        results.append({
            "name": item.get("full_name", ""),
            "url": item.get("html_url", ""),
            "description": item.get("description") or "",
            "stars": item.get("stargazers_count", 0),
            "language": item.get("language") or "-",
            "updated_at": item.get("updated_at", ""),
        })
    return {"count": len(results), "total": data.get("total_count", 0), "results": results}


def _builtin_npm_search(query: str, limit: int) -> dict[str, Any] | None:
    """Search npm packages (free, no auth)."""
    params = urllib.parse.urlencode({"text": query, "size": limit})
    url = f"{NPM_SEARCH_API}?{params}"
    data = _http_get_json(url)
    if not data or "objects" not in data:
        return None
    results = []
    for obj in data["objects"][:limit]:
        pkg = obj.get("package", {})
        results.append({
            "name": pkg.get("name", ""),
            "version": pkg.get("version", ""),
            "description": pkg.get("description") or "",
            "url": pkg.get("links", {}).get("npm", f"https://www.npmjs.com/package/{pkg.get('name', '')}"),
            "score": round(obj.get("score", {}).get("final", 0), 2),
        })
    return {"count": len(results), "total": data.get("total", 0), "results": results}


def _ddg_extract_results(html: str) -> list[dict[str, str]]:
    """Extract search results from DuckDuckGo HTML response."""
    results = []
    links = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet">(.*?)</(?:a|td|div)', html, re.DOTALL)
    for i, (raw_url, title_html) in enumerate(links[:20]):
        title = re.sub(r'<[^>]+>', '', title_html).strip()
        uddg = re.search(r'uddg=([^&]+)', raw_url)
        url = urllib.parse.unquote(uddg.group(1)) if uddg else raw_url
        snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ""
        if title and url:
            results.append({"title": title, "url": url, "snippet": snippet})
    return results


def _builtin_hn_search(query: str, limit: int) -> dict[str, Any] | None:
    """Search Hacker News via Algolia API (free, no key needed)."""
    params = urllib.parse.urlencode({"query": query, "tags": "story", "hitsPerPage": limit})
    url = f"https://hn.algolia.com/api/v1/search?{params}"
    data = _http_get_json(url, timeout=10)
    if not data or "hits" not in data:
        return None
    results = []
    for hit in data["hits"][:limit]:
        results.append({
            "title": hit.get("title", ""),
            "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
            "description": f"HN ⬆{hit.get('points', 0)} | {hit.get('num_comments', 0)} comments",
            "stars": hit.get("points", 0),
            "source": "hackernews",
        })
    return {"count": len(results), "total": data.get("nbHits", 0), "results": results}


def _builtin_reddit_search(query: str, limit: int) -> dict[str, Any] | None:
    """Search Reddit via public JSON API (free, no key needed)."""
    params = urllib.parse.urlencode({"q": query, "limit": limit, "sort": "relevance", "t": "month"})
    url = f"https://www.reddit.com/search.json?{params}"
    data = _http_get_json(url, headers={"User-Agent": USER_AGENT}, timeout=10)
    if not data or "data" not in data:
        return None
    results = []
    for child in data["data"].get("children", [])[:limit]:
        post = child.get("data", {})
        results.append({
            "title": post.get("title", ""),
            "url": f"https://reddit.com{post.get('permalink', '')}",
            "description": post.get("selftext", "")[:200],
            "stars": post.get("score", 0),
            "source": "reddit",
        })
    return {"count": len(results), "results": results}


def _builtin_ddg_search(query: str, limit: int) -> dict[str, Any] | None:
    """Search via DuckDuckGo HTML (last resort fallback)."""
    params = urllib.parse.urlencode({"q": query})
    url = f"{DDG_HTML_URL}?{params}"
    html = _http_get(url)
    if not html:
        return None
    results = _ddg_extract_results(html)[:limit]
    if not results:
        return None
    return {"count": len(results), "results": results}


def _detect_query_type(query: str) -> str:
    """Detect what type of search the query is about."""
    q = query.lower()
    if any(kw in q for kw in ["npm", "package", "module", "yarn", "pnpm"]):
        return "npm"
    if any(kw in q for kw in ["github", "repo", "stars", "framework", "library", "sdk", "cli tool", "open source"]):
        return "github"
    if any(kw in q for kw in ["pypi", "pip", "python package"]):
        return "npm"  # route to npm as similar
    if any(kw in q for kw in ["news", "latest", "trend", "trending", "2025", "2026", "hacker"]):
        return "trending"
    if any(kw in q for kw in ["tutorial", "guide", "how to", "learn", "course", "blog"]):
        return "general"
    return "general"


def builtin_search(query: str, limit: int) -> dict[str, Any]:
    """Smart built-in search: routes to best free API based on query type."""
    channel = "web:builtin"
    qtype = _detect_query_type(query)
    errors = []

    # Strategy 1: Type-specific API
    if qtype == "npm":
        result = _builtin_npm_search(query, limit)
        if result:
            return response(channel=channel, query=query, backend="npm", query_type=qtype, **result)
        errors.append("npm search failed")

    if qtype in ("github", "general", "code_discovery"):
        result = _builtin_github_repos(query, limit)
        if result:
            return response(channel=channel, query=query, backend="github-unauth", query_type=qtype, **result)
        errors.append("github search failed")

    # Strategy 2: For general/trending queries, try HN and Reddit
    if qtype in ("general", "trending"):
        result = _builtin_hn_search(query, limit)
        if result:
            return response(channel=channel, query=query, backend="hackernews", query_type=qtype, **result)

        result = _builtin_reddit_search(query, limit)
        if result:
            return response(channel=channel, query=query, backend="reddit", query_type=qtype, **result)

    # Strategy 3: DDG as last resort
    result = _builtin_ddg_search(query, limit)
    if result:
        return response(channel=channel, query=query, backend="ddg", query_type=qtype, **result)

    # Strategy 4: npm for non-npm queries
    if qtype != "npm":
        result = _builtin_npm_search(query, limit)
        if result:
            return response(channel=channel, query=query, backend="npm-fallback", query_type=qtype, **result)

    return response(ok=False, channel=channel, query=query, error=f"All built-in backends failed: {'; '.join(errors)}", results=[])


def fetch_url(url: str) -> dict[str, Any]:
    """Fetch and extract content from a URL. Tries Jina Reader, falls back to direct fetch."""
    channel = "fetch"
    # Try Jina Reader first (better extraction)
    jina_url = f"{JINA_READER_URL}{url}"
    content = _http_get(jina_url, timeout=20)
    if content and len(content) > 100:
        return response(channel=channel, query=url, backend="jina", raw=content[:BUILTIN_MAX_CHARS], results=[])
    # Fallback: direct fetch
    content = _http_get(url)
    if content:
        text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return response(channel=channel, query=url, backend="direct", raw=text[:BUILTIN_MAX_CHARS], results=[])
    return response(ok=False, channel=channel, query=url, error="Fetch failed", results=[])
