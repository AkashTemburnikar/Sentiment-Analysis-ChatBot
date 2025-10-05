# --- ensure project root on sys.path ---
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from typing import List

from src.recommender import HybridRecommender, DATA_DIRNAME

st.set_page_config(
    page_title="CineScope – Human-in-the-Loop Recommender",
    page_icon="🎞️",
    layout="wide",
)

@st.cache_resource(show_spinner=True)
def load_engine(data_dir: Path):
    return HybridRecommender(data_dir)

DATA_DIR = ROOT / DATA_DIRNAME
ENG = load_engine(DATA_DIR)

# ---------- helpers ----------
def genre_multiselect_chips(prefix: str = "") -> List[str]:
    """Render genre checkboxes as chips; prefix ensures unique widget IDs."""
    cols = st.columns(6)
    chosen: List[str] = []
    for i, g in enumerate(ENG.bundle.genres):
        with cols[i % 6]:
            if st.checkbox(g, key=f"{prefix}g_{g}"):
                chosen.append(g)
    return chosen

def render_cards(df: pd.DataFrame, show_explain: bool):
    if df.empty:
        st.info("No results yet. Try adjusting the blend or picking different seeds.")
        return
    for _, row in df.iterrows():
        with st.container(border=True):
            title = row["title"]
            score = float(row["score"])
            st.markdown(f"**{title}**  ·  _match: {score:.3f}_")
            why = row.get("why", "")
            if show_explain and isinstance(why, str) and why:
                with st.expander("Why this?"):
                    st.write(why)

# ---------- top control bar ----------
with st.container():
    c1, c2, c3, c4, c5 = st.columns([1.3, 1.1, 1.1, 1.1, 2.4])
    with c1:
        st.markdown("## 🎞️ CineScope")
        st.caption("Human-in-the-Loop Movie Recommender (MovieLens-100K)")
    with c2:
        top_n = st.slider("Top-N", 5, 50, 10, key="topn")
    with c3:
        alpha = st.slider("Content blend", 0.0, 1.0, 0.50, 0.05,
                          help="0 = Collaborative only, 1 = Content only")
    with c4:
        show_exp = st.toggle("Explanations", value=True)
    with c5:
        st.caption("Data folder")
        st.code(str(DATA_DIR), language="bash")

st.divider()

tab1, tab2, tab3 = st.tabs(["🔎 Discover", "👍 Personalize", "🧪 Explain"])

# -------------------- Discover --------------------
with tab1:
    st.subheader("Find similar films by title")
    q = st.text_input("Type part of a title", value="Toy Story")
    with st.popover("Filter by genres (optional)"):
        st.write("Select one or more genres:")
        genre_filters = genre_multiselect_chips(prefix="disc_")  # <-- unique prefix

    if st.button("Search & Recommend", type="primary"):
        matches = ENG.search_titles(q, k=25)
        if matches.empty:
            st.warning("No matches found. Try a different phrase.")
        else:
            st.caption("Search results")
            st.dataframe(matches, use_container_width=True, hide_index=True)
            seed_id = int(matches.iloc[0]["movie_id"])
            recs = ENG.recommend_from_title(
                seed_movie_id=seed_id,
                topk=top_n,
                alpha_content=alpha,
                genre_filters=genre_filters,
                show_explanations=show_exp,
            )
            st.markdown(f"### Recommendations for **{matches.iloc[0]['title']}**")
            render_cards(recs, show_exp)

# -------------------- Personalize --------------------
with tab2:
    st.subheader("Start from a few titles you already like")
    counts = ENG.bundle.ratings.groupby("movie_id").size().sort_values(ascending=False)
    top_pop_ids = counts.head(250).index.tolist()
    idx_map = {m: i for i, m in enumerate(ENG.bundle.movie_index)}
    top_pop_idx = [idx_map[m] for m in top_pop_ids if m in idx_map]
    pop_df = ENG.bundle.movies.loc[top_pop_idx, ["movie_id", "title"]].reset_index(drop=True)

    chosen = st.multiselect(
        "Choose liked titles (2–10 works well)",
        options=pop_df["title"].tolist(),
        max_selections=10,
    )

    with st.popover("Filter by genres (optional)"):
        st.write("Select one or more genres:")
        genre_filters2 = genre_multiselect_chips(prefix="pers_")  # <-- different prefix

    if st.button("Build my list", type="primary"):
        if not chosen:
            st.info("Pick at least one title.")
        else:
            liked_ids = [int(pop_df.loc[pop_df["title"] == t, "movie_id"].iloc[0]) for t in chosen]
            recs = ENG.recommend_from_likes(
                liked_movie_ids=liked_ids,
                topk=top_n,
                alpha_content=alpha,
                genre_filters=genre_filters2,
                show_explanations=show_exp,
            )
            st.markdown("### Your picks → Our suggestions")
            render_cards(recs, show_exp)

# -------------------- Explain --------------------
with tab3:
    st.subheader("How the system reasons (brief)")
    cA, cB = st.columns([1, 1])
    with cA:
        st.markdown("#### Signals we combine")
        st.markdown(
            """
            - **Content**: tokens from the cleaned title plus genre tags  
            - **Collaborative**: item–item similarity from mean-centered ratings  
            - **Hybrid blend**: `score = α·content + (1−α)·collab`
            """
        )
    with cB:
        st.markdown("#### Human-in-the-loop ideas")
        st.markdown(
            """
            - **Cold-start** defaults: show *popular now* when no history exists.  
            - **You control the blend**: slider reveals how signals change results.  
            - **Genre chips**: lightweight constraints without heavy forms.  
            - **Transparent rationale**: on-demand “why this” per item.  
            - **Gentle proactivity**: occasional, time-bounded nudges (e.g., “New sci-fi arrivals this month”).  
            """
        )
    st.info(
        "Dataset: Kaggle – MovieLens 100K Dataset (u.data, u.item, u.genre in `data/ml-100k/`)."
    )