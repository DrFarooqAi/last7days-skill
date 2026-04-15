# Last7Days Skill App v1.0 — by Dr. Farooq

Research any topic across 5 platforms from the **last 7 days** only.
Sources: Reddit · HackerNews · GitHub · Bluesky · Web
All sources are free and require zero configuration.

## Research Workflow

**Step 1 — Resolve targeting**
Before searching, identify the most relevant communities and handles for the topic:
- Reddit: find the top 2–3 subreddits (e.g. r/MachineLearning, r/programming)
- GitHub: identify key repo names or org names
- Bluesky/Web: identify key hashtags or creator handles

**Step 2 — Generate query plan**
For the topic, produce 1–3 subqueries optimized by intent:
- Breaking news → recency-first query
- Product/tool → name + "review" or "release"
- Comparison → "X vs Y" + use case
- Tutorial/how-to → "how to" + topic

**Step 3 — Execute research**
Run `python scripts/last7days.py "<query>"` with a 60-second timeout.
All 5 sources run in parallel. Results arrive per-source.

**Step 4 — Synthesize**
The synthesizer clusters results by semantic similarity and ranks by multi-source engagement.
Ground your output strictly in what was found — no hallucination.

## Output Format

Group results by **cluster** (cross-platform theme), not by source.
Each cluster shows:
- Title (best item from cluster)
- Confidence: HIGH (3+ sources) / MEDIUM (2 sources) / LOW (1 source)
- Source list
- Top 3 items with engagement scores and URLs

After clusters:
- **Patterns**: what themes appear across multiple clusters
- **Stats box**: count per source, total items, clusters found
- Invite follow-up questions

## Source Weights

Reddit upvotes · HN points · GitHub stars · Bluesky likes — all normalized 0–100.
Multi-source stories rank highest. Web supplements gaps.
Uncertainty tag `[SINGLE SOURCE]` on clusters with only 1 source.

## Query Modes

- **Comparison** ("X vs Y"): single optimized pass covering both + head-to-head
- **Recommendations** ("best X"): extract named items, rank by mention frequency
- **News** ("what happened with X"): recency-sorted, newest first

## Agent Mode

Pass `--json` flag to get structured JSON output for piping into other tools.
