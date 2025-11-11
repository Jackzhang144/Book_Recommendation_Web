"""LightFM-based collaborative filtering recommender."""

from __future__ import annotations

from typing import Dict, List

import numpy as np
from lightfm import LightFM
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity

from ...config import CF_MIN_BOOK_RATINGS, CF_MIN_USER_RATINGS
from ...data_pipeline import get_ratings
from .base import AlgorithmInfo, BaseRecommender, RecommendationError


class LightFMCollaborativeRecommender(BaseRecommender):
    info = AlgorithmInfo(
        id="cf_mf",
        name="LightFM Collaborative Filtering",
        description="Matrix factorization (WARP loss) over explicit ratings",
    )

    def __init__(self, book_repo):
        super().__init__(book_repo)
        ratings = get_ratings(filtered=True)
        ratings = ratings[ratings["ISBN"].isin(book_repo.by_isbn.keys())]

        book_counts = ratings["ISBN"].value_counts()
        popular_isbns = book_counts[book_counts >= CF_MIN_BOOK_RATINGS].index
        ratings = ratings[ratings["ISBN"].isin(popular_isbns)]

        user_counts = ratings["User-ID"].value_counts()
        active_users = user_counts[user_counts >= CF_MIN_USER_RATINGS].index
        ratings = ratings[ratings["User-ID"].isin(active_users)]

        if ratings.empty:
            raise RuntimeError("Not enough ratings to train LightFM")

        user_to_index = {uid: idx for idx, uid in enumerate(ratings["User-ID"].unique())}
        isbn_to_index = {isbn: idx for idx, isbn in enumerate(ratings["ISBN"].unique())}

        row = ratings["User-ID"].map(user_to_index)
        col = ratings["ISBN"].map(isbn_to_index)
        data = np.ones(len(ratings), dtype=np.float32)

        interactions = sparse.coo_matrix(
            (data, (row.values, col.values)),
            shape=(len(user_to_index), len(isbn_to_index)),
        )

        model = LightFM(loss="warp", no_components=32, learning_rate=0.05, random_state=42)
        model.fit(interactions, epochs=40, num_threads=4)

        self.model = model
        self.item_embeddings = model.item_embeddings
        self.isbn_to_index = isbn_to_index
        self.index_to_isbn = {idx: isbn for isbn, idx in isbn_to_index.items()}

    def recommend(self, isbn: str, k: int) -> List[Dict]:
        if isbn not in self.isbn_to_index:
            raise RecommendationError("Book not available in MF training set")

        idx = self.isbn_to_index[isbn]
        query_vec = self.item_embeddings[idx].reshape(1, -1)
        sims = cosine_similarity(query_vec, self.item_embeddings).flatten()

        ranking = np.argsort(sims)[::-1]
        results = []
        for candidate_idx in ranking:
            if candidate_idx == idx:
                continue
            candidate_isbn = self.index_to_isbn[candidate_idx]
            payload = self._format_result(candidate_isbn, sims[candidate_idx])
            if payload:
                results.append(payload)
            if len(results) >= k:
                break

        if not results:
            raise RecommendationError("No collaborative filtering matches found")
        return results

