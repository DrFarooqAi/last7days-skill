"""
Hacker News source adapter — Last7Days Skill App
Author: Dr. Farooq
Uses Algolia HN API. No API key required.
"""
import time
import requests

BASE_URL = "https://hn.algolia.com/api/v1/search"


def fetch(query: str, limit: int = 20) -> list[dict]:
    """Search Hacker News for stories from the last 7 days."""
    seven_days_ago = int(time.time()) - (7 * 24 * 60 * 60)
    params = {
        "query": query,
        "tags": "story",
        "numericFilters": f"created_at_i>{seven_days_ago}",
        "hitsPerPage": min(limit, 20),
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = []
        for hit in data.get("hits", []):
            items.append({
                "title": hit.get("title", ""),
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                "body": hit.get("story_text", "")[:300] if hit.get("story_text") else "",
                "score": hit.get("points", 0),
                "source": "HackerNews",
                "comments": hit.get("num_comments", 0),
                "timestamp": hit.get("created_at_i", 0),
            })
        return items
    except Exception:
        return []
