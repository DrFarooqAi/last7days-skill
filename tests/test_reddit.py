"""Tests for Reddit adapter — Last7Days Skill App by Dr. Farooq"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from unittest.mock import patch, MagicMock
from lib.reddit import fetch


def _mock_response(posts):
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = {
        "data": {"children": [{"data": p} for p in posts]}
    }
    return mock


def test_fetch_returns_list():
    with patch("lib.reddit.requests.get") as mock_get:
        mock_get.return_value = _mock_response([
            {"title": "Test post", "permalink": "/r/test/1", "score": 100,
             "selftext": "body", "subreddit_name_prefixed": "r/test",
             "num_comments": 10, "created_utc": 1700000000},
        ])
        results = fetch("test query", limit=5)
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["source"] == "Reddit"
    assert results[0]["score"] == 100


def test_fetch_handles_empty():
    with patch("lib.reddit.requests.get") as mock_get:
        mock_get.return_value = _mock_response([])
        results = fetch("empty query")
    assert results == []


def test_fetch_handles_network_error():
    with patch("lib.reddit.requests.get", side_effect=Exception("network error")):
        results = fetch("failing query")
    assert results == []
