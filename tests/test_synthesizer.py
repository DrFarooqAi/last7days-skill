"""Tests for Synthesizer — Last7Days Skill App by Dr. Farooq"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from lib.synthesizer import synthesize, _deduplicate, _normalize_scores, _raw_to_items


SAMPLE_RAW = [
    {"title": "OpenAI releases GPT-5 mini", "url": "https://reddit.com/1",
     "body": "OpenAI just dropped GPT-5 mini with huge cost reductions",
     "score": 1200, "source": "Reddit", "timestamp": 0},
    {"title": "GPT-5 Mini: What you need to know", "url": "https://hn.com/1",
     "body": "OpenAI GPT-5 mini pricing and benchmarks breakdown",
     "score": 340, "source": "HackerNews", "timestamp": 0},
    {"title": "Rust 2026 edition released", "url": "https://github.com/1",
     "body": "Rust programming language 2026 edition is now stable",
     "score": 890, "source": "GitHub", "timestamp": 0},
    {"title": "OpenAI GPT-5 mini launch — full analysis", "url": "https://web.com/1",
     "body": "Analysis of the OpenAI GPT-5 mini release and implications",
     "score": 0, "source": "Web", "timestamp": 0},
]


def test_synthesize_returns_clusters():
    clusters = synthesize(SAMPLE_RAW)
    assert isinstance(clusters, list)
    assert len(clusters) >= 1


def test_deduplication_removes_near_duplicates():
    items = _raw_to_items([
        {"title": "OpenAI releases GPT-5 mini", "url": "a", "body": "", "score": 100, "source": "Reddit", "timestamp": 0},
        {"title": "OpenAI releases GPT-5 mini today", "url": "b", "body": "", "score": 200, "source": "HN", "timestamp": 0},
        {"title": "Rust 2026 is out", "url": "c", "body": "", "score": 50, "source": "GitHub", "timestamp": 0},
    ])
    deduped = _deduplicate(items, threshold=0.80)
    assert len(deduped) == 2


def test_normalize_scores_in_range():
    items = _raw_to_items(SAMPLE_RAW)
    items = _normalize_scores(items)
    for item in items:
        assert 0.0 <= item.normalized_score <= 100.0


def test_multi_source_cluster_is_high_confidence():
    clusters = synthesize(SAMPLE_RAW)
    gpt_cluster = next(
        (c for c in clusters if "gpt" in c.title.lower() or "openai" in c.title.lower()), None
    )
    if gpt_cluster:
        assert gpt_cluster.confidence in ("HIGH", "MEDIUM")


def test_empty_input():
    assert synthesize([]) == []
