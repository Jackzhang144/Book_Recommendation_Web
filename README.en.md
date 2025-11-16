# Book Recommendation Web

> 中文版请参见 [README.md](README.md)

An end-to-end book recommendation demo. The frontend (Vue 3 + Vite) walks through “search → detail → algorithm comparison → instant recommendations” with bilingual UI, while the backend covers data exploration, feature engineering, and three recommendation algorithms (LightGBM / LightFM / DIN sequential modeling) exposed through a unified REST API. The visual layer follows the `apps.apple.com` breakdown inside this repo, recreating liquid-glass cards, orbit gradients, and micro-interactions.

---

## 1. Highlights

- **Multi-algorithm comparison** – Toggle among LightGBM ranking, collaborative filtering, and DIN sequential recs directly on the detail page.
- **Live interactions** – Instant search, curated picks, detail recommendations, and a dedicated “Quick Recommend” route for demos.
- **Bilingual experience** – `src/i18n` handles locale detection/persistence plus the `LanguageToggle` UI in the nav.
- **Liquid-glass UI** – SVG `feDisplacementMap` + `backdrop-filter` create the refractive “liquid glass” look across Hero/Section/status cards via a shared `#liquid-glass` filter.
- **Full data pipeline** – `backend/eda/` scripts cover overview, cleansing, feature engineering, and visualization with outputs in `backend/data/processed/`.
- **Clear contracts** – The API matches the spec documented in `frontend/docs/API.*`, so the frontend only needs `VITE_API_BASE_URL`.

---

## 2. Repository Layout

```
frontend/   # Vue 3 + Vite frontend
│
├─ src/
│  ├─ views/              # Home / BookDetail / QuickRecommend
│  ├─ components/         # SearchBar, BookCard, LanguageToggle, etc.
│  ├─ services/api.js     # Fetch wrapper + error handling
│  ├─ i18n/               # Locale state, dictionaries, persistence
│  └─ config/appConfig.js # API host, timeouts, defaults
└─ docs/                  # API & Usage guides

backend/
│
├─ data/
│  ├─ raw/                # Books.csv / Ratings.csv / Users.csv
│  └─ processed/          # Cleaned tables, features, visuals
├─ eda/                   # Scripts for tasks (1)-(2)
├─ src/
│  ├─ data_pipeline.py    # Loading/cleaning logic
│  ├─ book_repository.py  # Query helpers + serialization
│  ├─ recommendation/     # LightGBM / LightFM / DIN Sequential
│  └─ services/api.py     # Flask + Flask-CORS REST API
├─ requirements.txt
└─ tests.py               # HTTP smoke test
```

---

## 3. Quick Start

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# (Optional) regenerate processed data
python eda/dataset_overview.py
python eda/preprocess_books.py
python eda/examine_books.py
python eda/visualize_books.py

# Launch the API (default http://localhost:8000/api)
python -m src.services.api
```

Optionally run `python backend/tests.py` in another terminal for a quick smoke test.

### Frontend

```bash
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:8000/api npm run dev
```

For production builds: `npm run build`. Deploy `dist/` to any static host and remember to set `VITE_API_BASE_URL` in that environment. Detailed deployment recipes (Nginx/Gunicorn/static hosting) live in [DEPLOYMENT.en.md](DEPLOYMENT.en.md).

---

## 4. Pages ↔ API Mapping

| Page/Module | API |
| --- | --- |
| Search bar | `GET /books/search?q=...&limit=...` |
| Featured picks | `GET /recommendations/by-title?q=<title>&k=5` |
| Book detail header | `GET /books/{book_id}` |
| Similar list | `GET /recommendations/by-book?book_id=...` (LightGBM default) |
| Algorithm switcher | `GET /recommendations/by-book-and-algorithm?book_id=...&algorithm=lightgbm/cf_mf/din_content` |
| Quick Recommend | `GET /recommendations/by-title?q=...&k=5` |

All responses follow:

```json
{
  "code": 0,
  "message": "ok",
  "data": { ... }
}
```

---

## 5. Task Coverage

| Task | Description |
| --- | --- |
| (1) Dataset overview | `eda/dataset_overview.py` outputs shape, missing values, info, uniques, comparisons |
| (2) Exploration & preprocessing | `eda/preprocess_books.py`, `eda/examine_books.py`, `eda/visualize_books.py` |
| (3) Algorithm setup | LightGBM / LightFM / DIN sequential models under `backend/src/recommendation/` |
| (4) Recommendation API | Unified `/api/recommendations/*` endpoints with book/title/algorithm variants |
| (5) System demo | `frontend/` delivers the bilingual web demo with liquid-glass UI and LanguageToggle |

---

For more fields, see `frontend/docs/API.en.md`; frontend workflow is documented in `frontend/docs/USAGE.en.md`; deployment notes live in `DEPLOYMENT.en.md`. Contributions that extend algorithms, features, or visuals are always welcome! 
