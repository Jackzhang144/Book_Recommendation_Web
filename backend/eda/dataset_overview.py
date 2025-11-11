"""Generate the dataset summary required by task (1)."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, ensure_directories  # noqa: E402
from src.data_pipeline import clean_books  # noqa: E402


def build_summary(raw_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> dict:
    buffer = io.StringIO()
    raw_df.info(buf=buffer)

    summary = {
        "raw_shape": raw_df.shape,
        "clean_shape": cleaned_df.shape,
        "total_null_values": int(raw_df.isna().sum().sum()),
        "columns_with_null": raw_df.columns[raw_df.isna().any()].tolist(),
        "info": buffer.getvalue(),
        "unique_values": raw_df.nunique().to_dict(),
        "dtypes": raw_df.dtypes.astype(str).to_dict(),
        "comparison_samples": {
            "raw_head_csv": str(PROCESSED_DATA_DIR / "comparison_raw_head.csv"),
            "clean_head_csv": str(PROCESSED_DATA_DIR / "comparison_clean_head.csv"),
        },
    }
    return summary


def main():
    ensure_directories()
    raw_path = RAW_DATA_DIR / "Books.csv"
    raw_df = pd.read_csv(raw_path, low_memory=False)

    cleaned_df = clean_books(raw_df)
    cleaned_path = PROCESSED_DATA_DIR / "cleaned_books.csv"
    cleaned_df.to_csv(cleaned_path, index=False)

    raw_df.head(50).to_csv(PROCESSED_DATA_DIR / "comparison_raw_head.csv", index=False)
    cleaned_df.head(50).to_csv(PROCESSED_DATA_DIR / "comparison_clean_head.csv", index=False)

    summary = build_summary(raw_df, cleaned_df)
    summary_path = PROCESSED_DATA_DIR / "dataset_overview.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Dataset overview written to {summary_path}")


if __name__ == "__main__":
    main()
