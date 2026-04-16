---
title: Last7Days Skill App
emoji: 🔍
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.35.0"
python_version: "3.11"
app_file: app.py
pinned: false
---

# 🔍 Last7Days Skill App

![Banner](https://raw.githubusercontent.com/DrFarooqAi/last7days-skill/main/assets/banner.png)

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-HuggingFace%20Spaces-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/farooqgenai/last7days-skill)
[![GitHub](https://img.shields.io/badge/GitHub-DrFarooqAi-181717?style=for-the-badge&logo=github)](https://github.com/DrFarooqAi/last7days-skill)

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Sources](https://img.shields.io/badge/Sources-5_Platforms-purple)
![Zero Config](https://img.shields.io/badge/Config-Zero_Required-orange)

> **Research any topic across 5 platforms — filtered to the last 7 days only.**
> No API keys. No signup. Pure signal from real communities.

**Built by Dr. Farooq**

## Demo

<video src="https://raw.githubusercontent.com/DrFarooqAi/last7days-skill/main/assets/demo.mp4" controls width="100%"></video>

---

## What It Does

Last7Days aggregates discussions, repos, and posts from across the internet and ranks them by **actual human engagement** — upvotes, stars, likes — not editorial curation.

| Source | What You Get |
|--------|-------------|
| 🟠 Reddit | Top posts + comments from relevant subreddits |
| 🟡 HackerNews | Stories ranked by points from the last 7 days |
| ⚫ GitHub | Repositories with recent activity, sorted by stars |
| 🔵 Bluesky | Posts ranked by likes from the open social web |
| 🌐 Web | DuckDuckGo results filtered to recent coverage |

Results are automatically **clustered by theme**, **deduplicated**, and **ranked by cross-platform engagement**.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/farooqgenai/last7days-skill
cd last7days-skill

# 2. Install
pip install -r requirements.txt

# 3. Run
python scripts/last7days.py "AI agents"
```

---

## Web UI

```bash
streamlit run app.py
```

Opens a live Streamlit dashboard in your browser. Choose sources, set limits, and explore clustered results visually.

---

## CLI Usage

```bash
# Research a topic (all sources)
python scripts/last7days.py "large language models"

# Select specific sources
python scripts/last7days.py "rust programming" --sources reddit,hn,github

# Limit results per source
python scripts/last7days.py "openai gpt" --limit 10

# Output as JSON
python scripts/last7days.py "climate tech" --json
```

---

## How It Works

```
  Your Query
      │
      ▼
┌─────────────────────────────────────┐
│  Parallel Fetch (60s timeout)       │
│  🟠 Reddit  🟡 HN  ⚫ GitHub        │
│  🔵 Bluesky  🌐 Web                 │
└──────────────┬──────────────────────┘
               │
               ▼
        Deduplicate
    (title similarity > 85%)
               │
               ▼
     Normalize Scores (0–100)
    (per-source, comparable)
               │
               ▼
    Cluster by Theme
  (cosine similarity on tokens)
               │
               ▼
    Rank Clusters
  (multi-source = HIGH confidence)
               │
               ▼
      📊 Output Report
```

---

## Output Example

```
CLUSTER 1  [HIGH]  |  Reddit · HackerNews · GitHub
  OpenAI releases GPT-5.4 mini with 10x cost reduction
  12 items · score 847.3

    ██████████  98.0  [Reddit]   OpenAI just dropped GPT-5.4 mini...
    ████████    81.2  [HN]       GPT-5.4 Mini: Benchmarks and pricing
    ██████      60.4  [GitHub]   openai/openai-python — v2.1.0 release
```

---

## Deploy to HuggingFace Spaces

1. Create a new **Streamlit** Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Push this repo
3. Done — `app.py` is auto-detected as the entry point

---

## License

MIT — free to use, modify, and distribute.

---

*Built by **Dr. Farooq** · Last7Days Skill App*
