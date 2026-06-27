"""Channel adapters for praxis-search-hub."""

import json
import os
import urllib.parse
from pathlib import Path
from typing import Any

from ..core.constants import USER_AGENT, AGENT_REACH_SKILL, LAST30DAYS_SKILL
from ..core.env import env_bool, max_limit, clamp_limit, command_path, skill_exists
from ..core.audit import response, skipped, run_command
from ..core.http import fetch_json
from ..core.rate_limiter import _gh_limiter
from ..engines import builtin_search, fetch_url, _detect_query_type


def gh_suggest(query: str, limit: int) -> dict[str, Any]:
    """Generate GitHub search URLs and CLI commands — zero API cost."""
    channel = "gh-suggest"
    limit = clamp_limit(limit)

    # Build smart query variations
    encoded = urllib.parse.quote_plus(query)
    queries = {
        "raw": query,
        "with_stars": f"{query} stars:>100",
        "recent_push": f"{query} pushed:>={_days_ago(30)}",
        "recent_created": f"{query} created:>={_days_ago(90)}",
    }

    results = []
    for variant_name, q in queries.items():
        results.append({
            "variant": variant_name,
            "query": q,
            "github_url": f"https://github.com/search?q={urllib.parse.quote_plus(q)}&type=repositories",
            "cli_command": f'gh search repos "{q}" --limit {limit} --sort updated',
            "cli_with_fields": f'gh search repos "{q}" --limit {limit} --json name,owner,description,stargazersCount,updatedAt,url',
        })

    code_queries = {
        "raw": query,
        "recent_push": f"{query} pushed:>={_days_ago(30)}",
    }
    code_results = []
    for variant_name, q in code_queries.items():
        code_results.append({
            "variant": variant_name,
            "query": q,
            "github_url": f"https://github.com/search?q={urllib.parse.quote_plus(q)}&type=code",
            "cli_command": f'gh search code "{q}" --limit {limit}',
        })

    return response(
        channel=channel,
        query=query,
        limit=limit,
        note="These are ready-to-use links and commands. Copy and run manually — no API cost.",
        repo_queries=results,
        code_search=code_results[0] if code_results else None,
        quick_lookups=[
            "gh repo view <owner>/<repo>",
            "gh api repos/<owner>/<repo>",
            "gh api repos/<owner>/<repo>/topics",
        ],
        results=[],
    )


