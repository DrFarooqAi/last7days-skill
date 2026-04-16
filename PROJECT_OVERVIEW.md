# Last7Days Skill App — Project Overview
**Author: Dr. Farooq**
**Version: 1.0.0**
**Date: April 2026**

---

## What Is This?

Last7Days Skill App is an open-source, AI-assisted research aggregator that searches **5 platforms simultaneously** and returns results filtered to the **last 7 days only**. It clusters findings by theme, ranks them by real human engagement, and presents them in a clean web UI.

Built entirely from scratch by Dr. Farooq as a portfolio project. Zero paid APIs. Zero mandatory configuration. Runs locally or deployed live on Streamlit Cloud.

---

## Live Links

| Resource | URL |
|---|---|
| Live Web App | https://last7days-skill-drfarooq.streamlit.app/ |
| GitHub Repository | https://github.com/DrFarooqAi/last7days-skill |

---

## Unique Qualities

1. **7-day recency filter** — not 30 days, not "recent" — strictly the last 7 days across all sources
2. **5 sources in parallel** — fetches simultaneously using ThreadPoolExecutor, not sequentially
3. **Zero API keys** — all sources use free public APIs or no auth at all
4. **Theme clustering** — groups results by semantic similarity (cosine on token counters), not just source
5. **Cross-platform confidence scoring** — HIGH = same story found on 3+ platforms, MEDIUM = 2, LOW = 1
6. **Engagement normalization** — Reddit upvotes, GitHub stars, HN points, and Bluesky likes are all normalized to 0–100 for fair comparison
7. **Deduplication** — near-identical titles (>85% similarity) are merged, keeping the highest-scored version
8. **Claude Code skill** — includes SKILL.md so it works as a native Claude Code research command
9. **CLI + Web UI** — can be used as a terminal tool or a full browser app
10. **MIT licensed** — fully open source, no tracking, no analytics

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Web UI | Streamlit 1.35+ |
| Web Search | ddgs (DuckDuckGo, no API key) |
| HTTP | requests |
| Parallelism | concurrent.futures.ThreadPoolExecutor |
| Clustering | difflib + collections.Counter (no ML deps) |
| Deployment | Streamlit Community Cloud (free) |
| Version Control | Git + GitHub |

**No heavy dependencies.** No PyTorch, no transformers, no OpenAI SDK required to run.

---

## Sources

| Source | API Used | Auth Required | What You Get |
|---|---|---|---|
| Reddit | reddit.com/search.json | None | Top posts from the last week, sorted by score |
| HackerNews | hn.algolia.com/api/v1/search | None | Stories from last 7 days by points |
| GitHub | api.github.com/search/repositories | None (60 req/hr) | Repos pushed to in last 7 days, sorted by stars |
| Bluesky | public.api.bsky.app/xrpc/...searchPosts | None | Posts sorted by likes |
| Web | DuckDuckGo via ddgs library | None | General web results filtered to recent |

---

## File Structure

```
last7days-skill/
│
├── app.py                      # Streamlit web UI — main entry point for deployment
│
├── scripts/
│   ├── last7days.py            # CLI: python scripts/last7days.py "topic"
│   └── lib/
│       ├── __init__.py         # Package marker
│       ├── reddit.py           # Reddit adapter
│       ├── hackernews.py       # HackerNews Algolia adapter
│       ├── github_source.py    # GitHub REST API adapter
│       ├── bluesky.py          # Bluesky AT Protocol adapter
│       ├── web_search.py       # DuckDuckGo web search adapter
│       └── synthesizer.py      # Core engine: dedup + normalize + cluster + rank
│
├── tests/
│   ├── test_reddit.py          # Reddit adapter unit tests
│   ├── test_hackernews.py      # HN adapter unit tests
│   └── test_synthesizer.py     # Synthesizer pipeline tests
│
├── README.md                   # GitHub portfolio README with badges
├── SKILL.md                    # Claude Code skill specification
├── CLAUDE.md                   # Setup guide for Claude Code users
├── PROJECT_OVERVIEW.md         # This file
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project metadata
└── .gitignore
```

