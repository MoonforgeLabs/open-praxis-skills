"""
Evidence Extraction — trust grading and claim extraction from search results.

Reference:
  - research-ai-skills (siosio34/research-ai-skills): evidence ledger with A-D trust grades
    https://github.com/siosio34/research-ai-skills
  - AnkitClassicVision/Claude-Code-Deep-Research: verification gates, residual claims
    https://github.com/AnkitClassicVision/Claude-Code-Deep-Research
  - fathomx (Runa798/fathomx): epistemological marking, confidence + falsifiability
    https://github.com/Runa798/fathomx

Design:
  - Each search result gets a trust grade (A-D) based on source type and signals.
  - Key claims are extracted from descriptions/snippets.
  - Confidence is computed from cross-source agreement and source quality.
"""
from __future__ import annotations

from typing import Any


# Trust grade definitions
GRADES = {
    "A": "Official documentation, primary source, verified",
    "B": "Reputable secondary source, high stars/activity",
    "C": "Community content, blog post, unverified",
    "D": "Low authority, new project, no signals",
}


def grade_source(result: dict[str, Any], channel: str, backend: str) -> str:
    """Assign a trust grade (A-D) to a search result based on source signals."""
    url = result.get("url", "").lower()
    stars = result.get("stars", 0)

    # Grade A: Official / primary sources
    if any(d in url for d in [
        "docs.github.com", "docs.python.org", "nodejs.org/docs",
        "developer.mozilla.org", "learn.microsoft.com",
        "arxiv.org", "doi.org", "pubmed",
        "anthropic.com", "openai.com", "google.com",
    ]):
        return "A"
    if channel in ("web",) and backend in ("exa",):
        return "A"  # Exa semantic search is high quality

    # Grade B: Reputable with strong signals
    if stars and stars >= 1000:
        return "B"
    if "github.com" in url and stars and stars >= 100:
        return "B"
    if channel in ("web:builtin",) and backend in ("github-unauth",):
        return "B" if stars and stars >= 100 else "C"

    # Grade C: Community content
    if any(d in url for d in [
        "reddit.com", "stackoverflow.com", "medium.com",
        "dev.to", "hashnode.com", "blog.",
    ]):
        return "C"
    if channel.startswith("social"):
        return "C"

    # Grade D: Low authority
    return "D"


def compute_confidence(results: list[dict[str, Any]]) -> float:
    """Compute overall confidence (0.0-1.0) from cross-source agreement."""
    if not results:
        return 0.0

    # Factor 1: Number of results (more = higher confidence)
    count_score = min(len(results) / 10, 1.0)

    # Factor 2: Average trust grade
    grade_scores = {"A": 1.0, "B": 0.75, "C": 0.5, "D": 0.25}
    avg_grade = sum(grade_scores.get(r.get("grade", "D"), 0.25) for r in results) / len(results)

    # Factor 3: Cross-source agreement (URLs from different domains)
    domains = set()
    for r in results:
        url = r.get("url", "")
        parts = url.split("/")
        if len(parts) >= 3:
            domains.add(parts[2])
    diversity_score = min(len(domains) / 5, 1.0)

    # Weighted combination
    confidence = 0.3 * count_score + 0.4 * avg_grade + 0.3 * diversity_score
    return round(confidence, 2)


def extract_evidence(results: list[dict[str, Any]], channel: str = "", backend: str = "") -> list[dict[str, Any]]:
    """Enrich results with trust grade, confidence, and extracted claims."""
    enriched = []
    for r in results:
        grade = grade_source(r, channel, backend)
        description = r.get("description", r.get("snippet", ""))

        # Extract key claims (first sentence or first 150 chars)
        claims = []
        if description:
            sentences = [s.strip() for s in description.replace(". ", ".\n").split("\n") if s.strip()]
            claims = sentences[:3]  # Top 3 claims

        enriched.append({
            **r,
            "grade": grade,
            "grade_desc": GRADES.get(grade, ""),
            "claims": claims,
        })

    # Add overall confidence
    confidence = compute_confidence(enriched)
    for r in enriched:
        r["confidence"] = confidence

    return enriched


def summarize_evidence(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize the evidence quality of a result set."""
    if not results:
        return {"total": 0, "confidence": 0.0, "grades": {}}

    grades = {}
    for r in results:
        g = r.get("grade", "D")
        grades[g] = grades.get(g, 0) + 1

    return {
        "total": len(results),
        "confidence": compute_confidence(results),
        "grades": grades,
        "top_sources": [
            {"title": r.get("title", r.get("name", ""))[:60], "grade": r.get("grade"), "url": r.get("url", "")}
            for r in sorted(results, key=lambda x: {"A": 0, "B": 1, "C": 2, "D": 3}.get(x.get("grade", "D"), 9))[:5]
        ],
    }
