"""Data loading and preprocessing utilities shared across the backend."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd

from .config import (
    MAX_VALID_YEAR,
    MIN_VALID_YEAR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    ensure_directories,
)

CLEANED_BOOKS_FILENAME = "cleaned_books.csv"


def _read_csv(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Expected data file is missing: {path}")
    return pd.read_csv(path, **kwargs)


def load_raw_books() -> pd.DataFrame:
    """Load the original Books dataset."""
    return _read_csv(RAW_DATA_DIR / "Books.csv", low_memory=False)


def load_raw_ratings() -> pd.DataFrame:
    """Load the original Ratings dataset."""
    return _read_csv(RAW_DATA_DIR / "Ratings.csv")


def clean_books(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Apply data cleaning rules required by the project rubric."""
    df = raw_df.copy()

    df["Book-Title"] = df["Book-Title"].fillna("").str.strip()
    df["Book-Author"] = df["Book-Author"].fillna("Unknown").str.strip()
    df["Publisher"] = df["Publisher"].fillna("Unknown").str.strip()

    df = df[df["Book-Title"] != ""]
    df = df[df["ISBN"].notna()]

    df["Year-Of-Publication"] = pd.to_numeric(df["Year-Of-Publication"], errors="coerce")
    mask_year = df["Year-Of-Publication"].between(MIN_VALID_YEAR, MAX_VALID_YEAR)
    df = df[mask_year]
    df["Year-Of-Publication"] = df["Year-Of-Publication"].astype(int)

    df = df.drop_duplicates(subset="ISBN").reset_index(drop=True)
    df["book_id"] = df.index.astype(int)

    return df


def get_clean_books() -> pd.DataFrame:
    """Return the cached cleaned dataset, generating it if needed."""
    ensure_directories()
    cleaned_path = PROCESSED_DATA_DIR / CLEANED_BOOKS_FILENAME

    if cleaned_path.exists():
        cleaned_df = pd.read_csv(cleaned_path)
    else:
        cleaned_df = clean_books(load_raw_books())
        cleaned_df.to_csv(cleaned_path, index=False)
    return cleaned_df


def get_ratings(filtered: bool = True) -> pd.DataFrame:
    """Return ratings with optional filtering of implicit feedback."""
    ratings = load_raw_ratings()
    ratings.columns = ["User-ID", "ISBN", "Book-Rating"]
    if filtered:
        ratings = ratings[ratings["Book-Rating"] > 0]
    return ratings


def get_book_rating_stats(ratings: pd.DataFrame) -> pd.DataFrame:
    """Aggregate rating count and average per ISBN."""
    agg = (
        ratings.groupby("ISBN")
        .agg(
            rating_count=("Book-Rating", "count"),
            avg_rating=("Book-Rating", "mean"),
        )
        .reset_index()
    )
    return agg
