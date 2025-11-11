"""LightGBM-based pairwise similarity recommender."""

from __future__ import annotations

import random
from itertools import combinations
from typing import Dict, List

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split

from ...config import (
    LGB_CANDIDATE_POOL_SIZE,
    LGB_MAX_BOOKS_PER_USER,
    LGB_MAX_POSITIVE_PAIRS,
    LGB_RANDOM_STATE,
)
from ...data_pipeline import get_book_rating_stats, get_ratings
from .base import AlgorithmInfo, BaseRecommender, RecommendationError


class LightGBMPairwiseRecommender(BaseRecommender):
    info = AlgorithmInfo(
        id="lightgbm",
        name="LightGBM Pairwise Similarity",
        description="Gradient boosting over handcrafted book-pair features",
    )

    def __init__(self, book_repo):
        super().__init__(book_repo)
        ratings = get_ratings(filtered=True)
        ratings = ratings[ratings["ISBN"].isin(book_repo.by_isbn.keys())]

        if ratings.empty:
            raise RuntimeError("Ratings dataset is empty after filtering")

        stats = get_book_rating_stats(ratings)
        books_df = book_repo.get_dataframe().merge(stats, on="ISBN", how="left")
        books_df["rating_count"] = books_df["rating_count"].fillna(0)
        books_df["avg_rating"] = books_df["avg_rating"].fillna(0)
        books_df["clean_author"] = books_df["Book-Author"].fillna("unknown").str.lower()
        books_df["clean_publisher"] = books_df["Publisher"].fillna("unknown").str.lower()
        books_df["clean_title"] = books_df["Book-Title"].str.lower()
        books_df["title_tokens"] = books_df["clean_title"].apply(self._tokenize)

        author_popularity = (
            books_df.groupby("clean_author")["rating_count"].sum().to_dict()
        )

        self.book_meta: Dict[str, Dict] = {}
        for _, row in books_df.iterrows():
            # Keep column names with dashes (e.g. Year-Of-Publication) accessible without relying on itertuples renaming.
            year_value = row.get("Year-Of-Publication")
            year_numeric = int(year_value) if pd.notna(year_value) else None
            isbn = row["ISBN"]
            clean_author = row["clean_author"]
            clean_publisher = row["clean_publisher"]
            self.book_meta[isbn] = {
                "isbn": isbn,
                "book_id": str(int(row["book_id"])),
                "author": clean_author,
                "publisher": clean_publisher,
                "year": year_numeric,
                "tokens": row["title_tokens"],
                "rating_count": float(row["rating_count"]),
                "avg_rating": float(row["avg_rating"]),
                "author_popularity": float(author_popularity.get(clean_author, 0)),
            }

        stats_sorted = stats.sort_values(by="rating_count", ascending=False)
        self.candidate_isbns = [
            isbn for isbn in stats_sorted.ISBN.tolist() if isbn in self.book_meta
        ][:LGB_CANDIDATE_POOL_SIZE]

        self.feature_columns = [
            "same_author",
            "same_publisher",
            "year_diff",
            "title_jaccard",
            "rating_count_diff",
            "avg_rating_diff",
            "author_popularity_diff",
            "popularity_mean",
            "year_mean",
        ]

        X, y = self._build_training_pairs(ratings)
        if X.empty:
            raise RuntimeError("Failed to create training data for LightGBM recommender")

        X_train, X_valid, y_train, y_valid = train_test_split(
            X, y, test_size=0.2, random_state=LGB_RANDOM_STATE, stratify=y
        )

        self.model = LGBMClassifier(
            objective="binary",
            learning_rate=0.08,
            n_estimators=400,
            num_leaves=63,
            subsample=0.8,
            colsample_bytree=0.9,
            random_state=LGB_RANDOM_STATE,
        )
        self.model.fit(
            X_train,
            y_train,
            eval_set=[(X_valid, y_valid)],
            eval_metric="auc",
        )

    @staticmethod
    def _tokenize(text: str) -> frozenset:
        tokens = [token for token in text.split() if token]
        return frozenset(tokens)

    def _pair_features(self, isbn_a: str, isbn_b: str) -> Dict[str, float]:
        meta_a = self.book_meta.get(isbn_a)
        meta_b = self.book_meta.get(isbn_b)
        if not meta_a or not meta_b:
            return {}

        year_a = meta_a["year"]
        year_b = meta_b["year"]
        year_diff = abs(year_a - year_b) if year_a and year_b else 0
        year_mean = np.mean([val for val in [year_a, year_b] if val]) if year_a or year_b else 0

        tokens_a = meta_a["tokens"]
        tokens_b = meta_b["tokens"]
        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b) or 1
        jaccard = intersection / union

        features = {
            "same_author": float(meta_a["author"] == meta_b["author"]),
            "same_publisher": float(meta_a["publisher"] == meta_b["publisher"]),
            "year_diff": float(year_diff),
            "title_jaccard": float(jaccard),
            "rating_count_diff": abs(meta_a["rating_count"] - meta_b["rating_count"]),
            "avg_rating_diff": abs(meta_a["avg_rating"] - meta_b["avg_rating"]),
            "author_popularity_diff": abs(
                meta_a["author_popularity"] - meta_b["author_popularity"]
            ),
            "popularity_mean": (meta_a["rating_count"] + meta_b["rating_count"]) / 2.0,
            "year_mean": float(year_mean),
        }
        return features

    def _build_training_pairs(self, ratings: pd.DataFrame):
        rng = random.Random(LGB_RANDOM_STATE)
        records: List[Dict[str, float]] = []
        labels: List[int] = []

        for _, group in ratings.groupby("User-ID"):
            user_books = [isbn for isbn in group["ISBN"].unique() if isbn in self.candidate_isbns]
            if len(user_books) < 2:
                continue
            user_books = user_books[:LGB_MAX_BOOKS_PER_USER]
            for isbn_a, isbn_b in combinations(user_books, 2):
                feats = self._pair_features(isbn_a, isbn_b)
                if feats:
                    records.append(feats)
                    labels.append(1)
                negative = rng.choice(self.candidate_isbns)
                attempts = 0
                while negative in user_books and attempts < 5:
                    negative = rng.choice(self.candidate_isbns)
                    attempts += 1
                feats_neg = self._pair_features(isbn_a, negative)
                if feats_neg:
                    records.append(feats_neg)
                    labels.append(0)
                if len(records) >= LGB_MAX_POSITIVE_PAIRS:
                    break
            if len(records) >= LGB_MAX_POSITIVE_PAIRS:
                break

        X = pd.DataFrame(records).reindex(columns=self.feature_columns)
        y = pd.Series(labels, name="label")
        return X, y

    def recommend(self, isbn: str, k: int) -> List[Dict]:
        if isbn not in self.book_meta:
            raise RecommendationError("Book not available for LightGBM scoring")

        candidates = [cand for cand in self.candidate_isbns if cand != isbn]
        feature_rows = []
        candidate_ids = []
        for candidate in candidates:
            feats = self._pair_features(isbn, candidate)
            if feats:
                feature_rows.append(feats)
                candidate_ids.append(candidate)
        if not feature_rows:
            raise RecommendationError("No LightGBM candidates available")

        feature_df = pd.DataFrame(feature_rows).reindex(columns=self.feature_columns)
        scores = self.model.predict_proba(feature_df)[:, 1]

        ranking = np.argsort(scores)[::-1][:k]
        results = []
        for idx in ranking:
            payload = self._format_result(candidate_ids[idx], scores[idx])
            if payload:
                results.append(payload)
        if not results:
            raise RecommendationError("LightGBM returned empty results")
        return results
