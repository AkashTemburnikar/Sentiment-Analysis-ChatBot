from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity

# relative to project root
DATA_DIRNAME = "data/ml-100k"


@dataclass
class DataBundle:
    movies: pd.DataFrame     # movie_id, title, title_norm, title_base, genres_list, genres_str, genre flags
    ratings: pd.DataFrame    # user_id, movie_id, rating
    genres: list[str]
    user_item: np.ndarray    # (n_users x n_items) dense ratings (float32)
    movie_index: pd.Index    # index -> movie_id
    user_index: pd.Index     # index -> user_id


class HybridRecommender:
    """
    MovieLens 100k hybrid recommender:
      • Content-based: title + genres bag-of-words
      • Collaborative: item–item cosine on mean-centered ratings
      • Hybrid score = α * content + (1-α) * collaborative
    """

    def __init__(self, data_root: Path | str = DATA_DIRNAME):
        self.bundle = self._load_movielens(Path(data_root))
        self._build_models()

    # ----------------- DATA -----------------
    def _load_movielens(self, root: Path) -> DataBundle:
        movies_path = root / "u.item"
        ratings_path = root / "u.data"
        genre_path = root / "u.genre"

        if not (movies_path.exists() and ratings_path.exists() and genre_path.exists()):
            raise FileNotFoundError(
                f"Missing MovieLens files in: {root} (need u.item, u.data, u.genre)"
            )

        # genre list
        g = pd.read_csv(
            genre_path, sep="|", header=None, names=["genre", "id"], encoding="latin-1"
        )
        genres = g.dropna()["genre"].tolist()

        # u.item: id|title|release|video|imdb|{19 flags}
        movies_raw = pd.read_csv(
            movies_path, sep="|", header=None, encoding="latin-1", on_bad_lines="skip"
        )
        movies = movies_raw.iloc[:, [0, 1] + list(range(5, 5 + len(genres)))].copy()
        movies.columns = ["movie_id", "title"] + genres
        for col in genres:
            movies[col] = movies[col].fillna(0).astype(int)

        # normalized title fields
        movies["title_norm"] = (
            movies["title"].str.strip().str.lower().str.replace(r"\s+", " ", regex=True)
        )
        movies["title_base"] = (
            movies["title"]
            .str.replace(r"\s*\(\d{4}\)\s*$", "", regex=True)
            .str.strip()
            .str.lower()
        )
        movies["genres_list"] = movies[genres].apply(
            lambda r: [g for g, f in zip(genres, r) if f == 1], axis=1
        )
        movies["genres_str"] = movies["genres_list"].apply(
            lambda xs: " ".join(xs) if xs else "unknown"
        )

        ratings = pd.read_csv(
            ratings_path,
            sep="\t",
            names=["user_id", "movie_id", "rating", "ts"],
        )[["user_id", "movie_id", "rating"]]

        # build dense user-item
        user_index = pd.Index(sorted(ratings.user_id.unique()))
        movie_index = pd.Index(sorted(ratings.movie_id.unique()))
        u_map = {u: i for i, u in enumerate(user_index)}
        i_map = {m: i for i, m in enumerate(movie_index)}

        M = np.zeros((len(user_index), len(movie_index)), dtype=np.float32)
        for _, row in ratings.iterrows():
            M[u_map[row.user_id], i_map[row.movie_id]] = float(row.rating)

        # keep only movies present in ratings
        movies = movies[movies.movie_id.isin(movie_index)].copy()
        movies.index = movies.movie_id.map({m: i for i, m in enumerate(movie_index)})

        return DataBundle(
            movies=movies,
            ratings=ratings,
            genres=genres,
            user_item=M,
            movie_index=movie_index,
            user_index=user_index,
        )

    # ----------------- MODELS -----------------
    def _build_models(self):
        B = self.bundle

        # Content-based features: title_base + genres words (bag-of-words)
        text = (B.movies["title_base"] + " " + B.movies["genres_str"]).values
        vect = CountVectorizer(min_df=2, stop_words="english")
        X = vect.fit_transform(text)  # (n_items x vocab)
        self.content_matrix = normalize(X, norm="l2", axis=1)  # l2 rows

        # Collaborative similarity: item–item cosine on mean-centered ratings
        R = B.user_item.astype(np.float32)
        item_counts = (R > 0).sum(axis=0)
        item_sums = R.sum(axis=0)
        item_means = np.divide(
            item_sums, item_counts, out=np.zeros_like(item_sums), where=item_counts > 0
        )

        # *** FIXED: safe mean-centering with broadcasting ***
        mask = (R > 0)
        R_centered = R - item_means  # broadcast per column
        R_centered[~mask] = 0.0      # keep unrated positions at 0

        self.collab_sim = cosine_similarity(R_centered.T)  # (n_items x n_items)
        np.fill_diagonal(self.collab_sim, 0.0)

    # ----------------- HELPERS -----------------
    def _indices_for_genres(self, genre_filters: list[str] | None) -> np.ndarray:
        if not genre_filters:
            return np.arange(len(self.bundle.movie_index))
        mask = np.zeros(len(self.bundle.movie_index), dtype=bool)
        for g in genre_filters:
            if g in self.bundle.genres:
                mask |= (self.bundle.movies[g] == 1).values
        return np.where(mask)[0]

    # ----------------- PUBLIC API -----------------
    def search_titles(self, text: str, k: int = 20) -> pd.DataFrame:
        """Substring search (case-insensitive) on title fields."""
        if not text:
            return pd.DataFrame(columns=["movie_id", "title"])
        q = text.strip().lower()
        base = self.bundle.movies[self.bundle.movies["title_base"].str.contains(q, na=False)]
        if base.empty:
            base = self.bundle.movies[self.bundle.movies["title_norm"].str.contains(q, na=False)]
        return base[["movie_id", "title"]].head(k).reset_index(drop=True)

    def recommend_from_likes(
        self,
        liked_movie_ids: list[int],
        topk: int = 10,
        alpha_content: float = 0.5,
        genre_filters: list[str] | None = None,
        show_explanations: bool = False,
    ) -> pd.DataFrame:
        """Hybrid recommendations seeded by a set of liked movie IDs."""
        if not liked_movie_ids:
            return pd.DataFrame(columns=["movie_id", "title", "score", "why"])

        B = self.bundle
        idx_map = {m: i for i, m in enumerate(B.movie_index)}
        liked_idx = [idx_map[m] for m in liked_movie_ids if m in idx_map]
        if not liked_idx:
            return pd.DataFrame(columns=["movie_id", "title", "score", "why"])

        C = self.content_matrix
        content_scores = (C @ C[liked_idx].T).toarray().mean(axis=1)
        collab_scores = self.collab_sim[:, liked_idx].mean(axis=1)
        scores = alpha_content * content_scores + (1.0 - alpha_content) * collab_scores

        # never recommend the seeds
        scores[liked_idx] = -np.inf

        # optional genre filter
        keep = self._indices_for_genres(genre_filters)
        mask = np.full(scores.shape, False)
        mask[keep] = True
        scores[~mask] = -np.inf

        # top-k
        k = int(min(topk, len(scores)))
        if k <= 0:
            return pd.DataFrame(columns=["movie_id", "title", "score", "why"])
        top_idx = np.argpartition(-scores, k - 1)[:k]
        top_idx = top_idx[np.argsort(-scores[top_idx])]

        why = [""] * len(top_idx)
        if show_explanations:
            for i, idx in enumerate(top_idx):
                contrib = (C[idx] @ C[liked_idx].T).toarray().ravel()
                best_like = liked_idx[int(np.argmax(contrib))]
                why[i] = f"Because it’s similar to '{B.movies.loc[best_like, 'title']}'."

        return pd.DataFrame(
            {
                "movie_id": B.movie_index[top_idx].to_numpy(),
                "title": B.movies.loc[top_idx, "title"].to_list(),
                "score": scores[top_idx],
                "why": why,
            }
        )

    def recommend_from_title(
        self,
        seed_movie_id: int,
        **kwargs,
    ) -> pd.DataFrame:
        return self.recommend_from_likes([seed_movie_id], **kwargs)

    def recommend_for_user_id(
        self,
        user_id: int,
        threshold_like: float = 4.0,
        **kwargs,
    ) -> pd.DataFrame:
        """Use dataset ratings ≥ threshold_like as implicit likes for the user."""
        B = self.bundle
        if user_id not in set(B.user_index):
            return pd.DataFrame(columns=["movie_id", "title", "score", "why"])
        uidx = int(np.where(B.user_index == user_id)[0][0])
        liked_idx = np.where(B.user_item[uidx] >= threshold_like)[0]
        liked_movie_ids = B.movie_index[liked_idx].tolist()
        return self.recommend_from_likes(liked_movie_ids, **kwargs)