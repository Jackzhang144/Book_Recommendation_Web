import { computed, reactive } from 'vue'

const STORAGE_KEY = 'book-rec-language'

const messages = {
  zh: {
    app: {
      name: '阅荐助手',
      footer: '阅荐助手 · 图书推荐演示界面',
      nav: {
        home: '智能搜索',
        quick: '即时推荐',
      },
    },
    language: {
      zh: '中文',
      en: 'English',
    },
    general: {
      languageLabel: '界面语言',
    },
    home: {
      hero: {
        eyebrow: '阅荐助手 · Web Demo',
        title: '一键接入的智能图书推荐体验',
        description: '搜索、推荐与算法切换一体化的图书体验。',
        cta: '查看即时推荐流程 →',
      },
      searchBar: {
        label: '按书名或作者检索',
        placeholder: '例如 解忧杂货店',
      },
      sectionSearch: {
        eyebrow: '实时检索',
        titleSearched: '根据关键词联调返回的图书',
        titleIdle: '等待你的输入',
        helper: '输入关键词即可看到实时搜索结果。',
        loading: '正在联接检索接口...',
        empty: '暂无数据',
      },
      sectionFeatured: {
        eyebrow: '精选推荐',
        title: '同类读者也在读',
        helper: '基于《{title}》的相似读物。',
        loading: '正在生成推荐列表...',
      },
      errors: {
        noKeywordMatch: '没有匹配的图书，建议更换关键词',
        searchFailed: '搜索失败，请稍后重试',
        featuredFailed: '无法获取推荐，以下为示例数据',
      },
    },
    quick: {
      back: '← 返回智能搜索',
      sectionIntro: {
        eyebrow: '快速推荐',
        title: '搜索即推荐的最短路径',
        helper: '输入书名即可获取相似读物。',
      },
      searchBar: {
        label: '输入书名',
        placeholder: '例如 三体',
        button: '获取推荐',
      },
      sections: {
        matchedEyebrow: '匹配的原书',
        recommendEyebrow: '推荐结果',
        recommendTitle: '系统返回的 5 本相似书',
      },
      placeholders: {
        loading: '正在召回推荐...',
        empty: '完成上方输入后即可展示推荐结果',
      },
      errors: {
        missingKeyword: '请输入你想查询的书名',
        noRecommendations: '该标题暂无推荐结果',
        apiUnavailable: '推荐接口暂不可用',
      },
    },
    bookDetail: {
      back: '← 返回智能搜索',
      detail: {
        eyebrow: '图书详情',
        title: '图书概览',
        loading: '加载详情...',
        error: '无法获取图书详情',
      },
      similar: {
        eyebrow: '相似推荐',
        title: '默认算法的相似读物',
        loading: '推荐加载中...',
        error: '无法获取相似图书',
      },
      algorithm: {
        eyebrow: '算法对比',
        title: '切换不同算法的 Top-K 结果',
        helper:
          '切换下拉框即可查看 LightGBM / CF / DeepFM 等算法的差异化输出，方便交付评审。',
        loading: '根据所选算法拉取推荐...',
        error: '算法接口暂不可用',
      },
    },
    searchBar: {
      label: '搜索图书 / 推荐',
      placeholder: '输入书名或关键词',
      button: '开始检索',
      loading: '查询中...',
    },
    bookCard: {
      noCover: '无封面',
      score: '匹配度',
    },
  },
  en: {
    app: {
      name: 'ReadRec Assistant',
      footer: 'ReadRec Assistant · Book Recommendation Demo',
      nav: {
        home: 'Intelligent Search',
        quick: 'Instant Recommendations',
      },
    },
    language: {
      zh: '中文',
      en: 'English',
    },
    general: {
      languageLabel: 'Interface language',
    },
    home: {
      hero: {
        eyebrow: 'ReadRec Assistant · Web Demo',
        title: 'Plug-and-play intelligent book recommendations',
        description: 'Search, recommendations, and algorithm comparisons in one UI.',
        cta: 'See the instant recommendation flow →',
      },
      searchBar: {
        label: 'Search by title or author',
        placeholder: 'e.g. The Miracles of the Namiya General Store',
      },
      sectionSearch: {
        eyebrow: 'Live search',
        titleSearched: 'Books returned from the API',
        titleIdle: 'Waiting for your input',
        helper: 'Type a keyword to see results right away.',
        loading: 'Calling the search API...',
        empty: 'No data yet',
      },
      sectionFeatured: {
        eyebrow: 'Featured picks',
        title: 'Readers also enjoyed',
        helper: 'Similar titles based on “{title}”.',
        loading: 'Generating the recommendation list...',
      },
      errors: {
        noKeywordMatch: 'No matching books, try a different keyword',
        searchFailed: 'Search failed, please retry later',
        featuredFailed: 'Unable to fetch recommendations, showing demo data instead',
      },
    },
    quick: {
      back: '← Back to intelligent search',
      sectionIntro: {
        eyebrow: 'Quick recommendations',
        title: 'Shortest path from query to recommendation',
        helper: 'Enter a title to get similar books.',
      },
      searchBar: {
        label: 'Enter a title',
        placeholder: 'e.g. The Three-Body Problem',
        button: 'Get recommendations',
      },
      sections: {
        matchedEyebrow: 'Matched source title',
        recommendEyebrow: 'Recommendation results',
        recommendTitle: 'Top 5 similar books returned by the system',
      },
      placeholders: {
        loading: 'Fetching recommendations...',
        empty: 'Complete the input above to see recommendations',
      },
      errors: {
        missingKeyword: 'Please enter the title you want to query',
        noRecommendations: 'No recommendations for this title yet',
        apiUnavailable: 'Recommendation service is temporarily unavailable',
      },
    },
    bookDetail: {
      back: '← Back to intelligent search',
      detail: {
        eyebrow: 'Book details',
        title: 'Overview',
        loading: 'Loading details...',
        error: 'Unable to fetch book details',
      },
      similar: {
        eyebrow: 'Similar recommendations',
        title: 'Similar titles from the default algorithm',
        loading: 'Loading recommendations...',
        error: 'Unable to fetch similar books',
      },
      algorithm: {
        eyebrow: 'Algorithm comparison',
        title: 'Switch between Top-K outputs',
        helper: 'Toggle the dropdown to compare LightGBM / CF / Deep models for review.',
        loading: 'Fetching recommendations for the selected algorithm...',
        error: 'Algorithm service is temporarily unavailable',
      },
    },
    searchBar: {
      label: 'Search books / recommendations',
      placeholder: 'Enter a title or author',
      button: 'Start searching',
      loading: 'Searching...',
    },
    bookCard: {
      noCover: 'No cover',
      score: 'Match score',
    },
  },
}

