# Book Recommendation Web · API 文档

> 与前端已经对接的接口说明，覆盖《任务介绍.md》+《Book Recommendation Web API 文档（草案）》中要求的能力。实际字段若与下方不同，请在后端保持兼容或在前端做适配。

## 0. 概览

- **Base URL**：`VITE_API_BASE_URL` 环境变量（默认 `http://localhost:8000/api`，亦可在 `src/config/appConfig.js` 覆盖）
- **数据格式**：`application/json`
- **统一响应结构**：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

| 字段 | 说明 |
| --- | --- |
| `code` | 0 表示成功；非 0 为业务错误，前端会显示 `message` |
| `message` | 人类可读的提示，例如“无推荐结果” |
| `data` | 具体业务数据，结构见下方接口 |

### 错误码建议

| code | 说明 | 前端处理 |
| --- | --- | --- |
| 0 | 成功 | 正常渲染 |
| 1 | 参数缺失/非法 | 提示“输入不合法，请检查后重试” |
| 2 | 无数据 | 展示“没有找到相关图书” |
| 3 | 标题匹配失败或歧义 | 请用户输入更精确的书名 |
| 404 | 资源不存在 | 跳回搜索页 / 显示错误卡片 |
| 408 | 请求超时 | 前端会提示“请求超时，请稍后重试” |
| 500 | 服务器错误 | 提示稍后再试 |

---

## 1. 图书搜索 / 自动补全

### 1.1 GET `/books/search`
- **用途**：首页搜索框、自动补全列表
- **Query 参数**：
  | 名称 | 类型 | 必填 | 说明 |
  | --- | --- | --- | --- |
  | `q` | string | 是 | 书名关键词（大小写不敏感） |
  | `limit` | int | 否 | 返回条数，默认 10，最大 50 |
- **成功响应**：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "books": [
      {
        "book_id": "12345",
        "isbn": "0439708184",
        "title": "Harry Potter and the Sorcerer's Stone",
        "author": "J. K. Rowling",
        "year_of_publication": 1998,
        "publisher": "Scholastic",
        "image_url_s": "https://...",
        "image_url_m": "https://...",
        "image_url_l": "https://..."
      }
    ]
  }
}
```

---

## 2. 图书详情

### 2.1 GET `/books/{book_id}`
- **用途**：详情页顶部信息卡
- **路径参数**：`book_id`（string）
- **成功响应**：

```json
{
  "code": 0,
  "data": {
    "book": {
      "book_id": "12345",
      "title": "Harry Potter and the Sorcerer's Stone",
      "author": "J. K. Rowling",
      "year_of_publication": 1998,
      "publisher": "Scholastic",
      "summary": "...",
      "image_url_l": "https://...",
      "genres": ["Fantasy", "Adventure"]
    }
  }
}
```

> 前端会兜底处理缺失字段，但建议至少返回 `book_id/title/author/image_url_m`。

---

## 3. 图书推荐

### 3.1 GET `/recommendations/by-book`
- **用途**：详情页中的“相似推荐”卡片
- **Query 参数**：
  | 名称 | 类型 | 必填 | 说明 |
  | --- | --- | --- | --- |
  | `book_id` | string | 是 | 目标图书 ID |
  | `k` | int | 否 | 推荐数量，默认 5 |
- **成功响应**：

```json
{
  "code": 0,
  "data": {
    "query_book": { "book_id": "12345", "title": "Harry Potter and the Sorcerer's Stone" },
    "recommendations": [
      {
        "book_id": "23456",
        "title": "Harry Potter and the Chamber of Secrets",
        "author": "J. K. Rowling",
        "image_url_m": "https://...",
        "score": 0.93
      }
    ]
  }
}
```

### 3.2 GET `/recommendations/by-book-and-algorithm`
- **用途**：详情页“算法切换”区块
- **Query 参数**：
  | 名称 | 类型 | 必填 | 说明 |
  | --- | --- | --- | --- |
  | `book_id` | string | 是 | 目标图书 ID |
  | `algorithm` | string | 是 | `lightgbm` / `user_cf` / `item_cf` / `deepfm` 等 |
  | `k` | int | 否 | 推荐数量，默认 5 |
- **成功响应**：

```json
{
  "code": 0,
  "data": {
    "algorithm": {
      "id": "lightgbm",
      "name": "LightGBM Ranker"
    },
    "recommendations": [
      {
        "book_id": "34567",
        "title": "Fantastic Beasts and Where to Find Them",
        "author": "J. K. Rowling",
        "image_url_m": "https://...",
        "score": 0.82
      }
    ]
  }
}
```

### 3.3 GET `/recommendations/by-title`
- **用途**：快速推荐页、首页热门推荐
- **Query 参数**：
  | 名称 | 类型 | 必填 | 说明 |
  | --- | --- | --- | --- |
  | `q` | string | 是 | 原始输入书名 |
  | `k` | int | 否 | 推荐数量，默认 5 |
- **成功响应**：

```json
{
  "code": 0,
  "data": {
    "query_book": {
      "book_id": "12345",
      "title": "Harry Potter and the Sorcerer's Stone",
      "author": "J. K. Rowling",
      "image_url_m": "https://..."
    },
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

---

## 4. 状态接口（可选）

### GET `/health`
- **用途**：部署检测/监控
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

确保所有接口返回字段名一致，可避免前端再做额外映射。
