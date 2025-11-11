## Backend Overview

后端负责三个大的板块：数据处理、推荐算法、Web API，并为前端提供稳定的 REST 契约与健康检查。目录结构如下：

| 目录 | 内容 |
| --- | --- |
| `data/raw/` | Book-Crossing 原始数据（Books/Ratings/Users） |
| `data/processed/` | 清洗后的数据集、对比样本、图表、EDA 报告 |
| `eda/` | 任务 (1)-(2) 所需脚本：数据概览、特征工程、可视化 |
| `src/` | 公共数据管线、书目仓储、推荐算法、Flask API |
| `tests.py` | 调用 REST API 的快速巡检脚本（search/recommend/health） |

---

### 1. 准备环境

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

若需重新生成数据成果，可依次执行：

```bash
python eda/dataset_overview.py   # shape / 缺失值 / info / comparison dataset
python eda/preprocess_books.py   # 类别编码 + 标准化特征
python eda/examine_books.py      # 文本形式的分布与缺失值报告
python eda/visualize_books.py    # 年度出版趋势、热门作者/出版社图表
```

---

### 2. 推荐算法

| 算法 ID | 描述 | 主要用途 |
| --- | --- | --- |
| `lightgbm` | 以用户共现的图书对为训练样本，构造作者/出版社/年份/Jaccard/热度等特征，由 LightGBM 计算相似度 | 默认推荐、满足“必须包含 LightGBM”要求 |
| `cf_mf` | 基于 LightFM 的矩阵分解协同过滤，聚焦评分 ≥40 的热门书与活跃用户 | 经典课堂算法 |
| `din_content` | 对标题+作者+出版社做 TF-IDF，再基于余弦距离检索相似书（DIN 思想的内容模型） | 参考算法之一 |

`/api/system/algorithms` 会返回上述算法及别名（`user_cf`、`item_cf`、`deepfm`），前端在切换算法时直接传入 `algorithm` 参数即可，`BookDetailView` 的语言切换对该结构无影响。

---

### 3. API 列表（均为 `http://localhost:8000/api` 前缀，可通过 `BASE_URL` 环境变量自定义）

| Endpoint | 说明 |
| --- | --- |
| `GET /books/search?q=...&limit=...` | 关键词搜索 / 自动补全 |
| `GET /books/{book_id}` | 图书详情 |
| `GET /recommendations/by-title?q=...&k=...` | 输入书名返回 Top-K 相似书 |
| `GET /recommendations/by-book?book_id=...&k=...` | 默认算法（LightGBM）相似书 |
| `GET /recommendations/by-book-and-algorithm?book_id=...&algorithm=...` | 指定算法切换（LightGBM / CF / DIN） |
| `GET /system/algorithms` | 返回可用算法与 alias |
| `GET /health` | 健康检查（包含书籍数量和算法 ID） |

所有接口遵循统一响应结构：`{"code": 0, "message": "ok", "data": {...}}`。与前端的字段对照可以在 `frontend/docs/API.md` 中查看。

---

### 4. 运行 API 与测试

```bash
python -m src.services.api               # 启动 Flask API（默认端口 8000）
python tests.py                          # 可选：对健康检查/搜索/推荐做快速验证
```

启动前确保 `backend/data/raw` 下存在 `Books.csv` 与 `Ratings.csv`；若要重新清洗数据，只需重新运行 EDA 脚本即可。生产部署（Gunicorn + Nginx、Docker 等）详见仓库根目录的 `DEPLOYMENT.md`。***
