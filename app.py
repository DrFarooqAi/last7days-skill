"""
Last7Days Skill App — Streamlit Web UI
Author: Dr. Farooq

Deploy to HuggingFace Spaces:
    streamlit run app.py
"""
import sys
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from lib import reddit, hackernews, github_source, bluesky, web_search
from lib.synthesizer import synthesize, Cluster

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Last7Days Skill App",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SOURCE_MAP = {
    "Reddit": reddit,
    "HackerNews": hackernews,
    "GitHub": github_source,
    "Bluesky": bluesky,
    "Web": web_search,
}

SOURCE_EMOJI = {
    "Reddit": "🟠",
    "HackerNews": "🟡",
    "GitHub": "⚫",
    "Bluesky": "🔵",
    "Web": "🌐",
}

CONFIDENCE_COLOR = {
    "HIGH": "#22c55e",
    "MEDIUM": "#eab308",
    "LOW": "#6b7280",
}

# ── Cyberpunk Styles ──────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Audiowide&display=swap');

    /* ── Global white background ── */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    [data-testid="stHeader"]  { background: #ffffff !important; }
    [data-testid="stSidebar"] { background: #f9fafb !important; }
    section[data-testid="stMain"] > div { background: #ffffff !important; }

    /* inputs */
    input, textarea, [data-baseweb="input"] input {
        background: #f9fafb !important;
        color: #111111 !important;
        border: 1px solid #d1d5db !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* expander */
    [data-testid="stExpander"] {
        background: #f9fafb !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary {
        color: #111111 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }

    /* metrics */
    [data-testid="stMetric"] {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.6rem 1rem;
    }
    [data-testid="stMetricLabel"] { color: #6b7280 !important; font-size: 0.75rem !important; letter-spacing: 0.05em; }
    [data-testid="stMetricValue"] { color: #111111 !important; font-family: 'Audiowide', monospace !important; }

    /* divider */
    hr { border-color: #e5e7eb !important; }

    /* ── Title ── */
    .cp-title {
        font-family: 'Audiowide', monospace;
        font-size: 2rem;
        font-weight: 900;
        color: #111111;
        letter-spacing: 0.04em;
        margin-bottom: 0;
    }
    .cp-name {
        font-family: 'Audiowide', monospace;
        font-size: 0.82rem;
        color: #374151;
        letter-spacing: 0.12em;
        margin-top: 4px;
    }
    .cp-sub {
        font-family: 'Inter', sans-serif;
        color: #6b7280;
        font-size: 0.88rem;
        margin-top: 4px;
    }

    /* ── Cluster card ── */
    .cluster-card {
        font-family: 'Inter', sans-serif;
        border-radius: 8px;
        padding: 0.9rem 1.1rem 0.7rem 1.1rem;
        margin-bottom: 0.7rem;
        border-left: 4px solid #d1d5db;
        background: #f9fafb;
        position: relative;
    }
    .cluster-card.high   { border-left-color: #16a34a; background: #f0fdf4; }
    .cluster-card.medium { border-left-color: #d97706; background: #fffbeb; }
    .cluster-card.low    { border-left-color: #d1d5db; background: #f9fafb; }

    .cluster-header {
        display: flex; align-items: flex-start; gap: 8px;
        margin-bottom: 0.6rem; flex-wrap: wrap;
    }
    .cluster-title {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem; font-weight: 700;
        color: #111111; margin: 0; flex: 1; min-width: 200px;
    }

    /* ── Badges ── */
    .badge {
        display: inline-flex; align-items: center;
        padding: 2px 9px; border-radius: 99px;
        font-size: 0.68rem; font-weight: 700;
        font-family: 'Inter', sans-serif;
        white-space: nowrap; letter-spacing: 0.04em;
    }
    .badge-high   { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
    .badge-medium { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .badge-low    { background: #f3f4f6; color: #6b7280; border: 1px solid #e5e7eb; }
    .badge-source { background: #ede9fe; color: #5b21b6; border: 1px solid #ddd6fe; }

    /* ── Items ── */
    .item-block {
        padding: 0.5rem 0;
        border-bottom: 1px solid #f3f4f6;
    }
    .item-block:last-child { border-bottom: none; }
    .item-title { font-size: 0.9rem; font-weight: 600; }
    .item-title a { color: #1d4ed8; text-decoration: none; }
    .item-title a:hover { text-decoration: underline; }
    .item-body  { font-size: 0.8rem; color: #4b5563; margin: 3px 0 4px 0; line-height: 1.5; }
    .item-meta  { font-size: 0.73rem; color: #9ca3af; }
    .item-meta b { color: #6b7280; }

    /* ── Section label ── */
    .section-label {
        font-family: 'Audiowide', monospace;
        font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
        color: #6b7280; text-transform: uppercase;
        margin: 1.2rem 0 0.6rem 0;
    }

    /* ── Searching label ── */
    .search-status {
        font-family: 'Inter', sans-serif;
        color: #6b7280; font-size: 0.88rem;
    }
    .search-status code {
        color: #111111 !important;
        background: #f3f4f6 !important;
        font-family: monospace !important;
    }

    .footer {
        text-align: center; font-family: 'Inter', sans-serif;
        color: #9ca3af; font-size: 0.75rem; padding-top: 2rem;
        letter-spacing: 0.05em;
    }
    .footer span { color: #374151; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="padding: 0.5rem 0 1rem 0;">
    <div class="cp-title">LAST7DAYS SKILL</div>
    <div class="cp-name">DR. FAROOQ — SUPER SEARCH SKILL</div>
    <div class="cp-sub">Research Reddit · HackerNews · GitHub · Bluesky · Web — last 7 days only</div>
</div>
""", unsafe_allow_html=True)
st.divider()

# ── Controls ──────────────────────────────────────────────────────────────────

col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input(
        "Topic",
        placeholder='e.g. "AI agents", "Rust 2026", "climate tech"',
        label_visibility="collapsed",
    )

with col2:
    search_btn = st.button("🔍 Research", use_container_width=True, type="primary")

with st.expander("⚙️ Sources & Options", expanded=False):
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    use_reddit = sc1.checkbox("🟠 Reddit", value=True)
    use_hn     = sc2.checkbox("🟡 HackerNews", value=True)
    use_github = sc3.checkbox("⚫ GitHub", value=True)
    use_bluesky= sc4.checkbox("🔵 Bluesky", value=True)
    use_web    = sc5.checkbox("🌐 Web", value=True)
    limit = st.slider("Results per source", 5, 25, 15)

selected_sources = {
    "Reddit": use_reddit,
    "HackerNews": use_hn,
    "GitHub": use_github,
    "Bluesky": use_bluesky,
    "Web": use_web,
}
active_sources = [name for name, enabled in selected_sources.items() if enabled]

# ── Research ──────────────────────────────────────────────────────────────────

if search_btn and query.strip():
    st.divider()
    st.markdown(f'<div class="search-status">Searching: <code>{query.strip()}</code> across {len(active_sources)} sources...</div>', unsafe_allow_html=True)

    progress = st.progress(0)
    status_cols = st.columns(len(active_sources))
    source_status = {name: status_cols[i].empty() for i, name in enumerate(active_sources)}

    for name in active_sources:
        source_status[name].markdown(f"{SOURCE_EMOJI.get(name, '•')} **{name}**\n⏳ waiting…")

    all_results = []
    completed = 0

    with ThreadPoolExecutor(max_workers=len(active_sources)) as executor:
        futures = {
            executor.submit(SOURCE_MAP[name].fetch, query.strip(), limit): name
            for name in active_sources
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                results = future.result(timeout=20)
                all_results.extend(results)
                source_status[name].markdown(
                    f"{SOURCE_EMOJI.get(name, '•')} **{name}**\n✅ {len(results)} results"
                )
            except Exception as e:
                source_status[name].markdown(
                    f"{SOURCE_EMOJI.get(name, '•')} **{name}**\n❌ failed"
                )
            completed += 1
            progress.progress(completed / len(active_sources))

    progress.empty()
    st.divider()

    clusters = synthesize(all_results)

    if not clusters:
        st.warning("No results found. Try a different query or enable more sources.")
    else:
        # Stats row
        m1, m2, m3, m4 = st.columns(4)
        high_count   = sum(1 for c in clusters if c.confidence == "HIGH")
        medium_count = sum(1 for c in clusters if c.confidence == "MEDIUM")
        m1.metric("Total Clusters", len(clusters))
        m2.metric("Total Items",    sum(c.item_count for c in clusters))
        m3.metric("High Confidence", high_count)
        m4.metric("Multi-Source",   high_count + medium_count)

        def render_item(item):
            emoji = SOURCE_EMOJI.get(item.source, "•")
            title = item.title[:120] + ("..." if len(item.title) > 120 else "")
            body  = item.body[:180]  + ("..." if len(item.body)  > 180 else "") if item.body else ""

            title_html = (f'<a href="{item.url}" target="_blank">{title}</a>'
                          if item.url else title)

            meta_parts = [f"{emoji} <b>{item.source}</b>"]
            if item.score:
                meta_parts.append(f"Score {item.score:,}")
            if item.extra.get("subreddit"):
                meta_parts.append(item.extra["subreddit"])
            if item.extra.get("comments"):
                meta_parts.append(f"{item.extra['comments']} comments")
            if item.extra.get("language"):
                meta_parts.append(item.extra["language"])
            if item.extra.get("forks"):
                meta_parts.append(f"{item.extra['forks']} forks")
            if item.extra.get("author"):
                meta_parts.append(f"@{item.extra['author']}")

            body_html = f'<div class="item-body">{body}</div>' if body else ""
            meta_html = ' &nbsp;·&nbsp; '.join(meta_parts)

            return (
                f'<div class="item-block">'
                f'  <div class="item-title">{title_html}</div>'
                f'  {body_html}'
                f'  <div class="item-meta">{meta_html}</div>'
                f'</div>'
            )

        def render_cluster(cluster):
            conf   = cluster.confidence.lower()
            cbadge = f'<span class="badge badge-{conf}">{cluster.confidence}</span>'
            sbadges = " ".join(
                f'<span class="badge badge-source">{SOURCE_EMOJI.get(s,"")} {s}</span>'
                for s in cluster.sources
            )
            items_html = "".join(render_item(i) for i in cluster.items)
            count_text = f'<span style="font-size:0.75rem;color:#9ca3af">{cluster.item_count} items</span>'

            return (
                f'<div class="cluster-card {conf}">'
                f'  <div class="cluster-header">'
                f'    <div class="cluster-title">{cluster.title[:100]}</div>'
                f'    {cbadge} {sbadges} {count_text}'
                f'  </div>'
                f'  {items_html}'
                f'</div>'
            )

        # HIGH & MEDIUM — always visible
        top_clusters = [c for c in clusters if c.confidence in ("HIGH", "MEDIUM")]
        low_clusters  = [c for c in clusters if c.confidence == "LOW"]

        if top_clusters:
            st.markdown('<div class="section-label">High-Signal Clusters</div>', unsafe_allow_html=True)
            for cluster in top_clusters:
                st.markdown(render_cluster(cluster), unsafe_allow_html=True)
        else:
            st.info("No multi-source clusters found. Try a broader query or more sources.")

        # LOW — hidden behind toggle
        if low_clusters:
            with st.expander(f"Show {len(low_clusters)} single-source results", expanded=False):
                for cluster in low_clusters:
                    st.markdown(render_cluster(cluster), unsafe_allow_html=True)

elif search_btn and not query.strip():
    st.warning("Please enter a topic to research.")

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    '<div class="footer">[ <span>DR. FAROOQ</span> ] · LAST7DAYS SUPER SEARCH SKILL · MIT</div>',
    unsafe_allow_html=True,
)
