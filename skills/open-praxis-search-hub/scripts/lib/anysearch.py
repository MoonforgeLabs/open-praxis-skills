"""AnySearch integration for praxis-search-hub.

Provides vertical domain search capabilities from anysearch-skill.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

# AnySearch API endpoint
ANYSEARCH_ENDPOINT = "https://api.anysearch.com/mcp"

# Available domains
AVAILABLE_DOMAINS = [
    "general", "resource", "social_media", "finance", "academic", "legal",
    "health", "business", "security", "ip", "code", "energy",
    "environment", "agriculture", "travel", "film", "gaming",
]


def _load_api_key() -> str:
    """Load AnySearch API key from environment or .env file."""
    # Check environment variable first
    api_key = os.environ.get("ANYSEARCH_API_KEY")
    if api_key:
        return api_key
    
    # Check .env file in anysearch-skill directory
    skill_dir = os.path.expanduser("~/.agents/skills/anysearch-skill")
    for env_path in [os.path.join(skill_dir, "scripts", ".env"), 
                     os.path.join(skill_dir, ".env")]:
        if os.path.isfile(env_path):
            with open(env_path, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip().lstrip(chr(0xFEFF))
                    value = value.strip().strip("\"'").strip()
                    if key == "ANYSEARCH_API_KEY" and value:
                        return value
    
    return ""


def _call_api(tool_name: str, arguments: dict, api_key: str) -> dict:
    """Call AnySearch API."""
    import requests
    
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    
    try:
        resp = requests.post(ANYSEARCH_ENDPOINT, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def search(query: str, domain: str = "general", sub_domain: str = "", 
           max_results: int = 5, api_key: str = "") -> dict:
    """Search using AnySearch.
    
    Args:
        query: Search query
        domain: Search domain (general, finance, academic, etc.)
        sub_domain: Sub-domain for vertical search
        max_results: Maximum results (1-10)
        api_key: AnySearch API key (optional)
    
    Returns:
        Search results dict
    """
    if not api_key:
        api_key = _load_api_key()
    
    arguments = {"query": query, "max_results": max_results}
    if domain and domain != "general":
        arguments["domain"] = domain
    if sub_domain:
        arguments["sub_domain"] = sub_domain
    
    return _call_api("search", arguments, api_key)


def batch_search(queries: List[Dict[str, Any]], api_key: str = "") -> dict:
    """Batch search using AnySearch.
    
    Args:
        queries: List of query dicts with 'query', 'domain', 'sub_domain' keys
        api_key: AnySearch API key (optional)
    
    Returns:
        Batch search results dict
    """
    if not api_key:
        api_key = _load_api_key()
    
    arguments = {"queries": queries}
    return _call_api("batch_search", arguments, api_key)


def extract(url: str, api_key: str = "") -> dict:
    """Extract content from URL using AnySearch.
    
    Args:
        url: URL to extract content from
        api_key: AnySearch API key (optional)
    
    Returns:
        Extracted content dict
    """
    if not api_key:
        api_key = _load_api_key()
    
    arguments = {"url": url}
    return _call_api("extract", arguments, api_key)


def get_sub_domains(domain: str, api_key: str = "") -> dict:
    """Get available sub-domains for a domain.
    
    Args:
        domain: Domain name
        api_key: AnySearch API key (optional)
    
    Returns:
        Sub-domains dict
    """
    if not api_key:
        api_key = _load_api_key()
    
    arguments = {"domain": domain}
    return _call_api("get_sub_domains", arguments, api_key)


def list_domains() -> List[str]:
    """List available domains."""
    return AVAILABLE_DOMAINS
