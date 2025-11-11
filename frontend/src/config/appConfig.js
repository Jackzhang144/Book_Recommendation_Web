const defaultBaseUrl = 'http://localhost:8000/api'

const normalizeUrl = (url) => (url ? url.replace(/\/$/, '') : '')

const toNumber = (value, fallback) => {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback
}

const rawEnvBaseUrl = import.meta.env?.VITE_API_BASE_URL
const rawTimeout = import.meta.env?.VITE_API_TIMEOUT
const rawSearchLimit = import.meta.env?.VITE_SEARCH_LIMIT
const rawShowcaseTitle = import.meta.env?.VITE_SHOWCASE_TITLE

export const appConfig = {
  /**
   * 后端 API 根路径，可通过 VITE_API_BASE_URL 在部署环境中覆盖。
   */
  apiBaseUrl: normalizeUrl(rawEnvBaseUrl || defaultBaseUrl),
  /**
   * 请求超时时间（毫秒），默认 10s，防止接口长时间无响应。
   */
  requestTimeoutMs: toNumber(rawTimeout, 10000),
  /**
   * 首页搜索默认返回条数，可通过 VITE_SEARCH_LIMIT 调整。
   */
  defaultSearchLimit: toNumber(rawSearchLimit, 12),
  /**
   * 首页“精选推荐”默认使用的基准书名，可通过 VITE_SHOWCASE_TITLE 定制。
   */
  showcaseTitle: rawShowcaseTitle || 'Harry Potter',
}
