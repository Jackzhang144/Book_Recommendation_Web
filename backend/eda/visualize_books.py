"""Create charts for key distributions in the Books dataset."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, ensure_directories  # noqa: E402

plt.rcParams["figure.figsize"] = (12, 7)
plt.rcParams["font.size"] = 11


def save_plot(fig, filename: str):
    output = PROCESSED_DATA_DIR / filename
    fig.tight_layout()
    fig.savefig(output, dpi=300)
    plt.close(fig)
    print(f"Saved plot to {output}")


def plot_books_per_year(df):
    series = (
        df["Year-Of-Publication"]
        .value_counts()
        .sort_index()
        .loc[lambda s: (s.index >= 1900) & (s.index <= 2025)]
    )
    fig, ax = plt.subplots()
    ax.plot(series.index, series.values, color="#2563eb")
    ax.set_title("Books Published Per Year (1900-2025)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.grid(alpha=0.3)
    save_plot(fig, "books_per_year.png")


def plot_top_entities(df, column: str, title: str, filename: str, top_n: int = 20):
    series = df[column].value_counts().head(top_n)
    fig, ax = plt.subplots()
    series.sort_values().plot(kind="barh", ax=ax, color="#9333ea")
    ax.set_title(title)
    ax.set_xlabel("Count")
    save_plot(fig, filename)


def main():
    ensure_directories()
    df = pd.read_csv(RAW_DATA_DIR / "Books.csv", low_memory=False)
    df["Year-Of-Publication"] = pd.to_numeric(df["Year-Of-Publication"], errors="coerce")
    df = df.dropna(subset=["Year-Of-Publication"])
    df["Year-Of-Publication"] = df["Year-Of-Publication"].astype(int)

    plot_books_per_year(df)
    plot_top_entities(df, "Book-Author", "Top Authors by Book Count", "top_authors.png")
    plot_top_entities(df, "Publisher", "Top Publishers by Book Count", "top_publishers.png")


if __name__ == "__main__":
    main()
