#!/usr/bin/env python3
"""
Alex Safe Search — unified search gateway with risk control, audit, and degradation.

Refactored architecture:
  - lib/core/: infrastructure (constants, env, audit, rate_limiter, http)
  - lib/engines/: built-in search engines (GitHub, npm, HN, Reddit, DDG)
  - lib/channels/: channel adapters (web, social, gh-lookup, deep-research)
  - lib/research/: research capabilities (catalog, evidence, gate, orchestrator)
  - lib/system/: system diagnostics (status, doctor, backends, tiers)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Add lib/ to path for module imports
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# Import from new module structure
from lib.core import (
    CAPABILITY_TIERS,
    env_bool,
    max_limit,
    clamp_limit,
    command_path,
    skill_exists,
    audit,
    response,
    skipped,
    run_command,
)

from lib.engines import (
    builtin_search,
    fetch_url,
    _detect_query_type,
)

from lib.channels import (
    gh_suggest,
    gh_lookup,
    web,
    social,
    deep_research,
)

from lib.system import (
    status,
    doctor,
    dependency_status,
    tiers_cmd,
    backends_cmd,
)

# Import research modules (existing)
from lib import catalog, evidence, gate


def ratelimit_cmd(action: str) -> dict[str, Any]:
    """Rate limiter management."""
    from lib.core.rate_limiter import _gh_limiter
    from lib.core.constants import GH_MIN_INTERVAL, GH_SESSION_MAX

    if action == "show":
        state = _gh_limiter._load_state()
        return {
            "ok": True,
            "channel": "ratelimit",
            "gh_remaining": state.get("remaining", "unknown"),
            "gh_reset_in": f"{max(0, state.get('reset_ts', 0) - int(__import__('time').time()))}s" if state.get("reset_ts") else "unknown",
            "last_call_ago": f"{int(__import__('time').time() - state.get('last_call_ts', 0))}s" if state.get("last_call_ts") else "never",
            "session_calls": _gh_limiter.session_calls,
            "session_max": GH_SESSION_MAX,
            "min_interval": f"{GH_MIN_INTERVAL}s",
            "etag_cache_entries": len(state.get("etag_cache", {})),
            "state_file": str(_gh_limiter.state_path),
        }
    elif action == "reset":
        _gh_limiter._save_state({"last_call_ts": 0.0, "etag_cache": {}, "remaining": 30, "reset_ts": 0})
        _gh_limiter.session_calls = 0
        return {"ok": True, "channel": "ratelimit", "action": "reset", "message": "Rate limiter state reset."}
    return {"ok": False, "channel": "ratelimit", "error": f"Unknown action: {action}"}


def catalog_cmd(action: str, query: str, days: int) -> dict[str, Any]:
    """Research memory management."""
    if action == "list":
        topics = catalog.list_topics()
        return response(channel="catalog", action="list", topics=topics, count=len(topics), results=[])
    elif action == "recall":
        entries = catalog.recall(query)
        return response(channel="catalog", action="recall", query=query, entries=entries, count=len(entries), results=[])
    elif action == "prune":
        pruned = catalog.prune(days=days)
        return response(channel="catalog", action="prune", pruned=pruned, results=[])
    return {"ok": False, "channel": "catalog", "error": f"Unknown action: {action}"}


def research_cmd(query: str, max_sources: int, social: bool) -> dict[str, Any]:
    """Multi-source research pipeline."""
    from lib.research import orchestrator
    return orchestrator.run_research(query, max_sources=max_sources, include_social=social)


def gate_cmd() -> dict[str, Any]:
    """Search strategy analysis."""
    return gate.recommend_channels()


def anysearch_cmd(query: str, domain: str, sub_domain: str, limit: int, dry_run: bool) -> dict[str, Any]:
    """Search using AnySearch vertical domain search."""
    channel = "anysearch"

    # Import anysearch module
    try:
        from lib.anysearch import search, list_domains
    except ImportError:
        return skipped(channel, query, "anysearch module not found", missing="lib/anysearch.py")

    if dry_run:
        return response(channel=channel, query=query, dry_run=True,
                       domain=domain, sub_domain=sub_domain, limit=limit, results=[])

    # Execute search
    result = search(query, domain=domain, sub_domain=sub_domain, max_results=limit)

    if "error" in result:
        return response(ok=False, channel=channel, query=query,
                       error=result["error"], results=[])

    return response(channel=channel, query=query, backend="anysearch",
                   domain=domain, sub_domain=sub_domain,
                   raw=json.dumps(result, ensure_ascii=False)[:8000], results=[])


def anysearch_domains_cmd() -> dict[str, Any]:
    """List available AnySearch domains."""
    try:
        from lib.anysearch import list_domains
        domains = list_domains()
    except ImportError:
        domains = ["general", "finance", "academic", "legal", "health",
                   "business", "security", "ip", "code", "energy",
                   "environment", "agriculture", "travel", "film", "gaming"]

    return {
        "ok": True,
        "channel": "anysearch-domains",
        "domains": domains,
        "count": len(domains),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Alex safe search gateway")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("doctor")
    rl_p = sub.add_parser("ratelimit")
    rl_p.add_argument("action", choices=["show", "reset"], nargs="?", default="show")
    # gh-suggest: generate search URLs/commands, zero API cost
    suggest_p = sub.add_parser("gh-suggest")
    suggest_p.add_argument("query")
    suggest_p.add_argument("--limit", type=int, default=5)
    # gh-lookup: look up a single repo via core API (safe, 5000/hr)
    lookup_p = sub.add_parser("gh-lookup")
    lookup_p.add_argument("repo", help="owner/repo, e.g. anthropics/claude-code")
    # fetch: extract content from a URL via Jina Reader (built-in, zero deps)
    fetch_p = sub.add_parser("fetch")
    fetch_p.add_argument("url", help="URL to fetch and extract content from")
    for name in ["web", "github-repos", "github-code"]:
        p = sub.add_parser(name)
        p.add_argument("query")
        p.add_argument("--limit", type=int, default=5)
        p.add_argument("--dry-run", action="store_true")
    social_p = sub.add_parser("social")
    social_p.add_argument("platform")
    social_p.add_argument("query")
    social_p.add_argument("--limit", type=int, default=5)
    social_p.add_argument("--dry-run", action="store_true")
    deep_p = sub.add_parser("deep-research")
    deep_p.add_argument("query")
    deep_p.add_argument("--dry-run", action="store_true")
    deep_p.add_argument("--use-llm", action="store_true",
                        help="Enable LLM reasoning for synthesis (requires API key)")
    # catalog: research memory management
    cat_p = sub.add_parser("catalog")
    cat_p.add_argument("action", choices=["list", "recall", "prune"])
    cat_p.add_argument("--query", default="")
    cat_p.add_argument("--days", type=int, default=7)
    # research: multi-source research pipeline
    res_p = sub.add_parser("research")
    res_p.add_argument("query")
    res_p.add_argument("--max-sources", type=int, default=3)
    res_p.add_argument("--social", action="store_true", help="Include social media sources")
    # gate: search strategy analysis
    sub.add_parser("gate")
    # backends: show which search backends are active
    sub.add_parser("backends")
    # tiers: show capability tiers for open-source planning
    sub.add_parser("tiers")
    # anysearch: vertical domain search via AnySearch API
    anysearch_p = sub.add_parser("anysearch")
    anysearch_p.add_argument("query", help="Search query")
    anysearch_p.add_argument("--domain", default="general",
                            choices=["general", "finance", "academic", "legal", "health",
                                    "business", "security", "ip", "code", "energy",
                                    "environment", "agriculture", "travel", "film", "gaming"],
                            help="Search domain")
    anysearch_p.add_argument("--sub-domain", default="", help="Sub-domain for vertical search")
    anysearch_p.add_argument("--limit", type=int, default=5, help="Max results (1-10)")
    anysearch_p.add_argument("--dry-run", action="store_true")
    # anysearch-domains: list available domains
    sub.add_parser("anysearch-domains")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "status":
            result = status()
        elif args.command == "doctor":
            result = doctor()
        elif args.command == "ratelimit":
            result = ratelimit_cmd(args.action)
        elif args.command == "gh-suggest":
            result = gh_suggest(args.query, args.limit)
        elif args.command == "gh-lookup":
            result = gh_lookup(args.repo)
        elif args.command == "fetch":
            result = fetch_url(args.url)
        elif args.command == "web":
            result = web(args.query, args.limit, args.dry_run)
        elif args.command == "github-repos":
            result = github_repos(args.query, args.limit, args.dry_run)
        elif args.command == "github-code":
            result = github_code(args.query, args.limit, args.dry_run)
        elif args.command == "social":
            result = social(args.platform, args.query, args.limit, args.dry_run)
        elif args.command == "deep-research":
            result = deep_research(args.query, args.dry_run, args.use_llm)
        elif args.command == "catalog":
            result = catalog_cmd(args.action, args.query, args.days)
        elif args.command == "research":
            result = research_cmd(args.query, args.max_sources, args.social)
        elif args.command == "gate":
            result = gate_cmd()
        elif args.command == "backends":
            result = backends_cmd()
        elif args.command == "tiers":
            result = tiers_cmd()
        elif args.command == "anysearch":
            result = anysearch_cmd(args.query, args.domain, args.sub_domain, args.limit, args.dry_run)
        elif args.command == "anysearch-domains":
            result = anysearch_domains_cmd()
        else:
            raise ValueError(args.command)
    except Exception as exc:  # noqa: BLE001
        result = {"ok": False, "skipped": False, "error": str(exc), "results": []}
        audit(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
