<script setup>
import { onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import BookCard from '../components/BookCard.vue'
import {
  getBookDetail,
  getRecommendationsByBook,
  getRecommendationsByBookAndAlgorithm,
} from '../services/api'

const props = defineProps({
  bookId: {
    type: String,
    required: true,
  },
})

const book = ref(null)
const bookLoading = ref(true)
const bookError = ref('')

const recommendations = ref([])
const recLoading = ref(false)
const recError = ref('')

const algorithm = ref('lightgbm')
const algoRecommendations = ref([])
const algoLoading = ref(false)
const algoError = ref('')

const algorithmOptions = [
  { id: 'lightgbm', name: 'LightGBM (课程必做)' },
  { id: 'user_cf', name: 'User-based CF' },
  { id: 'item_cf', name: 'Item-based CF' },
  { id: 'deepfm', name: 'DeepFM' },
]

const fetchBook = async () => {
  bookLoading.value = true
  bookError.value = ''
  try {
    const data = await getBookDetail(props.bookId)
    book.value = data.book || data
  } catch (error) {
    bookError.value = error.message || '无法获取图书详情'
  } finally {
    bookLoading.value = false
  }
}

const fetchRecommendations = async () => {
  recLoading.value = true
  recError.value = ''
  try {
    const data = await getRecommendationsByBook(props.bookId)
    recommendations.value = data.recommendations || []
  } catch (error) {
    recError.value = error.message || '无法获取相似图书'
    recommendations.value = []
  } finally {
    recLoading.value = false
  }
}

const fetchAlgorithmRecommendations = async () => {
  algoLoading.value = true
  algoError.value = ''
  try {
    const data = await getRecommendationsByBookAndAlgorithm(
      props.bookId,
      algorithm.value,
    )
    algoRecommendations.value = data.recommendations || []
  } catch (error) {
    algoError.value = error.message || '算法接口暂不可用'
    algoRecommendations.value = []
  } finally {
    algoLoading.value = false
  }
}

const init = async () => {
  if (!props.bookId) return
  await Promise.all([fetchBook(), fetchRecommendations()])
  fetchAlgorithmRecommendations()
}

onMounted(init)

watch(
  () => props.bookId,
  () => {
    init()
  },
)

watch(
  () => algorithm.value,
  () => {
    fetchAlgorithmRecommendations()
  },
)
</script>

<template>
  <div class="page">
    <RouterLink class="link-button" :to="{ name: 'home' }">← 返回智能搜索</RouterLink>

    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">图书详情</p>
          <h1>图书概览</h1>
        </div>
      </header>
      <div v-if="bookLoading" class="placeholder">加载详情...</div>
      <div v-else-if="bookError" class="error">{{ bookError }}</div>
      <BookCard v-else :book="book" :as-link="false" />
    </section>

    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">相似推荐</p>
          <h2>默认算法的相似读物</h2>
          <p class="muted">实时调用 GET /recommendations/by-book，展示默认召回算法的 Top-K 结果。</p>
        </div>
      </header>
      <div v-if="recLoading" class="placeholder">推荐加载中...</div>
      <div v-else-if="recError" class="error">{{ recError }}</div>
      <div v-else class="grid grid--compact">
        <BookCard v-for="book in recommendations" :key="book.book_id" :book="book" compact />
      </div>
    </section>

    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">算法对比</p>
          <h2>切换不同算法的 Top-K 结果</h2>
        </div>
        <select v-model="algorithm" class="select">
          <option v-for="option in algorithmOptions" :key="option.id" :value="option.id">
            {{ option.name }}
          </option>
        </select>
      </header>
      <p class="muted">切换下拉框即可查看 LightGBM / CF / DeepFM 等算法的差异化输出，方便交付评审。</p>
      <div v-if="algoLoading" class="placeholder">根据所选算法拉取推荐...</div>
      <div v-else-if="algoError" class="warning">{{ algoError }}</div>
      <div v-else class="grid grid--compact">
        <BookCard v-for="book in algoRecommendations" :key="book.book_id" :book="book" compact />
      </div>
    </section>
  </div>
</template>
