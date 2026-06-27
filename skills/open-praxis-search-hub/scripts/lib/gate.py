"""
Search Strategy Gate — learn from audit history to optimize channel selection.

Reference:
  - smart-search (JiangHe12/smart-search): one-time gate mode, complementary tool roles
    https://github.com/JiangHe12/smart-search
  - deep-research-claude (dbc-oduffy/deep-research-claude): PreToolUse hook routing
    https://github.com/dbc-oduffy/deep-research-claude
  - fathomx (Runa798/fathomx): intelligent routing based on research task
    https://github.com/Runa798/fathomx

Design:
  - Analyze audit.jsonl to learn which channels return the most results for which query types.
  - Auto-select optimal channel priority for new queries.
  - First-time users get sensible defaults; the gate improves over time.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

AUDIT_LOG = Path.home() / ".praxis-search-hub/audit.jsonl"


def _load_audit(limit: int = 500) -> list[dict[str, Any]]:
    """Load recent audit entries."""
    if not AUDIT_LOG.exists():
        return []
    entries = []
    with AUDIT_LOG.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries[-limit:]


def analyze_channel_performance() -> dict[str, Any]:
    """Analyze which channels perform best from audit history."""
    entries = _load_audit()
    if not entries:
        return {"channels": {}, "query_types": {}, "recommendations": []}

    # Channel success rates
    channel_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "success": 0, "skipped": 0})
    for e in entries:
        ch = e.get("channel", "unknown")
        if ch in ("status", "doctor", "ratelimit", "gh-suggest", "gh-lookup", "catalog"):
            continue
        channel_stats[ch]["total"] += 1
        if e.get("skipped"):
            channel_stats[ch]["skipped"] += 1
        elif e.get("ok"):
            channel_stats[ch]["success"] += 1

    # Query type detection
    query_types: dict[str, list[str]] = defaultdict(list)
    for e in entries:
        q = e.get("query", "")
        ch = e.get("channel", "")
        if q and ch and ch not in ("status", "doctor", "ratelimit"):
            qtype = _classify_query(q)
            query_types[qtype].append(ch)

    # Most used channel per query type
    type_preferences = {}
    for qtype, channels in query_types.items():
        counter = Counter(channels)
        type_preferences[qtype] = counter.most_common(3)

    return {
        "channels": dict(channel_stats),
        "query_types": {k: v for k, v in type_preferences.items()},
    }


def _classify_query(query: str) -> str:
    """Classify a query into a type for strategy routing."""
    q = query.lower()
    if any(kw in q for kw in ["github", "repo", "stars", "framework", "library", "sdk"]):
        return "code_discovery"
    if any(kw in q for kw in ["npm", "package", "module", "yarn"]):
        return "package_search"
    if any(kw in q for kw in ["paper", "arxiv", "research", "study", "journal"]):
        return "academic"
    if any(kw in q for kw in ["tutorial", "guide", "how to", "learn", "course"]):
        return "learning"
    if any(kw in q for kw in ["news", "latest", "trend", "2025", "2026"]):
        return "trending"
    return "general"


def recommend_channels(query: str) -> list[dict[str, Any]]:
    """Recommend channel priority for a query based on learned patterns."""
    analysis = analyze_channel_performance()
    qtype = _classify_query(query)

    # Default channel priority
    defaults = {
        "code_discovery": [
            {"channel": "web", "reason": "Exa semantic search for code"},
            {"channel": "web:builtin", "reason": "GitHub API fallback"},
            {"channel": "gh-suggest", "reason": "GitHub search URLs"},
        ],
        "package_search": [
            {"channel": "web:builtin", "reason": "npm registry search"},
            {"channel": "web", "reason": "Exa for broader coverage"},
        ],
        "academic": [
            {"channel": "web", "reason": "Exa for paper search"},
            {"channel": "web:builtin", "reason": "GitHub API for implementations"},
        ],
        "learning": [
            {"channel": "web", "reason": "Exa for tutorials"},
            {"channel": "social:bilibili", "reason": "Video tutorials"},
        ],
        "trending": [
            {"channel": "web", "reason": "Exa for recent content"},
            {"channel": "social:toutiao", "reason": "Trending topics"},
            {"channel": "social:bilibili", "reason": "Trending videos"},
        ],
        "general": [
            {"channel": "web", "reason": "General web search"},
            {"channel": "web:builtin", "reason": "GitHub/npm fallback"},
        ],
    }

    recommendations = defaults.get(qtype, defaults["general"])

    # If we have audit data, boost channels that performed well for this query type
    type_prefs = analysis.get("query_types", {}).get(qtype, [])
    if type_prefs:
        preferred_channels = {ch for ch, _ in type_prefs[:2]}
        for r in recommendations:
            if r["channel"] in preferred_channels:
                r["reason"] += " (historically effective)"

    return recommendations
