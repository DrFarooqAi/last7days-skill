# Last7Days Skill App — Claude Code Setup
**Author: Dr. Farooq**

## Quick Start

```bash
pip install -r requirements.txt
python scripts/last7days.py "your topic here"
```

## CLI Usage

```bash
# Basic research
python scripts/last7days.py "AI agents"

# Select specific sources
python scripts/last7days.py "rust lang" --sources reddit,hn,github

# Limit results per source
python scripts/last7days.py "openai" --limit 10

# JSON output for piping
python scripts/last7days.py "climate tech" --json > results.json
```

## Web UI

```bash
streamlit run app.py
```

## Project Structure

```
last7days-skill/
├── app.py                  # Streamlit web UI
├── scripts/
│   ├── last7days.py        # CLI entry point
│   └── lib/
│       ├── reddit.py       # Reddit public API
│       ├── hackernews.py   # HN Algolia API
│       ├── github_source.py# GitHub REST API
│       ├── bluesky.py      # Bluesky AT Protocol
│       ├── web_search.py   # DuckDuckGo search
│       └── synthesizer.py  # Clustering engine
└── tests/
```

## Source Details

| Source     | API Endpoint                              | Auth    |
|------------|-------------------------------------------|---------|
| Reddit     | reddit.com/search.json                    | None    |
| HackerNews | hn.algolia.com/api/v1/search              | None    |
| GitHub     | api.github.com/search/repositories        | None    |
| Bluesky    | public.api.bsky.app/xrpc/...searchPosts   | None    |
| Web        | DuckDuckGo (duckduckgo-search lib)        | None    |

## Adding a New Source

1. Create `scripts/lib/mysource.py`
2. Implement `fetch(query: str, limit: int) -> list[dict]`
3. Each dict must have: `title`, `url`, `body`, `score`, `source`, `timestamp`
4. Register it in `SOURCE_MAP` in `scripts/last7days.py` and `app.py`

## Deploy to HuggingFace Spaces

1. Create a new Space (Streamlit type) at huggingface.co/spaces
2. Push this repo to the Space
3. `app.py` is the entry point — Spaces picks it up automatically
