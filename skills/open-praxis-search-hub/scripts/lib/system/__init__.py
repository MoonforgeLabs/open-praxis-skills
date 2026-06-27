"""System diagnostics for praxis-search-hub."""

import json
from pathlib import Path
from typing import Any

from ..core.constants import AGENT_REACH_SKILL, LAST30DAYS_SKILL, GH_MIN_INTERVAL, GH_SESSION_MAX, CAPABILITY_TIERS
from ..core.env import env_bool, max_limit, command_path, skill_exists
from ..core.audit import audit, response
from ..core.rate_limiter import _gh_limiter


def dependency_status() -> dict[str, Any]:
    """Get dependency status."""
    commands = {name: command_path(name) for name in ["agent-reach", "mcporter", "opencli", "bili", "gh"]}
    skills = {
        "agent_reach_skill": str(AGENT_REACH_SKILL) if skill_exists(AGENT_REACH_SKILL) else None,
        "last30days_skill": str(LAST30DAYS_SKILL) if skill_exists(LAST30DAYS_SKILL) else None,
    }
    return {"commands": commands, "skills": skills}


def status() -> dict[str, Any]:
    """Show gateway status."""
    deps = dependency_status()
    # Rate limiter state
    rl_state = _gh_limiter._load_state()
    rate_limit_info = {
        "gh_remaining": rl_state.get("remaining", "unknown"),
        "gh_reset_ts": rl_state.get("reset_ts", 0),
        "gh_min_interval": GH_MIN_INTERVAL,
        "gh_session_max": GH_SESSION_MAX,
        "gh_session_used": _gh_limiter.session_calls,
        "gh_etag_cache_size": len(rl_state.get("etag_cache", {})),
    }
    data = {
        "github_repos_enabled": env_bool("PRAXIS_SEARCH_GITHUB_ENABLED", False),
        "github_code_enabled": env_bool("PRAXIS_SEARCH_GITHUB_CODE_ENABLED", False),
        "exa_enabled": env_bool("PRAXIS_SEARCH_EXA_ENABLED", True),
        "opencli_enabled": env_bool("PRAXIS_SEARCH_OPENCLI_ENABLED", True),
        "bili_enabled": env_bool("PRAXIS_SEARCH_BILI_ENABLED", True),
        "last30days_enabled": env_bool("PRAXIS_SEARCH_LAST30DAYS_ENABLED", False),
        "max_limit": max_limit(),
        "audit_log": str(Path(os.getenv("PRAXIS_SEARCH_AUDIT_LOG", "~/.praxis-search-hub/audit.jsonl")).expanduser()),
        "audit_log_fallback": "/tmp/praxis-search-hub/audit.jsonl",
        "rate_limit": rate_limit_info,
        **deps,
    }
    audit({"channel": "status", **data})
    return {"ok": True, "channel": "status", **data}


def doctor() -> dict[str, Any]:
    """Dependency health check."""
    deps = dependency_status()
    findings: list[dict[str, Any]] = []
    checks = [
        ("agent-reach command", deps["commands"].get("agent-reach"), "Install Agent-Reach or restore ~/.local/bin / Hermes PATH."),
        ("agent-reach skill", deps["skills"].get("agent_reach_skill"), "Install / restore ~/.agents/skills/agent-reach."),
        ("mcporter", deps["commands"].get("mcporter"), "Install or configure mcporter for Exa web search."),
        ("opencli", deps["commands"].get("opencli"), "Install OpenCLI for xiaohongshu/twitter/reddit channels."),
        ("bili", deps["commands"].get("bili"), "Install bili-cli for Bilibili search."),
        ("gh", deps["commands"].get("gh"), "Install GitHub CLI only after GitHub flagged status is resolved."),
        ("last30days skill", deps["skills"].get("last30days_skill"), "Restore ~/.agents/skills/last30days for manual deep research."),
    ]
    for name, available, fix in checks:
        findings.append({"name": name, "ok": bool(available), "path": available, "fix": None if available else fix})
    # Built-in capabilities (always available with just Python)
    builtins = [
        {"name": "web search (DuckDuckGo)", "ok": True, "note": "Built-in fallback when mcporter unavailable"},
        {"name": "URL fetch (direct)", "ok": True, "note": "Built-in fallback when Jina unavailable"},
        {"name": "gh-suggest", "ok": True, "note": "Zero API cost, generates search URLs/commands"},
        {"name": "gh-lookup (via gh CLI)", "ok": bool(command_path("gh")), "note": "Core API, 5000/hr"},
    ]
    risk = []
    if not env_bool("PRAXIS_SEARCH_GITHUB_ENABLED", False):
        risk.append("GitHub repository search is disabled, safe for flagged-account period.")
    if not env_bool("PRAXIS_SEARCH_GITHUB_CODE_ENABLED", False):
        risk.append("GitHub code search is disabled, safe for flagged-account period.")
    result = {"ok": True, "channel": "doctor", "findings": findings, "builtins": builtins, "risk_controls": risk, **deps}
    audit({"channel": "doctor", "findings": findings, "risk_controls": risk})
    return result


