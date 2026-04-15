"""Tests for HackerNews adapter — Last7Days Skill App by Dr. Farooq"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from unittest.mock import patch, MagicMock
from lib.hackernews import fetch


def _mock_response(hits):
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = {"hits": hits}
    return mock


def test_fetch_returns_list():
    with patch("lib.hackernews.requests.get") as mock_get:
        mock_get.return_value = _mock_response([
            {"title": "Show HN: cool project", "url": "https://example.com",
             "points": 250, "num_comments": 42, "objectID": "123",
             "story_text": None, "created_at_i": 1700000000},
        ])
        results = fetch("cool project", limit=5)
    assert isinstance(results, list)
    assert results[0]["source"] == "HackerNews"
    assert results[0]["score"] == 250


def test_fetch_handles_empty():
    with patch("lib.hackernews.requests.get") as mock_get:
        mock_get.return_value = _mock_response([])
        results = fetch("nothing here")
    assert results == []


def test_fetch_handles_error():
    with patch("lib.hackernews.requests.get", side_effect=Exception("timeout")):
        results = fetch("broken")
    assert results == []
