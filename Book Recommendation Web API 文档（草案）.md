下面是一份**给前端 / 后端对接用的 REST API 文档草案**，专门围绕你们的 *Book Recommendation* Web 项目来设计的。你可以直接发给后端同学一起改，或按需要删减字段。



------





# **Book Recommendation Web API 文档（草案）**







## **总体说明**





- **Base URL**（由后端确定，比如）

  

  - https://your-domain.com/api

  

- 所有接口返回数据格式：application/json

- 统一返回结构（推荐）：



```json
{
  "code": 0,
  "message": "ok",
  "data": { }
}
```



- code：0 表示成功，非 0 表示错误（如 400/404/500 等逻辑码）
- message：错误信息或提示信息
- data：真正的业务数据





------





## **1. 图书搜索 / 自动补全**







### **1.1 根据关键词搜索图书**





**用途：**



- 前端搜索框输入书名关键词时展示候选列表
- 也可以作为“找一本书并点进去看详情”的入口





**URL**



GET /books/search



**Query 参数**

| **参数名** | **类型** | **必填** | **说明**                         |
| ---------- | -------- | -------- | -------------------------------- |
| q          | string   | 是       | 搜索关键词（书名的一部分）       |
| limit      | int      | 否       | 返回条数，默认 10，最大可设为 50 |

**请求示例**



GET /api/books/search?q=harry potter&limit=5



**成功响应**

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

**可能错误**



- code = 1：参数缺失（如没传 q）
- code = 2：没有搜索到任何图书（data.books 返回空数组）





------





## **2. 图书详情**





**用途：**



- 搜索结果点击某一本书，展示更完整的信息（作者、出版年、出版社、封面图等）





**URL**



GET /books/{book_id}



**Path 参数**

| **参数名** | **类型** | **必填** | **说明**    |
| ---------- | -------- | -------- | ----------- |
| book_id    | string   | 是       | 图书内部 ID |

> book_id 由后端从原始 ISBN 或用户 ID 映射过来，前端只要当成字符串使用即可。



**请求示例**



GET /api/books/12345



**成功响应**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "book": {
      "book_id": "12345",
      "isbn": "0439708184",
      "title": "Harry Potter and the Sorcerer's Stone",
      "author": "J. K. Rowling",
      "year_of_publication": 1998,
      "publisher": "Scholastic",
      "image_url_s": "https://...",
      "image_url_m": "https://...",
      "image_url_l": "https://...",
      "avg_rating": 8.7,
      "num_ratings": 1234,
      "description": "Optional, if backend wants to provide",
      "tags": ["Fantasy", "Magic", "Children"]
    }
  }
}
```

**可能错误**



- code = 404：没有找到该 book_id 对应的图书





------





## **3. 图书推荐（核心功能）**







### **3.1 根据书名关键词获取推荐（简单版）**





**用途：**



- 满足课程要求：**“输入一本书的标题，返回 5 本相似的书”**
- 用户在搜索框输入书名后，点击“推荐相似图书”按钮即可调用





**URL**



GET /recommendations/by-title



**Query 参数**

| **参数名** | **类型** | **必填** | **说明**           |
| ---------- | -------- | -------- | ------------------ |
| q          | string   | 是       | 书名（可模糊匹配） |
| k          | int      | 否       | 推荐数量，默认 5   |

**请求示例**



GET /api/recommendations/by-title?q=Harry%20Potter&k=5



**成功响应**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "query_title": "Harry Potter and the Sorcerer's Stone",
    "query_book": {
      "book_id": "12345",
      "isbn": "0439708184",
      "title": "Harry Potter and the Sorcerer's Stone",
      "author": "J. K. Rowling",
      "image_url_m": "https://..."
    },
    "recommendations": [
      {
        "book_id": "23456",
        "isbn": "0439064872",
        "title": "Harry Potter and the Chamber of Secrets",
        "author": "J. K. Rowling",
        "image_url_m": "https://...",
        "similarity": 0.93
      },
      {
        "book_id": "34567",
        "isbn": "0439139600",
        "title": "Harry Potter and the Prisoner of Azkaban",
        "author": "J. K. Rowling",
        "image_url_m": "https://...",
        "similarity": 0.90
      }
    ]
  }
}
```

**说明**



- query_title：最终后端匹配到的书名（用来做“你正在查看 X 的相似图书”）
- query_book：原始那本书的基本信息，用于页面上显示“你选的是这本书”。
- recommendations：相似图书列表，前端只要拿 title + author + 封面图 做卡片展示即可。
- similarity：相似度分数（0~1），前端可选显示或不显示。





