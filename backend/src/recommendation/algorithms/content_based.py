"""TF-IDF content-based recommender (DIN-inspired)."""

from __future__ import annotations

from typing import Dict, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .base import AlgorithmInfo, BaseRecommender, RecommendationError


class TfidfContentRecommender(BaseRecommender):
    """Uses TF-IDF over title/author/publisher tokens to find similar books."""

    info = AlgorithmInfo(
        id="din_content",
        name="DIN Content-based Recommendation",
        description="TF-IDF + cosine similarity over title/author/publisher tokens",
    )

    def __init__(self, book_repo, max_features: int = 6000):
        super().__init__(book_repo)
        df = book_repo.get_dataframe()
        df["combined"] = (
            df["Book-Title"].fillna("")
            + " "
            + df["Book-Author"].fillna("")
            + " "
            + df["Publisher"].fillna("")
        )
        self.df = df
        self.vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=(1, 2), stop_words="english")
        self.feature_matrix = self.vectorizer.fit_transform(df["combined"])
        self.isbn_to_index = {row.ISBN: idx for idx, row in df.reset_index(drop=True).iterrows()}

    def recommend(self, isbn: str, k: int) -> List[Dict]:
        if isbn not in self.isbn_to_index:
            raise RecommendationError("Book not covered by TF-IDF model")

        idx = self.isbn_to_index[isbn]
        target_vector = self.feature_matrix[idx]
        similarities = cosine_similarity(target_vector, self.feature_matrix).flatten()

        similar_indices = np.argsort(similarities)[::-1]
        results = []
        collected = 0
        seen_titles = set()
        for candidate_idx in similar_indices:
            if candidate_idx == idx:
                continue
            candidate_isbn = self.df.iloc[candidate_idx].ISBN
            payload = self._format_result(candidate_isbn, similarities[candidate_idx])
            if payload:
                title_key = payload["title"].strip().lower()
                if title_key in seen_titles:
                    continue
                seen_titles.add(title_key)
                results.append(payload)
                collected += 1
            if collected >= k:
                break
        if not results:
            raise RecommendationError("No TF-IDF matches found")
        return results
