<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import SearchBar from '../components/SearchBar.vue'
import BookCard from '../components/BookCard.vue'
import { searchBooks, getRecommendationsByTitle } from '../services/api'
import { appConfig } from '../config/appConfig'

const query = ref('')
const searchResults = ref([])
const searchLoading = ref(false)
const searchError = ref('')
const hasSearched = ref(false)

const featuredBooks = ref([])
const featuredLoading = ref(true)
const featuredError = ref('')

const demoBooks = [
  {
    book_id: '12345',
    title: "Harry Potter and the Sorcerer's Stone",
    author: 'J. K. Rowling',
    image_url_m: 'https://covers.openlibrary.org/b/id/7984916-M.jpg',
  },
  {
    book_id: '23456',
    title: 'Harry Potter and the Chamber of Secrets',
    author: 'J. K. Rowling',
    image_url_m: 'https://covers.openlibrary.org/b/id/8231856-M.jpg',
  },
  {
    book_id: '34567',
    title: 'Fantastic Beasts and Where to Find Them',
    author: 'J. K. Rowling',
    image_url_m: 'https://covers.openlibrary.org/b/id/10521281-M.jpg',
  },
]

let activeSearchController

const handleSearch = async () => {
  const keyword = query.value.trim()
  searchError.value = ''
  hasSearched.value = true
  if (!keyword) {
    searchResults.value = []
    return
  }
  searchLoading.value = true
  try {
    if (activeSearchController) {
      activeSearchController.abort()
    }
    activeSearchController = new AbortController()
    const data = await searchBooks(
      { q: keyword, limit: appConfig.defaultSearchLimit },
      { signal: activeSearchController.signal },
    )
    searchResults.value = data.books || []
    if (!searchResults.value.length) {
      searchError.value = '没有匹配的图书，建议更换关键词'
    }
  } catch (error) {
    searchError.value = error.message || '搜索失败，请稍后重试'
  } finally {
    searchLoading.value = false
    activeSearchController = null
  }
}

const fetchFeatured = async () => {
  featuredLoading.value = true
  try {
    const data = await getRecommendationsByTitle(appConfig.showcaseTitle, 5)
    featuredBooks.value = data.recommendations || []
  } catch (error) {
    featuredError.value = error.message || '无法获取推荐，以下为示例数据'
    featuredBooks.value = demoBooks
  } finally {
    featuredLoading.value = false
  }
}

onMounted(fetchFeatured)
</script>

<template>
  <div class="page">
    <section class="hero">
      <p class="eyebrow">阅荐助手 · Web Demo</p>
      <h1>一键接入的智能图书推荐体验</h1>
      <p class="description">
        覆盖“搜索-详情-算法对比”三大场景，只需配置后端地址即可交付。所有文案与状态提示均已本地化，方便直接演示。
      </p>
      <div class="hero__actions">
        <SearchBar
          v-model="query"
          :loading="searchLoading"
          label="按书名或作者检索"
          placeholder="例如 解忧杂货店"
          @submit="handleSearch"
        />
        <RouterLink class="link-button" :to="{ name: 'quick-recommend' }">
          查看即时推荐流程 →
        </RouterLink>
      </div>
      <p v-if="searchError" class="error">{{ searchError }}</p>
    </section>

    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">实时检索</p>
          <h2>{{ hasSearched ? '根据关键词联调返回的图书' : '等待你的输入' }}</h2>
          <p v-if="!hasSearched" class="muted">输入关键词后即调用 GET /books/search，并展示 Top {{ appConfig.defaultSearchLimit }} 条。</p>
        </div>
      </header>
      <div v-if="searchLoading" class="placeholder">正在联接检索接口...</div>
      <div v-else-if="hasSearched && !searchResults.length" class="placeholder">
        {{ searchError || '暂无数据' }}
      </div>
      <div v-else class="grid">
        <BookCard v-for="book in searchResults" :key="book.book_id" :book="book" />
      </div>
    </section>

    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">精选推荐</p>
          <h2>同类读者也在读</h2>
          <p class="muted">默认调用 GET /recommendations/by-title?q={{ appConfig.showcaseTitle }}&k=5，可根据展示需求随时替换。</p>
        </div>
      </header>
      <div v-if="featuredLoading" class="placeholder">正在生成推荐列表...</div>
      <div v-else>
        <p v-if="featuredError" class="warning">{{ featuredError }}</p>
        <div class="grid grid--compact">
          <BookCard v-for="book in featuredBooks" :key="book.book_id" :book="book" compact />
        </div>
      </div>
    </section>
  </div>
</template>