**可能错误**



- code = 3：根据标题 q 无法唯一匹配任何图书
- code = 4：匹配到多本相似书且不确定（这时可考虑让后端返回一个“歧义列表”，前端弹窗让用户选择；如果你们想简化，也可以后端直接选最相似的一本）





------





### **3.2 根据 book_id 获取推荐（进阶版，可选）**





**用途：**



- 当用户已经选定/点击了一本书时，可直接用其 book_id 获取推荐，避免标题歧义。
- 例如：在书籍详情页下方展示“相似图书”。





**URL**



GET /recommendations/by-book



**Query 参数**

| **参数名** | **类型** | **必填** | **说明**         |
| ---------- | -------- | -------- | ---------------- |
| book_id    | string   | 是       | 目标图书 ID      |
| k          | int      | 否       | 推荐数量，默认 5 |

**请求示例**



GET /api/recommendations/by-book?book_id=12345&k=5



**成功响应**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "query_book": {
      "book_id": "12345",
      "isbn": "0439708184",
      "title": "Harry Potter and the Sorcerer's Stone",
      "author": "J. K. Rowling",
      "image_url_m": "https://..."
    },
    "recommendations": [
      {
        "book_id": "23456",
        "isbn": "0439064872",
        "title": "Harry Potter and the Chamber of Secrets",
        "author": "J. K. Rowling",
        "image_url_m": "https://...",
        "similarity": 0.93
      }
    ]
  }
}
```



------





## **4. 推荐算法信息展示（可选，但对报告展示很好用）**





如果你们想在前端展示“本系统用了哪些算法 / 当前推荐是由哪个算法生成的”，可以加一组简单的接口。





### **4.1 获取可用的推荐算法列表**





**URL**



GET /system/algorithms



**用途：**



- 用来在前端页面显示：

  

  - “我们使用了：User-based CF、Item-based CF、LightGBM、BPR 等算法”

  

- 甚至可以做一个“切换算法”的下拉框，看看不同算法推荐出的结果差异（很加分）





**成功响应示例**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "algorithms": [
      {
        "id": "user_cf",
        "name": "User-based Collaborative Filtering",
        "description": "基于用户相似度的协同过滤推荐算法"
      },
      {
        "id": "item_cf",
        "name": "Item-based Collaborative Filtering",
        "description": "基于物品相似度的协同过滤推荐算法"
      },
      {
        "id": "lightgbm",
        "name": "LightGBM Ranking Model",
        "description": "基于 LightGBM 的排序学习模型"
      }
    ]
  }
}
```



### **4.2 按算法获取推荐（进阶可选）**





**URL**



GET /recommendations/by-book-and-algorithm



**用途：**



- 前端提供“算法切换”功能，例如：

  

  - 下拉框选择算法：UserCF / ItemCF / LightGBM
  - 推荐结果随之变化，方便课堂展示不同算法的差异

  





**Query 参数**

| **参数名** | **类型** | **必填** | **说明**                            |
| ---------- | -------- | -------- | ----------------------------------- |
| book_id    | string   | 是       | 目标图书 ID                         |
| algorithm  | string   | 是       | 算法 ID（比如 user_cf, item_cf 等） |
| k          | int      | 否       | 推荐数量，默认 5                    |

**成功响应示例**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "algorithm": {
      "id": "user_cf",
      "name": "User-based Collaborative Filtering"
    },
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
        "score": 0.93
      }
    ]
  }
}
```



------





## **5. 系统状态 / 调试接口（可选）**







### **5.1 健康检查（前端一般用不到，但方便测试）**





**URL**



GET /health



**成功响应示例**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "status": "healthy"
  }
}
```



------





## **6. 错误码约定（建议）**





后端可约定一些基础错误码，前端据此展示不同的提示：

| **code** | **含义**                     | **前端处理建议**                 |
| -------- | ---------------------------- | -------------------------------- |
| 0        | 成功                         | 正常展示数据                     |
| 1        | 参数错误（缺字段、类型错误） | 提示“输入不合法，请检查后重试”   |
| 2        | 无数据（搜索不到 / 无推荐）  | 展示“没有找到相关图书”           |
| 3        | 标题匹配失败或歧义           | 提示用户换一个更精确的书名       |
| 404      | 资源不存在（book_id 不存在） | 展示 404 样式页面或 Toast        |
| 500      | 服务器内部错误               | 提示“服务器开小差了，请稍后再试” |