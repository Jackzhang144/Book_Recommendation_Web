import { appConfig } from '../config/appConfig'

const baseUrl = appConfig.apiBaseUrl

class ApiError extends Error {
  constructor(message, status = 500, payload) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
  }
}

const buildUrl = (path, params) => {
  const url = new URL(`${baseUrl}${path}`)
  if (params) {
    Object.entries(params)
      .filter(([, value]) => value !== undefined && value !== null && value !== '')
      .forEach(([key, value]) => url.searchParams.append(key, value))
  }
  return url
}

const request = async (path, config = {}) => {
  const { params, ...fetchOptions } = config
  const url = buildUrl(path, params)

  const controller = new AbortController()
  const { headers: customHeaders = {}, signal: externalSignal, ...restOptions } = fetchOptions
  let abortedByTimeout = false

  if (externalSignal) {
    if (externalSignal.aborted) {
      controller.abort(externalSignal.reason)
    } else {
      externalSignal.addEventListener('abort', () => controller.abort(), { once: true })
    }
  }

  const timeoutId =
    appConfig.requestTimeoutMs > 0
      ? setTimeout(() => {
          abortedByTimeout = true
          controller.abort()
        }, appConfig.requestTimeoutMs)
      : null

  try {
    const response = await fetch(url, {
      ...restOptions,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...customHeaders,
      },
      signal: controller.signal,
    })

    if (!response.ok) {
      const errorText = await response.text().catch(() => '')
      const errorMessage = errorText || `请求失败: ${response.status}`
      throw new ApiError(errorMessage, response.status)
    }

    const payload = await response.json().catch(() => ({}))
    const { code, message, data } = payload

    if (code !== undefined && code !== 0) {
      throw new ApiError(message || '接口返回错误', code, payload)
    }

    return data ?? payload
  } catch (error) {
    if (error.name === 'AbortError') {
      const message = abortedByTimeout ? '请求超时，请稍后重试' : '请求已取消'
      throw new ApiError(message, 408)
    }

    if (error instanceof ApiError) {
      throw error
    }

    throw new ApiError(error.message || '网络异常，请稍后再试', 500)
  } finally {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
  }
}

export const searchBooks = (params, config) =>
  request('/books/search', {
    ...(config || {}),
    params,
  })

export const getBookDetail = (bookId, config) => request(`/books/${bookId}`, config)

export const getRecommendationsByBook = (bookId, k = 5, config) =>
  request('/recommendations/by-book', {
    ...(config || {}),
    params: { book_id: bookId, k },
  })

export const getRecommendationsByBookAndAlgorithm = (bookId, algorithm, k = 5, config) =>
  request('/recommendations/by-book-and-algorithm', {
    ...(config || {}),
    params: { book_id: bookId, algorithm, k },
  })

export const getRecommendationsByTitle = (title, k = 5, config) =>
  request('/recommendations/by-title', {
    ...(config || {}),
    params: { q: title, k },
  })

export { ApiError }
