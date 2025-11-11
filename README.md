# Book Recommendation Web

> English version available in [README.en.md](README.en.md)

一个端到端的图书推荐 Demo：前端基于 Vue 3 + Vite 呈现“搜索—详情—算法切换—快速推荐”全流程，并内置中英文双语 UI；后端提供数据探索、特征处理、三种推荐算法（LightGBM / LightFM / DIN 风格 TF-IDF）及统一 REST API。团队可参考 `apps.apple.com/` 目录中的 Apple App Store UI 拆解文档，复刻或延展更精致的界面与动效。

---

## 1. 项目亮点

- **多算法对比**：LightGBM 排序、矩阵分解协同过滤、内容相似推荐均可在详情页切换查看，满足课程对算法多样性的要求。
- **实时交互**：前端首页支持联想搜索与精选推荐，详情页展示默认推荐 + 算法切换，快速推荐页用于答辩时即输即出。
- **多语言体验**：`src/i18n` 提供轻量国际化，默认跟随浏览器/LocalStorage 切换中英，对应的切换入口位于导航栏 `LanguageToggle`。
- **液态玻璃 UI**：前端通过 SVG `feDisplacementMap` + `backdrop-filter` 叠加实现“液态玻璃”折射效果，Hero、Section、状态提示等组件共享 `#liquid-glass` 滤镜，重现 apps.apple.com 的沉浸式观感。
- **完整数据流程**：`backend/eda/` 提供数据概览、清洗、特征工程、可视化脚本，所有产物统一放在 `backend/data/processed/` 方便复现。
- **接口契约清晰**：API 与《Book Recommendation Web API 文档（草案）》保持一致，前端只需配置 `VITE_API_BASE_URL` 即可对接。

---

## 2. 目录总览

```
frontend/   # Vue 3 + Vite 前端
│
├─ src/
│  ├─ views/              # Home / BookDetail / QuickRecommend
│  ├─ components/         # SearchBar、BookCard 等复用组件
│  ├─ services/api.js     # 统一请求封装与错误处理
│  ├─ i18n/               # 语言状态、文案词典、LanguageToggle 使用的 composable
│  └─ config/appConfig.js # API 地址、超时、默认参数
└─ docs/                  # API 与使用说明

backend/
│
├─ data/
│  ├─ raw/                # 原始 Books.csv / Ratings.csv / Users.csv
│  └─ processed/          # 清洗结果、特征表、可视化、EDA 报告
├─ eda/                   # 覆盖任务 (1)-(2) 的脚本
├─ src/
│  ├─ data_pipeline.py    # 数据加载/清洗逻辑
│  ├─ book_repository.py  # 书目查询、序列化
│  ├─ recommendation/     # LightGBM / LightFM / DIN(TF-IDF)
│  └─ services/api.py     # Flask + Flask-CORS REST API
├─ requirements.txt
└─ tests.py               # HTTP smoke test
```

---

## 3. 快速启动

### 后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 生成/更新数据产物（可选）
python eda/dataset_overview.py
python eda/preprocess_books.py
python eda/examine_books.py
python eda/visualize_books.py

# 启动 API（默认 http://localhost:8000/api）
python -m src.services.api
```

可选：另开终端运行 `python backend/tests.py` 对 API 做一次简单巡检。

### 前端

```bash
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:8000/api npm run dev
```

生产构建：`npm run build`，生成的 `dist/` 可部署到任意静态托管，部署环境同样设置 `VITE_API_BASE_URL`。详尽的部署实践（含 Nginx/Gunicorn/静态托管示例）见新增的 [DEPLOYMENT.md](DEPLOYMENT.md)。

---

## 4. 主要页面与接口映射

| 页面/模块 | 使用的 API |
| --- | --- |
| 首页搜索框 | `GET /books/search?q=...&limit=...` |
| 精选推荐 | `GET /recommendations/by-title?q=<配置书名>&k=5` |
| 图书详情顶部 | `GET /books/{book_id}` |
| 相似推荐区块 | `GET /recommendations/by-book?book_id=...`（默认 LightGBM） |
| 算法切换 | `GET /recommendations/by-book-and-algorithm?book_id=...&algorithm=lightgbm/cf_mf/din_content`（支持 `user_cf/item_cf/deepfm` alias） |
| 快速推荐页 | `GET /recommendations/by-title?q=...&k=5` |

所有响应均遵循统一结构：

```json
{
  "code": 0,
  "message": "ok",
  "data": { ... }
}
```

---

## 5. 任务对照

| 任务 | 说明 |
| --- | --- |
| (1) 数据集信息提取 | `eda/dataset_overview.py` 输出 shape、缺失值、info、unique、comparison dataset |
| (2) 数据探索与预处理 | `eda/preprocess_books.py`、`eda/examine_books.py`、`eda/visualize_books.py` 负责特征工程与可视化 |
| (3) 算法定义 | LightGBM、LightFM、DIN(TF-IDF) 三种算法，`backend/src/recommendation/algorithms/` |
| (4) 图书推荐实现 | `/api/recommendations/*` 接口统一返回 Top-K 推荐，支持按书名/ID/算法切换 |
| (5) 系统展示 | `frontend/` 完成“搜索—详情—算法对比—快速推荐”的网页 Demo（含 i18n / LanguageToggle） |

---

如需更多接口字段，请参考 `frontend/docs/API.md`（英文版 `frontend/docs/API.en.md`）；前端使用指南见 `frontend/docs/USAGE.md`（英文版 `frontend/docs/USAGE.en.md`）；部署流程见 `DEPLOYMENT.md`（英文版 `DEPLOYMENT.en.md`）。欢迎基于现有架构扩展更多算法、特征或可视化。
