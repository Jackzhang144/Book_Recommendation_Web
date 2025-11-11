# Book Recommendation Web · API 说明

> English version: [API.en.md](API.en.md)

面向前端 `frontend/` 目录的所有接口均由 Flask 服务（`backend/src/services/api.py`）提供。本文档描述这些接口的用途、参数与典型返回结构，便于联调与自测，并在末尾补充了国际化/部署相关注意事项。

## 0. 基本信息

- **Base URL**：`VITE_API_BASE_URL`，默认 `http://localhost:8000/api`
- **响应格式**：`application/json`
- **统一响应体**：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

| 字段 | 说明 |
| --- | --- |
| `code` | 0 表示成功，其他值表示业务异常 |
| `message` | 友好的提示文案 |
| `data` | 实际业务数据 |

常见错误码：`1` 参数错误、`2` 无数据、`3` 书名歧义、`404` 查无此书、`408` 超时、`500` 服务器错误。

---

## 1. 搜索 / 自动补全

### GET `/books/search`
首页搜索框与自动补全均调用此接口。

| 参数 | 说明 |
| --- | --- |
| `q` *(必填)* | 关键词（书名 / 作者片段） |
| `limit` | 返回条数，默认 10 |

成功示例：

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

## 2. 图书详情

### GET `/books/{book_id}`
详情页顶部卡片。

成功示例：

```json
{
  "code": 0,
  "data": {
    "book": {
      "book_id": "12345",
      "isbn": "0439708184",
      "title": "Harry Potter and the Sorcerer's Stone",
      "author": "J. K. Rowling",
      "year_of_publication": 1998,
      "publisher": "Scholastic",
      "image_url_m": "https://..."
    }
  }
}
```

---

## 3. 推荐接口

### 3.1 GET `/recommendations/by-book`
详情页默认的“相似读物”列表（默认使用 LightGBM）。

| 参数 | 说明 |
| --- | --- |
| `book_id` *(必填)* | 目标书 |
| `k` | 推荐条数，默认 5 |

### 3.2 GET `/recommendations/by-book-and-algorithm`
详情页算法切换使用。

| 参数 | 说明 |
| --- | --- |
| `book_id` *(必填)* | 目标书 |
| `algorithm` | `lightgbm` / `cf_mf` / `din_content`，也支持 `user_cf`、`item_cf`、`deepfm` 等别名 |
| `k` | 推荐条数，默认 5 |

返回示例：

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

### 3.3 GET `/recommendations/by-title`
快速推荐页、首页精选推荐共用接口。

| 参数 | 说明 |
| --- | --- |
| `q` *(必填)* | 书名 |
| `k` | 推荐条数，默认 5 |

若未找到精确匹配，将返回 `code = 3` 并附带 `similar_titles` 供提示。

---

## 4. 系统信息

### GET `/system/algorithms`
用于在前端下拉框展示可选算法。

```json
{
  "code": 0,
  "data": {
    "algorithms": [
      { "id": "lightgbm", "name": "LightGBM Pairwise Similarity" },
      { "id": "cf_mf", "name": "LightFM Collaborative Filtering" },
      { "id": "din_content", "name": "DIN Content Recommendation" },
      { "id": "user_cf", "name": "User-based CF (alias of LightFM)" },
      ...
    ]
  }
}
```

### GET `/health`
部署或监控用，返回当前书籍数量与算法列表：

```json
{
  "code": 0,
  "data": {
    "status": "healthy",
    "total_books": 50000,
    "algorithms": ["lightgbm", "cf_mf", "din_content"]
  }
}
```

---

## 5. 调试提示

- 前端会在 `services/api.js` 中统一处理超时、错误码和取消请求逻辑，同时根据 `BookCard` 的多语言文本（`src/i18n`）展示提示。
- 若后端新增字段，请在 `BookCard` 或各页面中按需展示；旧字段缺失时前端会自动降级显示。
- 所有接口默认 `k=5`，允许前端传入更大的值以展示更多卡片。
- **响应**：`{"code":0,"data":{"status":"healthy"}}`

---

## 5. 数据字段规范

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `book_id` | string | 业务唯一 ID，用于详情/推荐接口 |
| `isbn` | string | 可选，展示用 |
| `title` | string | 图书标题 |
| `author` | string | 作者名称 |
| `publisher` | string | 出版社 |
| `year_of_publication` | int | 出版年份 |
| `image_url_s/m/l` | string | 不同尺寸封面，前端优先 `image_url_m` |
| `score` | float | 推荐算法评分（0~1 或任意数值） |
| `genres` | string[] | 可选，标签展示 |

## 6. 国际化 & 部署补充

- 前端会根据 `localStorage` / 浏览器语言决定 `locale`，但接口层依旧使用一致的字段名称；无需额外提供 `Accept-Language`。
- 如果部署在不同域名，请确认后端开启 CORS 或在前端 `vite.config.js` 配置 `server.proxy`。生产部署模板可参考根目录的 `DEPLOYMENT.md`。
- `GET /health` 可作为发布后的 smoke test，配合 `frontend/src/services/api.js` 的超时设置（默认 10s）能快速定位网络/服务异常。

确保所有接口返回字段名一致，可避免前端再做额外映射。***
