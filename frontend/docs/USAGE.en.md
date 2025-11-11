# Book Recommendation Web · Frontend Usage

> 中文版请参见 [USAGE.md](USAGE.md)

## 1. Environment

- Node.js ≥ 18, npm ≥ 10
- Modern browser (Chrome/Edge recommended for devtools)

## 2. Structure

```
frontend/
├─ src/
│  ├─ App.vue                 # Layout + nav
│  ├─ components/             # SearchBar, BookCard, LanguageToggle, etc.
│  ├─ config/appConfig.js     # API host + defaults
│  ├─ i18n/                   # Locale state + dictionaries
│  ├─ services/api.js         # Fetch helpers
│  ├─ views/                  # Home / BookDetail / QuickRecommend
│  └─ style.css               # Global + liquid-glass styles
├─ router/index.js
├─ docs/
└─ package.json
```

## 3. API Config

`.env` / `.env.local`:

```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=10000
VITE_SEARCH_LIMIT=12
VITE_SHOWCASE_TITLE=Harry Potter
VITE_DEFAULT_LANG=en
```

You can also tweak defaults in `src/config/appConfig.js`.

## 4. Dev & Build

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. For production: `npm run build` → deploy `dist/`.

## 5. Routes & APIs

| Page | Route | APIs |
| --- | --- | --- |
| Home | `/` | `GET /books/search`, `GET /recommendations/by-title` |
| Detail | `/books/:bookId` | `GET /books/{id}`, `/recommendations/by-book`, `/recommendations/by-book-and-algorithm` |
| Quick Recommend | `/recommendations/by-title` | `GET /recommendations/by-title` |

`SearchBar` manages input/loading, `BookCard` renders all tiles, `LanguageToggle` relies on `useI18n()`, and `services/api.js` centralizes error handling.

## 6. FAQ

1. **CORS** – Enable it on Flask or proxy via `vite.config.js`.
2. **Field changes** – Patch `services/api.js` once; pages/BookCard consume the normalized data.
3. **New algorithms** – Extend `algorithmOptions` in `BookDetailView.vue` and expose them via `/system/algorithms`.
4. **i18n entries** – Add keys to both `zh` and `en` branches in `src/i18n/index.js`.
5. **Offline demo** – Mock responses inside `services/api.js` or follow the `demoBooks` fallback from Home view.

## 7. Liquid-glass Styling Tips

- `App.vue` injects `<svg class="app-filters">` with the `#liquid-glass` filter (fractal noise → blur → displacement). Keep it in the DOM.
- `.hero`, `.section`, and status blocks apply `filter: url('#liquid-glass')` plus `backdrop-filter` in `src/style.css`. Reuse the same pattern for new cards.
- Provide solid-color fallbacks if your target browsers disable `backdrop-filter`.

See also `docs/API.en.md` for endpoint details and `DEPLOYMENT.en.md` for production notes.