def tiers_cmd() -> dict[str, Any]:
    """Show capability tiers for open-source planning."""
    result = {"ok": True, "channel": "tiers", "tiers": {}}
    for name, info in CAPABILITY_TIERS.items():
        tier = info["tier"]
        if tier not in result["tiers"]:
            result["tiers"][tier] = []
        result["tiers"][tier].append({
            "command": name,
            "deps": info["deps"],
            "desc": info["desc"],
        })
    result["summary"] = {
        "CORE": f"{sum(1 for v in CAPABILITY_TIERS.values() if v['tier']=='CORE')} commands — zero dependencies",
        "ENHANCED": f"{sum(1 for v in CAPABILITY_TIERS.values() if v['tier']=='ENHANCED')} commands — optional CLI tools",
        "ADVANCED": f"{sum(1 for v in CAPABILITY_TIERS.values() if v['tier']=='ADVANCED')} commands — remove or stub in open-source",
    }
    return result


def backends_cmd() -> dict[str, Any]:
    """Show which search backends are currently active and their priority."""
    has_mcporter = bool(command_path("mcporter"))
    has_opencli = bool(command_path("opencli"))
    has_bili = bool(command_path("bili"))
    has_gh = bool(command_path("gh"))
    has_agent_reach_skill = skill_exists(AGENT_REACH_SKILL)
    has_last30days_skill = skill_exists(LAST30DAYS_SKILL)

    # Determine web search priority
    if has_mcporter:
        web_primary = "Exa (via mcporter/Agent-Reach) ★ 最高质量"
        web_fallback = "GitHub API → npm → DuckDuckGo (内置)"
    else:
        web_primary = "GitHub API (unauthenticated, 60/hr)"
        web_fallback = "npm registry → DuckDuckGo HTML (内置)"

    # Determine social capability
    social_channels = []
    if has_bili:
        social_channels.append("bilibili")
    if has_opencli:
        social_channels.extend(["xiaohongshu", "toutiao", "twitter", "reddit"])
    if not social_channels:
        social_channels = ["(全部 skipped — 需要 Agent-Reach)"]

    return {
        "ok": True,
        "channel": "backends",
        "web_search": {
            "primary": web_primary,
            "fallback": web_fallback,
            "uses_agent_reach": has_mcporter,
        },
        "social_search": {
            "available": social_channels,
            "uses_agent_reach": has_opencli or has_bili,
        },
        "github_search": {
            "gh_lookup": "✅ 可用" if has_gh else "❌ 需要 gh CLI",
            "github_repos": "✅ 开启" if env_bool("PRAXIS_SEARCH_GITHUB_ENABLED", False) else "⬜ 关闭 (默认)",
            "github_code": "✅ 开启" if env_bool("PRAXIS_SEARCH_GITHUB_CODE_ENABLED", False) else "⬜ 关闭 (默认)",
        },
        "deep_research": {
            "available": has_last30days_skill,
            "status": "✅ 可用" if has_last30days_skill else "❌ 需要 last30days skill",
        },
        "agent_reach_status": "✅ 已安装" if (has_mcporter and has_opencli) else "⚠️ 部分或未安装",
        "last30days_status": "✅ 已安装" if has_last30days_skill else "❌ 未安装",
    }


# Import os for environment variables
import os
