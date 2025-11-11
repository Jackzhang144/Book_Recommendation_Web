# Book Recommendation Web · Deployment Guide

> 中文版请参见 [DEPLOYMENT.md](DEPLOYMENT.md)

This guide targets teams shipping the project to staging/production. Examples assume **Ubuntu 22.04 + systemd + Nginx**; feel free to swap in Docker/Cloud Run/etc. as long as you keep the same environment variables and service layout.

---

## 1. Prerequisites

- Python 3.10+, Node.js 18+, npm 10+
- Open ports 80/443 (frontend) and 8000 (API; can be hidden behind reverse proxy)
- A domain + HTTPS certificate (Let’s Encrypt recommended)

---

## 2. Environment Variables

| Component | Variable | Meaning | Default |
| --- | --- | --- | --- |
| Backend | `API_BASE_URL` | Public API prefix | `/api` |
| Backend | `HOST` / `PORT` | Flask bind host/port | `0.0.0.0:8000` |
| Frontend | `VITE_API_BASE_URL` | Full API URL (incl. `/api`) | `http://localhost:8000/api` |
| Frontend | `VITE_API_TIMEOUT` | Request timeout (ms) | `10000` |
| Frontend | `VITE_SEARCH_LIMIT` | Home search limit | `12` |
| Frontend | `VITE_SHOWCASE_TITLE` | Featured baseline title | `Classical Mythology` |
| Frontend | `VITE_DEFAULT_LANG` | Default locale (`zh` / `en` / auto) | Auto detect |

Store them in `/etc/book-rec/*.env` or CI/CD secrets.

---

## 3. Backend (Gunicorn + systemd)

```bash
sudo mkdir -p /srv/book-rec/backend
sudo chown $USER /srv/book-rec/backend
rsync -av --exclude node_modules --exclude dist ./backend/ /srv/book-rec/backend/

cd /srv/book-rec/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# optional data refresh
python eda/preprocess_books.py

# quick sanity run
API_BASE_URL=/api python -m src.services.api
```

### systemd unit

`/etc/systemd/system/book-rec-backend.service`

```
[Unit]
Description=Book Recommendation API
After=network.target

[Service]
Type=simple
EnvironmentFile=/etc/book-rec/backend.env
WorkingDirectory=/srv/book-rec/backend
ExecStart=/srv/book-rec/backend/.venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 src.services.api:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

`/etc/book-rec/backend.env`

```
API_BASE_URL=/api
PYTHONUNBUFFERED=1
```

```
sudo systemctl daemon-reload
sudo systemctl enable --now book-rec-backend
sudo journalctl -u book-rec-backend -f
```

---

## 4. Frontend Build & Hosting

```bash
cd frontend
npm ci
VITE_API_BASE_URL=https://book.example.com/api npm run build
```

Upload `frontend/dist/` to `/srv/book-rec/www`. The liquid-glass UI depends on the `#liquid-glass` SVG filter injected in `App.vue`, so make sure your HTML minifier or templating step does not strip the `<svg class="app-filters">` block. Sample Nginx config:

```
server {
    server_name book.example.com;

    root /srv/book-rec/www;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        try_files $uri /index.html;
    }
}
```

Reload Nginx: `sudo nginx -t && sudo systemctl reload nginx`

---

## 5. Health & Smoke Tests

1. **Backend** – `curl https://book.example.com/api/health`
2. **Search** – `curl 'https://book.example.com/api/books/search?q=harry&limit=1'`
3. **Frontend** – Open the site and inspect Network tab for SPA routes.

Include `backend/tests.py` and `npm run build` in CI/CD to block bad releases.

---

## 6. FAQ

| Issue | Fix |
| --- | --- |
| CORS errors | Enable `Flask-CORS` or keep frontend+API under one domain via reverse proxy. |
| Language toggle not working | Ensure `localStorage` is allowed; redeploy to bust cached assets. |
| 504 / timeouts | Increase `VITE_API_TIMEOUT` or Gunicorn `--timeout`, and profile DB/FS bottlenecks. |
| Static 404 | Remember `try_files $uri /index.html` for SPA routing. |

References:

- `frontend/docs/API.en.md`
- `frontend/docs/USAGE.en.md`
- `backend/README.md`

Happy shipping! 🚀
