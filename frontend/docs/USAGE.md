# Book Recommendation Web · 前端使用说明

> English version: [USAGE.en.md](USAGE.en.md)

## 1. 环境与依赖

- Node.js ≥ 18，npm ≥ 10
- 任意现代浏览器（推荐使用 Chrome/Edge 进行开发调试）

## 2. 目录速览

```
frontend/
├─ src/
│  ├─ App.vue                 # 布局与导航
│  ├─ components/             # SearchBar、BookCard、LanguageToggle 等复用组件
│  ├─ config/appConfig.js     # API 地址与默认参数
│  ├─ i18n/                   # 语言状态、词典、持久化逻辑
│  ├─ services/api.js         # 请求封装、错误处理、超时控制
│  ├─ views/                  # Home / BookDetail / QuickRecommend
│  └─ style.css               # 全局样式
├─ router/index.js            # 路由定义
├─ docs/                      # API & Usage 说明
└─ package.json
```

## 3. 配置 API

推荐写入仓库根目录下的 `.env` 或 `.env.local`：

```bash
VITE_API_BASE_URL=http://localhost:8000/api   # 必填：后端地址
VITE_API_TIMEOUT=10000                        # 可选：超时时长（毫秒）
VITE_SEARCH_LIMIT=12                          # 可选：首页搜索返回条数
VITE_SHOWCASE_TITLE=Harry Potter              # 可选：精选推荐基准书名
VITE_DEFAULT_LANG=en                          # 可选：初始语言（zh/en，默认自动侦测）
```

未设置时可在 `src/config/appConfig.js` 内修改默认值，该文件同时管理首页搜索条数及精选推荐书名。

## 4. 开发与构建

```bash
cd frontend
npm install          # 安装依赖
npm run dev          # 启动 Vite（默认端口 5173）
```

访问 `http://localhost:5173` 预览。构建上线版本：

```bash
npm run build        # 生成 dist/ 静态资源
```

`dist/` 可部署到任意静态站点，记得在部署环境设置同样的 `VITE_API_BASE_URL`。

## 5. 页面与接口对应

| 页面 | 路由 | 调用的 API |
| --- | --- | --- |
| 首页 | `/` | `GET /books/search`（搜索框）、`GET /recommendations/by-title`（精选推荐） |
| 详情页 | `/books/:bookId` | `GET /books/{id}`、`GET /recommendations/by-book`、`GET /recommendations/by-book-and-algorithm` |
| 快速推荐 | `/recommendations/by-title` | `GET /recommendations/by-title` |

`SearchBar` 组件接管输入与提交；`BookCard` 承载所有列表/详情展示；`LanguageToggle` 使用 `src/i18n` 暴露的 `useI18n()` 改变语言；`services/api.js` 统一处理超时、取消请求与错误提示。

## 6. 常见问题

1. **跨域错误**：确保后端已启用 CORS 或在 `vite.config.js` 中配置 `server.proxy`。
2. **接口字段变化**：在 `services/api.js` 中集中适配；`BookCard` 与各页面会优先显示已提供字段。
3. **扩展算法选项**：在 `BookDetailView.vue` 的 `algorithmOptions` 增加新 `id`，并在后端 `/system/algorithms` 返回对应项。
4. **多语言文案**：新增文案请在 `src/i18n/index.js` 同时补齐 `zh/en`；组件通过 `useI18n().t('key')` 读取。
5. **无网络示例**：可在 `services/api.js` 注入 mock 数据，或参考首页 `demoBooks` 的容错写法。

---

## 7. 液态玻璃样式要点

- `App.vue` 顶部注入的 `<svg class="app-filters">` 定义了 `#liquid-glass` 滤镜，通过 `feTurbulence + feGaussianBlur + feDisplacementMap` 模拟折射。
- `src/style.css` 中的 `.hero`、`.section`、`.placeholder/.warning/.error` 均通过 `filter: url('#liquid-glass')` 与 `backdrop-filter` 叠加出液态玻璃效果；如需新增卡片，可沿用同样的结构。
- Safari 对 `backdrop-filter` 的支持取决于用户设置，必要时可在 CSS 中提供降级的纯色背景。

更多接口细节见 `docs/API.md`；部署到生产环境可参考根目录 `DEPLOYMENT.md`。
