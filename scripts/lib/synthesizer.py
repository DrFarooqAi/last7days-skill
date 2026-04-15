"""
Synthesizer — Last7Days Skill App
Author: Dr. Farooq

Deduplicates, scores, clusters, and ranks results from all sources.
No ML dependencies — uses difflib + Counter for lightweight clustering.
"""
from __future__ import annotations
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from difflib import SequenceMatcher


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class Item:
    title: str
    url: str
    body: str
    score: int
    source: str
    normalized_score: float = 0.0
    extra: dict = field(default_factory=dict)


@dataclass
class Cluster:
    title: str
    confidence: str          # HIGH / MEDIUM / LOW
    items: list[Item]
    sources: list[str]
    total_score: float = 0.0

    @property
    def item_count(self) -> int:
        return len(self.items)


# ── Helpers ───────────────────────────────────────────────────────────────────

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "has", "have",
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "it", "its", "this", "that", "from", "by", "as", "up", "if",
    "how", "what", "why", "when", "who", "which", "not", "no", "so",
}


def _tokenize(text: str) -> Counter:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return Counter(t for t in tokens if t not in _STOPWORDS and len(t) > 2)


def _similarity(a: str, b: str) -> float:
    """Title-level string similarity using SequenceMatcher."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _cosine(c1: Counter, c2: Counter) -> float:
    """Cosine similarity between two token Counters."""
    if not c1 or not c2:
        return 0.0
    shared = set(c1) & set(c2)
    dot = sum(c1[t] * c2[t] for t in shared)
    mag1 = math.sqrt(sum(v * v for v in c1.values()))
    mag2 = math.sqrt(sum(v * v for v in c2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


# ── Core pipeline ─────────────────────────────────────────────────────────────

def _raw_to_items(raw: list[dict]) -> list[Item]:
    items = []
    for r in raw:
        if not r.get("title"):
            continue
        extra = {k: v for k, v in r.items()
                 if k not in {"title", "url", "body", "score", "source", "timestamp"}}
        items.append(Item(
            title=r["title"].strip(),
            url=r.get("url", ""),
            body=r.get("body", ""),
            score=int(r.get("score", 0)),
            source=r.get("source", "Unknown"),
            extra=extra,
        ))
    return items


def _deduplicate(items: list[Item], threshold: float = 0.85) -> list[Item]:
    kept: list[Item] = []
    for item in items:
        duplicate = False
        for existing in kept:
            if _similarity(item.title, existing.title) >= threshold:
                # Keep higher-scored version
                if item.score > existing.score:
                    kept.remove(existing)
                    kept.append(item)
                duplicate = True
                break
        if not duplicate:
            kept.append(item)
    return kept


def _normalize_scores(items: list[Item]) -> list[Item]:
    """Normalize scores to 0–100 per source to make them comparable."""
    by_source: dict[str, list[Item]] = {}
    for item in items:
        by_source.setdefault(item.source, []).append(item)

    for source_items in by_source.values():
        max_score = max((i.score for i in source_items), default=1) or 1
        for item in source_items:
            item.normalized_score = round((item.score / max_score) * 100, 1)

    return items


def _cluster(items: list[Item], threshold: float = 0.25) -> list[Cluster]:
    """Group items into thematic clusters using cosine similarity on tokens."""
    token_cache = {id(item): _tokenize(item.title + " " + item.body) for item in items}
    clusters: list[list[Item]] = []

    for item in items:
        placed = False
        for cluster in clusters:
            centroid_tokens: Counter = Counter()
            for ci in cluster:
                centroid_tokens.update(token_cache[id(ci)])
            if _cosine(token_cache[id(item)], centroid_tokens) >= threshold:
                cluster.append(item)
                placed = True
                break
        if not placed:
            clusters.append([item])

    result = []
    for group in clusters:
        sources = list(dict.fromkeys(i.source for i in group))
        total = sum(i.normalized_score for i in group)
        n_sources = len(sources)
        confidence = "HIGH" if n_sources >= 3 else "MEDIUM" if n_sources == 2 else "LOW"
        # Cluster title = title of the highest-scored item
        best = max(group, key=lambda i: i.normalized_score)
        result.append(Cluster(
            title=best.title,
            confidence=confidence,
            items=sorted(group, key=lambda i: i.normalized_score, reverse=True),
            sources=sources,
            total_score=round(total, 1),
        ))

    return sorted(result, key=lambda c: (len(c.sources), c.total_score), reverse=True)


# ── Public API ────────────────────────────────────────────────────────────────

def synthesize(raw_results: list[dict]) -> list[Cluster]:
    """
    Full pipeline: raw dicts → deduplicated Items → normalized → clustered.

    Args:
        raw_results: flat list of dicts from all source adapters combined.

    Returns:
        Ranked list of Cluster objects.
    """
    items = _raw_to_items(raw_results)
    items = _deduplicate(items)
    items = _normalize_scores(items)
    return _cluster(items)
