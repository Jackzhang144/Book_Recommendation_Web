"""Global configuration and common paths for the backend."""

from __future__ import annotations

from pathlib import Path

# Base directories ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VISUALIZATION_DIR = PROCESSED_DATA_DIR  # reuse processed dir for artifacts


def ensure_directories() -> None:
    """Create required directories if they don't exist."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    VISUALIZATION_DIR.mkdir(parents=True, exist_ok=True)


# Data cleaning parameters -------------------------------------------------

MIN_VALID_YEAR = 1800
MAX_VALID_YEAR = 2025

# Collaborative filtering thresholds --------------------------------------

CF_MIN_BOOK_RATINGS = 40
CF_MIN_USER_RATINGS = 40

# LightGBM pairwise trainer settings --------------------------------------

LGB_MAX_POSITIVE_PAIRS = 60000
LGB_MAX_BOOKS_PER_USER = 25
LGB_CANDIDATE_POOL_SIZE = 2000
LGB_RANDOM_STATE = 42

# DIN recommender settings -------------------------------------------------

DIN_MAX_USERS = 8000
DIN_MIN_HISTORY_LENGTH = 2
DIN_MAX_HISTORY_LENGTH = 20
DIN_NEGATIVE_SAMPLES = 2
DIN_MAX_TRAINING_SAMPLES = 120000
DIN_BATCH_SIZE = 256
DIN_EPOCHS = 3
DIN_LEARNING_RATE = 1e-3
DIN_EMBED_DIM = 64
DIN_ATTENTION_HIDDEN_UNITS = (80, 40)
DIN_MLP_HIDDEN_UNITS = (128, 64)
DIN_RANDOM_STATE = 42
DIN_MIN_POSITIVE_RATING = 6
DIN_MAX_HISTORIES_PER_ITEM = 24
DIN_SCORE_BATCH_SIZE = 256
DIN_CANDIDATE_POOL_SIZE = 1500

# General defaults ---------------------------------------------------------

DEFAULT_TOP_K = 5
DEFAULT_SEARCH_LIMIT = 10

