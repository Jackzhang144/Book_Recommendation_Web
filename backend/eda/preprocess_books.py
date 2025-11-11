"""Feature engineering / preprocessing pipeline covering task (2)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
for path in (BACKEND_ROOT, REPO_ROOT):
    if str(path) not in sys.path:
        sys.path.append(str(path))

try:
    from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, ensure_directories  # type: ignore  # noqa: E402
    from src.data_pipeline import clean_books, load_raw_books  # type: ignore  # noqa: E402
except ModuleNotFoundError:  # pragma: no cover
    from backend.src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, ensure_directories  # type: ignore  # noqa: E402
    from backend.src.data_pipeline import clean_books, load_raw_books  # type: ignore  # noqa: E402


def main():
    ensure_directories()
    raw_df = load_raw_books()
    cleaned_df = clean_books(raw_df)

    features = cleaned_df[
        [
            "ISBN",
            "Book-Title",
            "Book-Author",
            "Year-Of-Publication",
            "Publisher",
            "book_id",
        ]
    ].copy()

    categorical_cols = ["Book-Author", "Publisher"]
    encoders = {}
    for column in categorical_cols:
        encoder = LabelEncoder()
        features[f"{column}_encoded"] = encoder.fit_transform(features[column].astype(str))
        encoders[column] = encoder

    scaler = StandardScaler()
    features["year_scaled"] = scaler.fit_transform(features[["Year-Of-Publication"]])

    processed_path = PROCESSED_DATA_DIR / "processed_books.csv"
    features.to_csv(processed_path, index=False)

    print(f"Processed feature table saved to {processed_path}")


if __name__ == "__main__":
    main()
