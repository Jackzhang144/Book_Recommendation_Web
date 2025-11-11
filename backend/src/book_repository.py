"""Utility class responsible for book lookups and serialization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

from .config import DEFAULT_SEARCH_LIMIT


def _safe_str(value) -> str:
    return value if isinstance(value, str) else ""


@dataclass
class BookRecord:
    book_id: int
    isbn: str
    title: str
    author: str
    publisher: str
    year: Optional[int]
    image_url_s: str
    image_url_m: str
    image_url_l: str

    def to_dict(self) -> Dict:
        return {
            "book_id": str(self.book_id),
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "year_of_publication": self.year,
            "publisher": self.publisher,
            "image_url_s": self.image_url_s,
            "image_url_m": self.image_url_m,
            "image_url_l": self.image_url_l,
        }


class BookRepository:
    """Provides search utilities over the cleaned books dataset."""

    def __init__(self, books_df: pd.DataFrame):
        df = books_df.copy()
        df["title_lower"] = df["Book-Title"].str.lower()
        df["author"] = df["Book-Author"].fillna("Unknown")
        df["publisher"] = df["Publisher"].fillna("Unknown")

        self.df = df
        self.by_id = {}
        for _, row in df.iterrows():
            record = BookRecord(
                book_id=int(row.book_id),
                isbn=row.ISBN,
                title=row["Book-Title"],
                author=row["author"],
                publisher=row["publisher"],
                year=int(row["Year-Of-Publication"]) if not pd.isna(row["Year-Of-Publication"]) else None,
                image_url_s=_safe_str(row.get("Image-URL-S", "")),
                image_url_m=_safe_str(row.get("Image-URL-M", "")),
                image_url_l=_safe_str(row.get("Image-URL-L", "")),
            )
            self.by_id[str(record.book_id)] = record
        self.by_isbn = {record.isbn: record for record in self.by_id.values()}

    def _serialize_rows(self, rows: pd.DataFrame) -> List[Dict]:
        return [self.by_id[str(int(row.book_id))].to_dict() for _, row in rows.iterrows()]

    def search(self, query: str, limit: int = DEFAULT_SEARCH_LIMIT) -> List[Dict]:
        """Case-insensitive substring search."""
        sanitized = query.strip().lower()
        if not sanitized:
            return []
        mask = self.df["title_lower"].str.contains(sanitized, na=False, regex=False)
        rows = self.df[mask].head(limit)
        return self._serialize_rows(rows)

    def get_by_id(self, book_id: str) -> Optional[Dict]:
        record = self.by_id.get(str(book_id))
        return record.to_dict() if record else None

    def get_by_isbn(self, isbn: str) -> Optional[Dict]:
        record = self.by_isbn.get(str(isbn))
        return record.to_dict() if record else None

    def find_exact_by_title(self, title: str) -> Optional[Dict]:
        sanitized = title.strip().lower()
        match = self.df[self.df["title_lower"] == sanitized]
        if match.empty:
            return None
        return self.get_by_id(str(int(match.iloc[0].book_id)))

    def suggest_titles(self, query: str, limit: int = 5) -> List[str]:
        sanitized = query.strip().lower()
        mask = self.df["title_lower"].str.contains(sanitized, na=False, regex=False)
        return self.df[mask]["Book-Title"].head(limit).tolist()

    def iter_books(self) -> List[BookRecord]:
        return list(self.by_id.values())

    def get_dataframe(self) -> pd.DataFrame:
        return self.df.copy()