def _days_ago(n: int) -> str:
    """Get date string for n days ago."""
    from datetime import datetime, timedelta
    return (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d")


def gh_lookup(repo: str) -> dict[str, Any]:
    """Look up a single GitHub repo via Core API (safe, 5000/hr)."""
    channel = "gh-lookup"
    if not command_path("gh"):
        return skipped(channel, repo, "gh CLI not installed", dependency="gh")

    command = ["gh", "api", f"repos/{repo}", "--jq",
               "{name: .full_name, url: .html_url, description: .description, stars: .stargazers_count, "
               "forks: .forks_count, open_issues: .open_issues_count, language: .language, "
               "license: .license.spdx_id, topics: .topics, created_at: .created_at, "
               "updated_at: .updated_at, pushed_at: .pushed_at, archived: .archived, "
               "default_branch: .default_branch, visibility: .visibility}"]

    code, stdout, stderr = run_command(command)
    if code != 0:
        return response(ok=False, channel=channel, query=repo, error=stderr.strip() or stdout.strip(), results=[])

    try:
        data = json.loads(stdout)
        return response(channel=channel, query=repo, count=1, results=[data])
    except json.JSONDecodeError:
        return response(ok=False, channel=channel, query=repo, error="Failed to parse gh output", results=[])


def web(query: str, limit: int, dry_run: bool) -> dict[str, Any]:
    """Web search via Exa (primary) or built-in fallback."""
    channel = "web"
    if not env_bool("PRAXIS_SEARCH_EXA_ENABLED", True):
        return skipped(channel, query, "Exa web search disabled by PRAXIS_SEARCH_EXA_ENABLED=false")
    limit = clamp_limit(limit)

    # Primary: Exa via mcporter
    if command_path("mcporter"):
        command = ["mcporter", "call", f"exa.web_search_exa(query: {json.dumps(query, ensure_ascii=False)}, numResults: {limit})"]
        if dry_run:
            return response(channel=channel, query=query, dry_run=True, command=command, results=[])
        code, stdout, stderr = run_command(command)
        if code != 0:
            return response(ok=False, channel=channel, query=query, error=stderr.strip() or stdout.strip(), results=[])
        return response(channel=channel, query=query, backend="exa", raw=stdout[:8000], results=[])

    # Fallback: smart built-in search (GitHub unauth / npm / DDG)
    if dry_run:
        return response(channel=channel, query=query, dry_run=True, backend="builtin-fallback",
                        query_type=_detect_query_type(query), results=[])
    return builtin_search(query, limit)


def social(platform: str, query: str, limit: int, dry_run: bool) -> dict[str, Any]:
    """Search social media platforms."""
    platform = platform.lower()
    limit = clamp_limit(limit)
    if platform in {"bilibili", "bili", "b站"}:
        if not env_bool("PRAXIS_SEARCH_BILI_ENABLED", True):
            return skipped("social:bilibili", query, "Bilibili search disabled by PRAXIS_SEARCH_BILI_ENABLED=false")
        if not command_path("bili"):
            return skipped("social:bilibili", query, "bili command not found, install Agent-Reach optional Bilibili backend", dependency="bili")
        command = ["bili", "search", query, "--type", "video", "-n", str(limit)]
    elif platform in {"xiaohongshu", "xhs", "小红书"}:
        if not env_bool("PRAXIS_SEARCH_OPENCLI_ENABLED", True):
            return skipped("social:xiaohongshu", query, "OpenCLI search disabled by PRAXIS_SEARCH_OPENCLI_ENABLED=false")
        if not command_path("opencli"):
            return skipped("social:xiaohongshu", query, "opencli not found, install OpenCLI via Agent-Reach", dependency="opencli")
        command = ["opencli", "xiaohongshu", "search", query, "-f", "yaml"]
    elif platform in {"toutiao", "今日头条", "头条"}:
        if not env_bool("PRAXIS_SEARCH_OPENCLI_ENABLED", True):
            return skipped("social:toutiao", query, "OpenCLI search disabled by PRAXIS_SEARCH_OPENCLI_ENABLED=false")
        if not command_path("opencli"):
            return skipped("social:toutiao", query, "opencli not found, install OpenCLI via Agent-Reach", dependency="opencli")
        command = ["opencli", "toutiao", "hot", "--limit", str(limit), "-f", "yaml"]
    elif platform in {"twitter", "x", "reddit"}:
        if not env_bool("PRAXIS_SEARCH_OPENCLI_ENABLED", True):
            return skipped(f"social:{platform}", query, "OpenCLI search disabled by PRAXIS_SEARCH_OPENCLI_ENABLED=false")
        if not command_path("opencli"):
            return skipped(f"social:{platform}", query, "opencli not found, install OpenCLI via Agent-Reach", dependency="opencli")
        command = ["opencli", platform, "search", query, "-f", "yaml"]
    else:
        return skipped("social", query, f"Unsupported social platform: {platform}")
    if dry_run:
        return response(channel=f"social:{platform}", query=query, dry_run=True, command=command, results=[])
    code, stdout, stderr = run_command(command)
    if code != 0:
        return response(ok=False, channel=f"social:{platform}", query=query, error=stderr.strip() or stdout.strip(), results=[])
    return response(channel=f"social:{platform}", query=query, raw=stdout[:8000], results=[])


LAST30DAYS_SCRIPT = Path.home() / ".agents/skills/last30days/scripts/last30days.py"


def deep_research(query: str, dry_run: bool, use_llm: bool = False) -> dict[str, Any]:
    """Deep research via last30days CLI. Actually executes, not just suggests."""
    channel = "deep-research"
    if not skill_exists(LAST30DAYS_SKILL):
        return skipped(channel, query, "last30days skill not installed", missing=str(LAST30DAYS_SKILL))
    if not LAST30DAYS_SCRIPT.exists():
        return skipped(channel, query, "last30days.py script not found", missing=str(LAST30DAYS_SCRIPT))

    # Base command
    command = [
        "python3", str(LAST30DAYS_SCRIPT),
        "--emit", "json",
    ]

    # If use_llm, enable deep mode (uses LLM for synthesis)
    # Otherwise, use quick mode (data aggregation only)
    if use_llm:
        command.append("--deep")
    else:
        command.append("--quick")

    # Always exclude GitHub search to prevent rate limiting
    command.extend(["--search", "grounding"])

    command.extend(query.split())
    if dry_run:
        return response(channel=channel, query=query, dry_run=True, command=command, results=[])

    code, stdout, stderr = run_command(command, timeout=120)
    if code != 0:
        return response(ok=False, channel=channel, query=query,
                        error=stderr.strip()[:2000] or stdout.strip()[:2000], results=[])

    # Parse JSON output
    try:
        data = json.loads(stdout)
        return response(channel=channel, query=query, backend="last30days", raw=json.dumps(data, ensure_ascii=False)[:8000], results=[])
    except json.JSONDecodeError:
        # If not JSON, return raw text
        return response(channel=channel, query=query, backend="last30days", raw=stdout[:8000], results=[])
