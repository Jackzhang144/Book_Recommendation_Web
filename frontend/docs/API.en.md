# Book Recommendation Web · API Reference

> 中文版请参见 [API.md](API.md)

All frontend calls are served by Flask (`backend/src/services/api.py`). This doc explains each endpoint, parameters, and sample responses so you can self-test quickly.

## 0. Basics

- **Base URL** – `VITE_API_BASE_URL` (default `http://localhost:8000/api`)
- **Content-Type** – `application/json`
- **Envelope**

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

`code=0` means success; common errors include `1` invalid params, `2` no data, `3` ambiguous title, `404` not found, `408` timeout, `500` server error.

---

## 1. Search / Autocomplete

`GET /books/search`

| Param | Description |
| --- | --- |
| `q` *(required)* | Keyword (title/author fragment) |
| `limit` | Max results (default 10) |

Response:

```json
{
  "code": 0,
  "data": {
    "books": [
      {
        "book_id": "12345",
        "isbn": "0439708184",
        "title": "Harry Potter and the Sorcerer's Stone",
        "author": "J. K. Rowling",
        "year_of_publication": 1998,
        "publisher": "Scholastic",
        "image_url_m": "https://..."
      }
    ]
  }
}
```

---

## 2. Book Detail

`GET /books/{book_id}` – feeds the detail header card.

---

## 3. Recommendation APIs

### 3.1 `GET /recommendations/by-book`

Default “Similar titles” list (LightGBM).

| Param | Description |
| --- | --- |
| `book_id` *(required)* | Target book |
| `k` | Count (default 5) |

### 3.2 `GET /recommendations/by-book-and-algorithm`

Used by the algorithm switcher.

| Param | Description |
| --- | --- |
| `book_id` *(required)* | Target book |
| `algorithm` | `lightgbm` / `cf_mf` / `din_content` (+ aliases `user_cf`, `item_cf`, `deepfm`) |
| `k` | Count (default 5) |

Example:

```json
{
  "code": 0,
  "data": {
    "algorithm": { "id": "lightgbm", "name": "LightGBM Pairwise Similarity" },
    "query_book": { "book_id": "12345", "title": "Harry Potter and the Sorcerer's Stone" },
    "recommendations": [
      {
        "book_id": "23456",
        "title": "Harry Potter and the Chamber of Secrets",
        "author": "J. K. Rowling",
        "image_url_m": "https://...",
        "score": 0.91
      }
    ]
  }
}
```

### 3.3 `GET /recommendations/by-title`

Used by the Quick Recommend view and the featured section.

| Param | Description |
| --- | --- |
| `q` *(required)* | Title |
| `k` | Count (default 5) |

Returns `code = 3` with `similar_titles` when no exact match.

---

## 4. System Metadata

- `GET /system/algorithms` – list of algorithm IDs/names for dropdowns.
- `GET /health` – simple heartbeat (status, total books, algorithms).

---

## 5. Debug Tips

- `services/api.js` centralizes timeouts, abort logic, and toast messages (hooked into `BookCard` copy from `src/i18n`).
- When adding new fields, surface them in `BookCard` or page templates; missing fields gracefully degrade.
- Default `k=5`, but you can pass higher numbers if the UI needs more cards.
- `GET /health` doubles as a smoke test post-deploy.

---

## 6. Payload Reference

| Field | Type | Notes |
| --- | --- | --- |
| `book_id` | string | Primary identifier |
| `isbn` | string | Optional display field |
| `title` | string | Book title |
| `author` | string | Author |
| `publisher` | string | Publisher |
| `year_of_publication` | int | Year |
| `image_url_s/m/l` | string | Cover URLs (prefer `image_url_m`) |
| `score` | float | Algorithm score |
| `genres` | string[] | Optional tags |

Internationalization happens entirely on the frontend; the API stays language-agnostic. When hosting under a different domain, enable CORS or reverse proxy through Nginx. And if you rely on the new liquid-glass UI, make sure responses stay fast enough—the refractive cards highlight slow states. 
