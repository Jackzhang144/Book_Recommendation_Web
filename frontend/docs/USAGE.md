# Book Recommendation Web · Usage 文档

## 1. 环境要求

- Node.js ≥ 18
- npm ≥ 10
- 任意现代浏览器（开发阶段推荐 Chrome/Edge）

## 2. 目录结构速览

```
frontend/
├─ src/
│  ├─ App.vue                # 布局 + 导航
│  ├─ style.css              # 全局样式
│  ├─ config/appConfig.js    # API & 请求参数配置
│  ├─ services/api.js        # 请求封装 + 错误处理
│  ├─ components/
│  │  ├─ SearchBar.vue
│  │  └─ BookCard.vue
│  └─ views/
│     ├─ HomeView.vue        # 搜索 + 热门推荐
│     ├─ BookDetailView.vue  # 详情 + 多算法对比
│     └─ QuickRecommendView.vue # 搜索即推荐
├─ router/index.js           # 路由定义
├─ docs/                     # 本文档与 API 文档
└─ package.json
```

## 3. 配置 API 地址与请求参数

优先通过环境变量控制，便于在不同环境直接交付。可以在仓库根目录新增 `.env`：

```bash
VITE_API_BASE_URL=http://localhost:8000/api   # 指向真实后端
VITE_API_TIMEOUT=10000                        # 超时时间（毫秒）
VITE_SEARCH_LIMIT=12                          # 首页搜索返回条数
VITE_SHOWCASE_TITLE=Harry Potter              # 精选推荐的基准书名
```

如未设置变量，可在 `src/config/appConfig.js` 中修改默认值；同一文件还维护了搜索条数与展示基准书名。

## 4. 安装与运行

```bash
cd frontend
npm install           # 安装依赖
npm run dev           # 启动 Vite，本地默认 5173 端口
```

访问 `http://localhost:5173` 即可预览。

## 5. 构建与部署

```bash
npm run build         # 生成 dist/ 静态资源
```

- `dist/` 目录内容可直接发布到任意静态托管（Nginx、Vercel、Netlify 等）。
- 如果后端与前端为同域，可将 `apiBaseUrl` 设为相对路径，例如 `/api`。

## 6. 功能说明

| 页面 | 路由 | 功能点 |
| --- | --- | --- |
| 首页 | `/` | 搜索框联调 `/books/search`，支持请求取消避免重复刷新；精选推荐展示 `/recommendations/by-title` 结果；跳转到“快速推荐”页 |
| 书籍详情 | `/books/:bookId` | 加载 `/books/{book_id}`；展示默认推荐 `/recommendations/by-book`；算法切换调用 `/recommendations/by-book-and-algorithm` |
| 快速推荐 | `/recommendations/by-title` | 输入书名后直接调用 `/recommendations/by-title?q=xxx&k=5`，展示匹配书与推荐列表 |

组件复用：`SearchBar` 提供输入+提交事件；`BookCard` 用于所有列表/详情展示。

## 7. 常见问题

1. **跨域 (CORS) 报错**：确认后端允许来自前端域名的请求，或在本地通过代理（可修改 `vite.config.js` 设置 `server.proxy`）。
2. **接口数据结构变化**：若字段名不一致，请在 `src/services/api.js` 中统一转换，或调整各页面的解构逻辑。
3. **需要增加算法**：在 `BookDetailView.vue` 的 `algorithmOptions` 数组中新增 `{ id, name }`，并保证后端支持对应的 `algorithm` 参数。
4. **无网络/离线演示**：可以在 `services/api.js` 中暂时替换为本地 mock 数据，或在页面中加上示例数据 fallback（首页已示范 `demoBooks`）。
5. **搜索被打断**：若用户频繁提交搜索，前一次请求会被自动取消，防止延迟结果覆盖最新输入。

## 8. 推荐开发流程

1. 后端提供最小可用接口并通过 Postman 自测。
2. 前端在 `appConfig` 中对齐 Base URL，运行 `npm run dev` 联调。
3. 根据《API 文档》逐条验证并在浏览器 Network 面板确认请求/响应。
4. 联调完成后执行 `npm run build`，将 `dist/` 部署到正式环境。

更多细节请参考 `docs/API.md`。
