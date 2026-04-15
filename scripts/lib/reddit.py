"""
Reddit source adapter — Last7Days Skill App
Author: Dr. Farooq
Uses Reddit's public JSON API. No API key required.
"""
import requests

HEADERS = {"User-Agent": "Last7Days-Skill-App/1.0 (by Dr. Farooq)"}
BASE_URL = "https://www.reddit.com/search.json"


def fetch(query: str, limit: int = 20) -> list[dict]:
    """Search Reddit for posts from the last 7 days."""
    params = {
        "q": query,
        "sort": "top",
        "t": "week",
        "limit": min(limit, 25),
        "type": "link",
    }
    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = []
        for post in data.get("data", {}).get("children", []):
            p = post.get("data", {})
            items.append({
                "title": p.get("title", ""),
                "url": f"https://reddit.com{p.get('permalink', '')}",
                "body": p.get("selftext", "")[:300],
                "score": p.get("score", 0),
                "source": "Reddit",
                "subreddit": p.get("subreddit_name_prefixed", ""),
                "comments": p.get("num_comments", 0),
                "timestamp": p.get("created_utc", 0),
            })
        return items
    except Exception:
        return []
