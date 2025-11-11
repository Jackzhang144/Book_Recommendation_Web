<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import SearchBar from '../components/SearchBar.vue'
import BookCard from '../components/BookCard.vue'
import { getRecommendationsByTitle } from '../services/api'

const title = ref('')
const loading = ref(false)
const error = ref('')
const queryBook = ref(null)
const recommendations = ref([])

const handleSubmit = async () => {
  const keyword = title.value.trim()
  error.value = ''
  queryBook.value = null
  recommendations.value = []
  if (!keyword) {
    error.value = '请输入你想查询的书名'
    return
  }
  loading.value = true
  try {
    const data = await getRecommendationsByTitle(keyword)
    queryBook.value = data.query_book || null
    recommendations.value = data.recommendations || []
    if (!recommendations.value.length) {
      error.value = '该标题暂无推荐结果'
    }
  } catch (err) {
    error.value = err.message || '推荐接口暂不可用'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <RouterLink class="link-button" :to="{ name: 'home' }">← 返回智能搜索</RouterLink>
    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">快速推荐</p>
          <h1>搜索即推荐的最短路径</h1>
          <p class="muted">输入目标书名后立刻命中 GET /recommendations/by-title，直接展示 Top-K 相似读物，适合答辩时的即席演示。</p>
        </div>
      </header>
      <SearchBar
        v-model="title"
        label="输入书名"
        placeholder="例如 三体"
        :loading="loading"
        button-text="获取推荐"
        @submit="handleSubmit"
      />
      <p v-if="error" class="warning">{{ error }}</p>
    </section>

    <section v-if="queryBook" class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">匹配的原书</p>
          <h2>{{ queryBook.title }}</h2>
        </div>
      </header>
      <BookCard :book="queryBook" :as-link="false" />
    </section>

    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">推荐结果</p>
          <h2>系统返回的 5 本相似书</h2>
        </div>
      </header>
      <div v-if="loading" class="placeholder">正在召回推荐...</div>
      <div v-else-if="!recommendations.length" class="placeholder">完成上方输入后即可展示推荐结果</div>
      <div v-else class="grid grid--compact">
        <BookCard v-for="book in recommendations" :key="book.book_id" :book="book" compact />
      </div>
    </section>
  </div>
</template>