const getStoredLocale = () => {
  if (typeof window === 'undefined') return null
  return window.localStorage.getItem(STORAGE_KEY)
}

const getBrowserLocale = () => {
  if (typeof navigator === 'undefined') return null
  return navigator.language?.slice(0, 2)?.toLowerCase() || null
}

const isSupportedLocale = (locale) => Boolean(locale && messages[locale])

const resolveInitialLocale = () => {
  const stored = getStoredLocale()
  if (isSupportedLocale(stored)) {
    return stored
  }
  const browser = getBrowserLocale()
  if (isSupportedLocale(browser)) {
    return browser
  }
  return 'zh'
}

const state = reactive({
  locale: resolveInitialLocale(),
})

const setDocumentLang = (lang) => {
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('lang', lang)
  }
}

setDocumentLang(state.locale)

const storeLocale = (locale) => {
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(STORAGE_KEY, locale)
  }
}

const resolveMessage = (locale, key) => {
  return key.split('.').reduce((acc, part) => {
    if (acc && Object.prototype.hasOwnProperty.call(acc, part)) {
      return acc[part]
    }
    return undefined
  }, messages[locale])
}

const formatMessage = (message, params = {}) => {
  if (typeof message !== 'string') {
    return message
  }
  return message.replace(/\{(\w+)\}/g, (_, token) => {
    return params[token] ?? `{${token}}`
  })
}

const setLocale = (nextLocale) => {
  if (!isSupportedLocale(nextLocale) || nextLocale === state.locale) {
    return
  }
  state.locale = nextLocale
  storeLocale(nextLocale)
  setDocumentLang(nextLocale)
}

export const availableLocales = Object.keys(messages)

export function useI18n() {
  const locale = computed(() => state.locale)

  const t = (key, params) => {
    const message = resolveMessage(state.locale, key)
    if (message === undefined) {
      return key
    }
    return formatMessage(message, params)
  }

  return {
    t,
    locale,
    setLocale,
    availableLocales,
  }
}
