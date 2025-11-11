# Book Recommendation Web · 部署指南

本文面向希望把系统发布到测试 / 生产环境的同学，覆盖后端 API、前端静态资源、环境变量、健康检查与常见拓展。示例默认使用 **Ubuntu 22.04 + systemd + Nginx**；若你选择 Docker/Cloud Run 等平台，可按相同逻辑替换命令。

---

## 1. 前置条件

- Python 3.10+、Node.js 18+、npm 10+
- 服务器开放 80/443（前端）与 8000（API，可通过反向代理隐藏）
- 域名及 HTTPS 证书（推荐使用 Let’s Encrypt）

---

## 2. 环境变量一览

| 组件 | 变量 | 含义 | 默认值 |
| --- | --- | --- | --- |
| 后端 | `API_BASE_URL` | API 根路径（对外） | `/api` |
| 后端 | `HOST` / `PORT` | Flask 监听地址与端口 | `0.0.0.0:8000` |
| 前端 | `VITE_API_BASE_URL` | 指向后端 API（含 `/api` 前缀） | `http://localhost:8000/api` |
| 前端 | `VITE_API_TIMEOUT` | 请求超时（毫秒） | `10000` |
| 前端 | `VITE_SEARCH_LIMIT` | 首页搜索条数 | `12` |
| 前端 | `VITE_SHOWCASE_TITLE` | 精选推荐基准书名 | `Classical Mythology` |
| 前端 | `VITE_DEFAULT_LANG` | 默认语言（`zh` / `en` / 留空自动） | 自动侦测 |

将上述变量写入 `/etc/book-rec/.env` 或 CI/CD 的 Secret 统一管理。

---

## 3. 部署后端 API（Gunicorn + systemd）

```bash
# 1) 创建目录
sudo mkdir -p /srv/book-rec/backend
sudo chown $USER /srv/book-rec/backend

# 2) 同步代码
rsync -av --exclude node_modules --exclude dist ./backend/ /srv/book-rec/backend/

# 3) 安装依赖
cd /srv/book-rec/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 4) 可选：重新生成处理数据
python eda/preprocess_books.py

# 5) 预跑一次服务
API_BASE_URL=/api python -m src.services.api
```

### systemd 单元

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

`/etc/book-rec/backend.env` 示例：

```
API_BASE_URL=/api
PYTHONUNBUFFERED=1
```

启用并查看日志：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now book-rec-backend
sudo journalctl -u book-rec-backend -f
```

---

## 4. 构建与托管前端

```bash
cd frontend
npm ci
VITE_API_BASE_URL=https://book.example.com/api npm run build
```

将 `frontend/dist/` 上传到 `/srv/book-rec/www`. Nginx 配置示例：

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

重载 Nginx：`sudo nginx -t && sudo systemctl reload nginx`

---

## 5. 健康检查与烟囱测试

1. **Backend**：`curl https://book.example.com/api/health`
2. **Search**：`curl 'https://book.example.com/api/books/search?q=harry&limit=1'`
3. **Frontend**：打开页面检查 Network 面板，确认路由 SPA 正常。

建议在 CI/CD 中加入 `backend/tests.py` 与 `npm run build` 以阻断无效发布。

---

## 6. 常见问题

| 问题 | 处理方式 |
| --- | --- |
| CORS 报错 | 确认 Flask 已启用 `Flask-CORS` 并允许前端域名；或通过 Nginx 反代保持同源。 |
| 语言切换不可用 | 检查浏览器是否阻止 `localStorage`，或 `LanguageToggle` 是否被缓存旧资源，可尝试 `npm run build` 重新部署。 |
| 大量 504/超时 | 增大 `VITE_API_TIMEOUT`，或在 Gunicorn `ExecStart` 中调大 `--timeout`，并确认数据库/FS 未阻塞。 |
| 静态资源 404 | Nginx 必须使用 `try_files $uri /index.html` 以支持前端路由。 |

---

更多细节可参考：

- `frontend/docs/API.md` —— 请求/响应定义
- `frontend/docs/USAGE.md` —— 前端开发说明
- `backend/README.md` —— 数据与算法脚本

祝部署顺利 🚀
