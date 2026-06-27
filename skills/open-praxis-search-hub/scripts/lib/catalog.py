"""
Research Catalog — persistent search memory with topic-based deduplication.

Reference:
  - fomo-researcher (razpetel/fomo-researcher): semantic memory + research catalogue
    https://github.com/razpetel/fomo-researcher
  - mindgap (grburgess/mindgap): compound memory architecture, knowledge graph
    https://github.com/grburgess/mindgap
  - research-catalogue (razpetel/research-catalogue): git as research memory
    https://github.com/razpetel/research-catalogue

Design:
  - Each search result is stored as a catalog entry with topic tags, source, and timestamp.
  - Topics are auto-extracted from query keywords.
  - Before searching, check the catalog for recent results on the same topic.
  - Catalog entries expire after configurable TTL (default 7 days).
"""
from __future__ import annotations

import json
import re
import time
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

CATALOG_DIR = Path.home() / ".praxis-search-hub/catalog"
CATALOG_TTL = 7 * 86400  # 7 days


def _ensure_dir() -> None:
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)


def _normalize_topic(query: str) -> str:
    """Extract a normalized topic key from a query string."""
    # Remove common qualifiers and noise words
    noise = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
             "how", "what", "why", "when", "where", "which", "who",
             "and", "or", "not", "but", "for", "to", "of", "in", "on",
             "with", "from", "by", "at", "this", "that", "it", "its"}
    words = re.findall(r'[a-z0-9]+', query.lower())
    keywords = sorted(set(w for w in words if w not in noise and len(w) > 2))
    return "-".join(keywords[:8])  # max 8 keywords as topic key


def _topic_file(topic: str) -> Path:
    safe = re.sub(r'[^a-z0-9\-]', '', topic)
    return CATALOG_DIR / f"{safe}.jsonl"


def store(query: str, results: list[dict[str, Any]], channel: str, backend: str = "") -> str:
    """Store search results in the catalog. Returns the topic key."""
    _ensure_dir()
    topic = _normalize_topic(query)
    path = _topic_file(topic)
    now = time.time()

    entries = []
    for r in results:
        entry = {
            "ts": now,
            "query": query,
            "channel": channel,
            "backend": backend,
            "topic": topic,
            "url": r.get("url", ""),
            "title": r.get("title", r.get("name", "")),
            "description": r.get("description", r.get("snippet", "")),
            "stars": r.get("stars", 0),
        }
        entries.append(entry)

    # Append to topic file
    with path.open("a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return topic


def recall(query: str, max_age: int = CATALOG_TTL, limit: int = 10) -> list[dict[str, Any]]:
    """Recall recent results for the same or similar topic."""
    _ensure_dir()
    topic = _normalize_topic(query)
    now = time.time()
    cutoff = now - max_age

    # Direct topic match
    path = _topic_file(topic)
    results = _read_entries(path, cutoff)

    # Fuzzy match on other topic files
    if len(results) < limit:
        for f in CATALOG_DIR.glob("*.jsonl"):
            if f == path:
                continue
            other_topic = f.stem
            similarity = SequenceMatcher(None, topic, other_topic).ratio()
            if similarity > 0.4:
                results.extend(_read_entries(f, cutoff))

    # Deduplicate by URL
    seen = set()
    deduped = []
    for r in results:
        url = r.get("url", "")
        if url and url not in seen:
            seen.add(url)
            deduped.append(r)

    # Sort by timestamp (most recent first)
    deduped.sort(key=lambda x: x.get("ts", 0), reverse=True)
    return deduped[:limit]


def _read_entries(path: Path, cutoff: float) -> list[dict[str, Any]]:
    """Read catalog entries from a JSONL file, filtering by time."""
    entries = []
    if not path.exists():
        return entries
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("ts", 0) >= cutoff:
                    entries.append(entry)
            except json.JSONDecodeError:
                continue
    return entries


def list_topics(days: int = 7) -> list[dict[str, Any]]:
    """List all topics in the catalog with entry counts."""
    _ensure_dir()
    cutoff = time.time() - days * 86400
    topics = []
    for f in sorted(CATALOG_DIR.glob("*.jsonl")):
        entries = _read_entries(f, cutoff)
        if entries:
            topics.append({
                "topic": f.stem,
                "count": len(entries),
                "last_search": max(e.get("ts", 0) for e in entries),
                "queries": list(set(e.get("query", "") for e in entries))[:3],
            })
    topics.sort(key=lambda x: x["last_search"], reverse=True)
    return topics


def prune(max_age: int = CATALOG_TTL * 4) -> int:
    """Remove entries older than max_age. Returns count of removed entries."""
    _ensure_dir()
    cutoff = time.time() - max_age
    removed = 0
    for f in CATALOG_DIR.glob("*.jsonl"):
        entries = _read_entries(f, float("inf"))  # read all
        kept = [e for e in entries if e.get("ts", 0) >= cutoff]
        removed += len(entries) - len(kept)
        if kept:
            with f.open("w", encoding="utf-8") as fh:
                for e in kept:
                    fh.write(json.dumps(e, ensure_ascii=False) + "\n")
        else:
            f.unlink()
    return removed
