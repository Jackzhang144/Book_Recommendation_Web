"""Base classes and helpers for recommendation algorithms."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from ...book_repository import BookRepository


@dataclass
class AlgorithmInfo:
    id: str
    name: str
    description: str


class RecommendationError(Exception):
    """Raised when an algorithm cannot produce recommendations."""


class BaseRecommender:
    """Common helper to map algorithm output to book payloads."""

    info: AlgorithmInfo

    def __init__(self, book_repo: BookRepository):
        self.book_repo = book_repo

    def recommend(self, isbn: str, k: int) -> List[Dict]:
        raise NotImplementedError

    def _format_result(self, isbn: str, score: Optional[float]) -> Optional[Dict]:
        book = self.book_repo.get_by_isbn(isbn)
        if not book:
            return None
        payload = book.copy()
        if score is not None:
            payload["score"] = round(float(score), 4)
        return payload

