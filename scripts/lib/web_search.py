"""
Web search adapter — Last7Days Skill App
Author: Dr. Farooq
Uses DuckDuckGo search via duckduckgo-search library. No API key required.
"""
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS


def fetch(query: str, limit: int = 10) -> list[dict]:
    """Search the web for recent results related to the query."""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(
                f"{query} last 7 days",
                max_results=min(limit, 15),
            ):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "body": r.get("body", "")[:300],
                    "score": 0,
                    "source": "Web",
                    "timestamp": 0,
                })
        return results
    except Exception:
        return []
