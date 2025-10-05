from difflib import get_close_matches
import re
import pandas as pd

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def _strip_year(s: str) -> str:
    return re.sub(r"\s*\(\d{4}\)\s*$", "", s).strip()

def resolve_title_to_id(movies_df: pd.DataFrame, user_text: str):
    """
    Resolve free-form title (partial or full) to movie_id.
    Order: exact → exact(no-year) → startswith → contains → fuzzy
    """
    if not user_text:
        return None
    q = _norm(user_text)
    q_base = _norm(_strip_year(user_text))

    exact = movies_df[movies_df["title_norm"] == q]
    if not exact.empty:
        return int(exact.iloc[0]["movie_id"])

    base = movies_df[movies_df["title_base"] == q_base]
    if not base.empty:
        return int(base.iloc[0]["movie_id"])

    starts = movies_df[movies_df["title_base"].str.startswith(q_base)]
    if not starts.empty:
        return int(starts.iloc[0]["movie_id"])

    contains = movies_df[movies_df["title_base"].str.contains(re.escape(q_base), na=False)]
    if not contains.empty:
        return int(contains.iloc[0]["movie_id"])

    # fuzzy
    choices = movies_df["title_base"].tolist()
    match = get_close_matches(q_base, choices, n=1, cutoff=0.6)
    if match:
        cand = movies_df[movies_df["title_base"] == match[0]]
        if not cand.empty:
            return int(cand.iloc[0]["movie_id"])
    return None