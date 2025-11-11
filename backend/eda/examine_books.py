"""Generate textual EDA report."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, ensure_directories  # noqa: E402


def main():
    ensure_directories()
    raw_path = RAW_DATA_DIR / "Books.csv"
    df = pd.read_csv(raw_path, low_memory=False)

    buffer = io.StringIO()
    buffer.write("=== Basic Info ===\n")
    df.info(buf=buffer)
    buffer.write("\n=== Missing Values ===\n")
    buffer.write(df.isna().sum().to_string())
    buffer.write("\n\n=== Year Distribution (Top 10) ===\n")
    buffer.write(df["Year-Of-Publication"].value_counts().head(10).to_string())
    buffer.write("\n\n=== Author Distribution (Top 10) ===\n")
    buffer.write(df["Book-Author"].value_counts().head(10).to_string())
    buffer.write("\n\n=== Publisher Distribution (Top 10) ===\n")
    buffer.write(df["Publisher"].value_counts().head(10).to_string())

    report_path = PROCESSED_DATA_DIR / "eda_text_report.txt"
    report_path.write_text(buffer.getvalue())
    print(f"EDA report written to {report_path}")


if __name__ == "__main__":
    main()
