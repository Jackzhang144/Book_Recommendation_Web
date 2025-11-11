# Book Recommendation Web · Front-end

Vue 3 + Vite 单页应用，对应《任务介绍.md》和《Book Recommendation Web API 文档（草案）》要求的交付场景，已完成中文文案与提示语的统一。

## 功能概览

- **首页**：书名/作者搜索（GET `/books/search`）、实时提示与精选推荐（GET `/recommendations/by-title`）
- **图书详情**：展示图书信息（GET `/books/{book_id}`）、默认推荐（GET `/recommendations/by-book`）、多算法切换对比
- **快速推荐页**：输入书名后直接输出 Top-K 结果（GET `/recommendations/by-title?q=xxx&k=5`）

请求层内置超时与取消控制，可防止重复搜索造成的闪烁。

## 配置与运行

1. 在部署/本地运行之前设置环境变量（可写入 `.env`）：

   ```bash
   VITE_API_BASE_URL=http://localhost:8000/api   # 必需，指向真实后端
   VITE_API_TIMEOUT=10000                        # 可选，接口超时毫秒
   VITE_SEARCH_LIMIT=12                          # 可选，首页搜索返回数量
   VITE_SHOWCASE_TITLE=Harry Potter              # 可选，精选推荐的基准书名
   ```

   若未设置，`src/config/appConfig.js` 会 fallback 到默认值。

2. 安装依赖并启动开发模式：

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. 构建生产包：

   ```bash
   npm run build
   ```

   生成的 `dist/` 可部署到任意静态托管，确保上线环境同样提供 `VITE_API_BASE_URL`。

## 关键文件

| 功能 | 路径 |
| --- | --- |
| 路由配置 | `src/router/index.js` |
| API 请求封装 | `src/services/api.js` |
| 首页 / 搜索 | `src/views/HomeView.vue` |
| 图书详情 + 算法对比 | `src/views/BookDetailView.vue` |
| 快速推荐 | `src/views/QuickRecommendView.vue` |

## 文档

- 详尽 API 说明：`docs/API.md`
- 操作 / 运维说明：`docs/USAGE.md`

## 下一步建议

1. 根据后端字段补齐封面、标签等更多展示信息。
2. 在 `BookDetailView.vue` 的 `algorithmOptions` 中扩展更多模型，并与后端保持同名。
3. 如需大屏/演示页，可基于现有组件组合新的路由或图表模块。