---

## How the Synthesizer Works

The synthesizer (`scripts/lib/synthesizer.py`) is the core intelligence of the app. It runs in 4 stages:

### Stage 1 — Deduplication
Compares every pair of result titles using `difflib.SequenceMatcher`.
If similarity ≥ 85%, the lower-scored duplicate is removed.
Prevents the same story appearing multiple times.

### Stage 2 — Score Normalization
Each source has different score scales (Reddit posts can have 50,000 upvotes, HN posts rarely exceed 1,000).
Scores are normalized to **0–100 per source** so they can be compared fairly.
Formula: `normalized = (raw_score / max_score_in_source) × 100`

### Stage 3 — Clustering
Items are grouped by semantic similarity using cosine similarity on token frequency vectors.
- Text is tokenized (lowercased, stopwords removed)
- Each item becomes a `Counter` of meaningful words
- Items are placed into the first cluster whose centroid exceeds the similarity threshold (0.25)
- No ML libraries needed — pure Python math

### Stage 4 — Ranking
Clusters are sorted by:
1. Number of unique sources (more sources = higher confidence)
2. Total normalized score within the cluster

Each cluster is assigned a confidence level:
- **HIGH** — found on 3 or more platforms
- **MEDIUM** — found on 2 platforms
- **LOW** — single source only

---

## Source Adapter Interface

Every adapter follows the same contract:

```python
def fetch(query: str, limit: int = 20) -> list[dict]:
    ...
```

Each dict in the returned list must contain:

| Field | Type | Description |
|---|---|---|
| title | str | Headline or post title |
| url | str | Direct link to the content |
| body | str | Short excerpt or description |
| score | int | Raw engagement metric (upvotes, stars, etc.) |
| source | str | Source name (e.g. "Reddit") |
| timestamp | int | Unix timestamp (0 if unavailable) |

Any additional fields (subreddit, forks, language, author) are stored in the item's `extra` dict and displayed in the UI metadata row.

---

## CLI Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Basic research
python scripts/last7days.py "AI agents"

# Choose specific sources
python scripts/last7days.py "rust programming" --sources reddit,hn,github

# Limit results per source
python scripts/last7days.py "openai" --limit 10

# JSON output (pipe to other tools)
python scripts/last7days.py "climate tech" --json > results.json
```

---

## Web UI Usage

```bash
# Local
python -m streamlit run app.py

# Or visit live
https://last7days-skill-drfarooq.streamlit.app/
```

---

## How to Add a New Source

1. Create `scripts/lib/mysource.py`
2. Implement `fetch(query, limit) -> list[dict]`
3. Add to `SOURCE_MAP` in both `scripts/last7days.py` and `app.py`
4. Add an emoji to `SOURCE_EMOJI` dict in both files
5. Done — the synthesizer handles it automatically

---

## Deployment (Streamlit Community Cloud)

The app is deployed at **https://last7days-skill-drfarooq.streamlit.app/**

It auto-redeploys every time a push is made to the `main` branch on GitHub.

To redeploy manually: go to share.streamlit.io → your app → **Reboot app**

---

## Known Limitations

| Issue | Status | Notes |
|---|---|---|
| Bluesky returns 0 results | Known | Their public search API is inconsistent |
| High Confidence clusters often 0 | Known | Clustering threshold may need tuning per query |
| GitHub: 60 req/hr unauthenticated | Known | Add `GITHUB_TOKEN` env var to increase to 5,000/hr |
| Web results have no engagement score | By design | DuckDuckGo returns no metrics |

---

## Future Ideas

- Add YouTube source (yt-dlp transcripts)
- Add arXiv source for research paper tracking
- GitHub token support for higher rate limits
- Trend delta: compare this week vs last week
- Export to PDF / Obsidian markdown
- Email digest: scheduled research reports
- HuggingFace Spaces deployment (alternative to Streamlit Cloud)

---

## License

MIT — free to use, modify, and distribute.

---

*Last7Days Skill App — Built by Dr. Farooq*
