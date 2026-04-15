#!/usr/bin/env python3
"""
Last7Days Skill App — CLI
Author: Dr. Farooq

Usage:
    python scripts/last7days.py "AI agents"
    python scripts/last7days.py "openai" --sources reddit,hn,github
    python scripts/last7days.py "rust lang" --limit 10 --json
"""
import argparse
import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from lib import reddit, hackernews, github_source, bluesky, web_search
from lib.synthesizer import synthesize, Cluster

SOURCE_MAP = {
    "reddit": reddit,
    "hn": hackernews,
    "github": github_source,
    "bluesky": bluesky,
    "web": web_search,
}

SOURCE_EMOJI = {
    "reddit": "[R]",
    "hn": "[HN]",
    "github": "[GH]",
    "bluesky": "[BS]",
    "web": "[W]",
}

CONFIDENCE_COLOR = {
    "HIGH": "\033[92m",   # green
    "MEDIUM": "\033[93m", # yellow
    "LOW": "\033[90m",    # grey
}
RESET = "\033[0m"


def run_sources(query: str, sources: list[str], limit: int) -> list[dict]:
    """Fetch from all selected sources in parallel."""
    all_results = []
    with ThreadPoolExecutor(max_workers=len(sources)) as executor:
        futures = {
            executor.submit(SOURCE_MAP[s].fetch, query, limit): s
            for s in sources
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                results = future.result(timeout=15)
                print(f"  {SOURCE_EMOJI.get(name, '•')} {name.upper():10} {len(results)} results")
                all_results.extend(results)
            except Exception as e:
                print(f"  [FAIL] {name.upper():10} failed ({e})")
    return all_results


def print_clusters(clusters: list[Cluster]) -> None:
    if not clusters:
        print("\nNo results found.")
        return

    SEP = "-" * 60
    print(f"\n{SEP}")
    print(f"  {'LAST7DAYS SKILL APP':^40}  by Dr. Farooq")
    print(f"{SEP}\n")

    for i, cluster in enumerate(clusters, 1):
        color = CONFIDENCE_COLOR.get(cluster.confidence, "")
        sources_str = " | ".join(cluster.sources)
        print(f"CLUSTER {i}  {color}[{cluster.confidence}]{RESET}  |  {sources_str}")
        print(f"  {cluster.title}")
        print(f"  {cluster.item_count} items | score {cluster.total_score}")
        print()
        for item in cluster.items[:3]:
            bar = "#" * max(1, int(item.normalized_score / 10))
            print(f"    {bar:<10} {item.normalized_score:5.1f}  [{item.source}]  {item.title[:70]}")
            if item.url:
                print(f"              {item.url}")
        print()

    print(f"{SEP}")
    print(f"  {len(clusters)} clusters from {sum(c.item_count for c in clusters)} items")
    print(f"{SEP}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Last7Days Skill App — by Dr. Farooq\nResearch any topic across 5 platforms in the last 7 days.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("query", help="Topic to research")
    parser.add_argument(
        "--sources",
        default="reddit,hn,github,bluesky,web",
        help="Comma-separated sources (default: all)",
    )
    parser.add_argument("--limit", type=int, default=20, help="Results per source (default: 20)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON clusters")
    args = parser.parse_args()

    sources = [s.strip() for s in args.sources.split(",") if s.strip() in SOURCE_MAP]
    if not sources:
        print("No valid sources specified. Choose from: " + ", ".join(SOURCE_MAP))
        sys.exit(1)

    print(f"\n[*] Researching: \"{args.query}\"")
    print(f"    Sources: {', '.join(sources)}\n")

    raw = run_sources(args.query, sources, args.limit)
    clusters = synthesize(raw)

    if args.json:
        output = [
            {
                "title": c.title,
                "confidence": c.confidence,
                "sources": c.sources,
                "total_score": c.total_score,
                "items": [
                    {"title": i.title, "url": i.url, "source": i.source, "score": i.normalized_score}
                    for i in c.items
                ],
            }
            for c in clusters
        ]
        print(json.dumps(output, indent=2))
    else:
        print_clusters(clusters)


if __name__ == "__main__":
    main()
