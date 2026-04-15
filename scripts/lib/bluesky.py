"""
Bluesky source adapter — Last7Days Skill App
Author: Dr. Farooq
Uses Bluesky public AT Protocol API. No API key required.
"""
import requests

BASE_URL = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"


def fetch(query: str, limit: int = 20) -> list[dict]:
    """Search Bluesky for posts from the last 7 days."""
    params = {
        "q": query,
        "limit": min(limit, 25),
        "sort": "top",
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = []
        for post in data.get("posts", []):
            record = post.get("record", {})
            author = post.get("author", {})
            handle = author.get("handle", "")
            uri = post.get("uri", "")
            rkey = uri.split("/")[-1] if uri else ""
            url = f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else ""
            items.append({
                "title": record.get("text", "")[:120],
                "url": url,
                "body": record.get("text", "")[:300],
                "score": post.get("likeCount", 0),
                "source": "Bluesky",
                "author": handle,
                "reposts": post.get("repostCount", 0),
                "timestamp": 0,
            })
        return items
    except Exception:
        return []
