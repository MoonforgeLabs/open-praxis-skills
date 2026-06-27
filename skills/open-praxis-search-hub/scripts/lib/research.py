"""
Research Orchestrator — multi-source search with deduplication and structured reports.

Reference:
  - deep-research-claude (dbc-oduffy/deep-research-claude): four-pipeline architecture
    https://github.com/dbc-oduffy/deep-research-claude
  - claude-code-deep-research-v2 (jamoeight): AggAgent + BATS budget awareness
    https://github.com/jamoeight/claude-code-deep-research-v2
  - fomo-researcher (razpetel/fomo-researcher): cross-source synthesis
    https://github.com/razpetel/fomo-researcher
  - GPT Researcher (assafelovic/gpt-researcher): planner/executor/publisher
    https://github.com/assafelovic/gpt-researcher

Design:
  - Pipeline: check catalog → search multi-source → deduplicate → evidence grading → report
  - Budget-aware: respects search quotas and rate limits
  - Graceful degradation: if a source fails, continue with others
"""
from __future__ import annotations

import json
import time
from typing import Any

# These are imported from the main module at runtime
# to avoid circular imports we use a lazy pattern


def _get_search_functions():
    """Lazy import to avoid circular dependency."""
    import importlib.util
    import sys
    from pathlib import Path

    # Import the main module
    main_path = Path(__file__).parent.parent / "safe_search.py"
    spec = importlib.util.spec_from_file_location("safe_search", main_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_research(
    query: str,
    max_sources: int = 3,
    include_social: bool = False,
    use_catalog: bool = True,
) -> dict[str, Any]:
    """
    Run a multi-source research pipeline.

    Steps:
    1. Check catalog for existing results
    2. Search primary source (web)
    3. Search secondary sources (gh-suggest, optionally social)
    4. Deduplicate across sources
    5. Apply evidence grading
    6. Return structured report
    """
    from . import catalog, evidence, gate

    start_time = time.time()
    errors = []
    all_results = []
    sources_used = []

    # Step 1: Check catalog
    catalog_results = []
    if use_catalog:
        catalog_results = catalog.recall(query, limit=5)
        if catalog_results:
            sources_used.append(f"catalog ({len(catalog_results)} cached)")

    # Step 2: Search primary source (web)
    mod = _get_search_functions()
    web_result = mod.web(query, max_sources, dry_run=False)
    if web_result.get("ok") and not web_result.get("skipped"):
        web_results = web_result.get("results", [])
        backend = web_result.get("backend", "unknown")
        channel = web_result.get("channel", "web")
        if web_results:
            all_results.extend(web_results)
            sources_used.append(f"{channel}:{backend} ({len(web_results)} results)")
        raw = web_result.get("raw", "")
        if raw and not web_results:
            sources_used.append(f"{channel}:{backend} (raw text)")
            # Also try built-in search for structured results
            builtin_result = mod.builtin_search(query, max_sources)
            if builtin_result and builtin_result.get("ok"):
                builtin_results = builtin_result.get("results", [])
                if builtin_results:
                    all_results.extend(builtin_results)
                    sources_used.append(f"builtin:{builtin_result.get('backend','?')} ({len(builtin_results)} results)")
    else:
        errors.append(f"web: {web_result.get('reason', web_result.get('error', 'unknown'))}")
        # Fallback: try built-in search directly
        builtin_result = mod.builtin_search(query, max_sources)
        if builtin_result and builtin_result.get("ok"):
            builtin_results = builtin_result.get("results", [])
            if builtin_results:
                all_results.extend(builtin_results)
                sources_used.append(f"builtin:{builtin_result.get('backend','?')} ({len(builtin_results)} results)")

    # Step 3: gh-suggest (zero cost)
    if len(all_results) < max_sources * 2:
        suggest_result = mod.gh_suggest(query, max_sources)
        if suggest_result.get("ok"):
            repo_queries = suggest_result.get("repo_queries", [])
            if repo_queries:
                sources_used.append(f"gh-suggest ({len(repo_queries)} variants)")

    # Step 4: Social search (optional)
    if include_social and len(all_results) < max_sources * 3:
        for platform in ["bilibili", "xiaohongshu"]:
            social_result = mod.social(platform, query, max_sources, dry_run=False)
            if social_result.get("ok") and not social_result.get("skipped"):
                social_results = social_result.get("results", [])
                if social_results:
                    all_results.extend(social_results)
                    sources_used.append(f"social:{platform} ({len(social_results)} results)")

    # Step 5: Deduplicate by URL
    seen_urls = set()
    deduped = []
    for r in all_results:
        url = r.get("url", r.get("html_url", ""))
        if url and url not in seen_urls:
            seen_urls.add(url)
            deduped.append(r)

    # Step 6: Evidence grading
    graded = evidence.extract_evidence(deduped, channel="research", backend="multi")
    evidence_summary = evidence.summarize_evidence(graded)

    # Step 7: Store in catalog
    if graded:
        catalog.store(query, graded, channel="research", backend="multi")

    elapsed = round(time.time() - start_time, 1)

    # Get channel recommendations
    recommendations = gate.recommend_channels(query)

    return {
        "ok": True,
        "channel": "research",
        "query": query,
        "elapsed_seconds": elapsed,
        "sources_used": sources_used,
        "errors": errors,
        "from_catalog": len(catalog_results),
        "total_found": len(all_results),
        "after_dedup": len(deduped),
        "evidence": evidence_summary,
        "recommendations": recommendations,
        "results": graded[:max_sources * 3],
        "catalog_hint": f"Run 'catalog list' to see all researched topics" if graded else None,
    }
