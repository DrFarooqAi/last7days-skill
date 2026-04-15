"""
GitHub source adapter — Last7Days Skill App
Author: Dr. Farooq
Uses GitHub public REST API. No API key required (60 req/hr unauthenticated).
"""
import time
import requests
from datetime import datetime, timedelta

BASE_URL = "https://api.github.com/search/repositories"
HEADERS = {"Accept": "application/vnd.github+json"}


def fetch(query: str, limit: int = 20) -> list[dict]:
    """Search GitHub for repositories pushed to in the last 7 days."""
    since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    params = {
        "q": f"{query} pushed:>{since}",
        "sort": "stars",
        "order": "desc",
        "per_page": min(limit, 20),
    }
    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = []
        for repo in data.get("items", []):
            items.append({
                "title": repo.get("full_name", ""),
                "url": repo.get("html_url", ""),
                "body": repo.get("description", "") or "",
                "score": repo.get("stargazers_count", 0),
                "source": "GitHub",
                "language": repo.get("language", ""),
                "forks": repo.get("forks_count", 0),
                "timestamp": 0,
            })
        return items
    except Exception:
        return []
