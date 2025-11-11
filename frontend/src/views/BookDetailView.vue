<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import BookCard from '../components/BookCard.vue'
import {
  getBookDetail,
  getRecommendationsByBook,
  getRecommendationsByBookAndAlgorithm,
} from '../services/api'
import { useI18n } from '../i18n'

const props = defineProps({
  bookId: {
    type: String,
    required: true,
  },
})

const book = ref(null)
const bookLoading = ref(true)
const bookErrorMessage = ref('')
const bookErrorActive = ref(false)

const recommendations = ref([])
const recLoading = ref(false)
const recErrorMessage = ref('')
const recErrorActive = ref(false)

const algorithm = ref('lightgbm')
const algoRecommendations = ref([])
const algoLoading = ref(false)
const algoErrorMessage = ref('')
const algoErrorActive = ref(false)

const algorithmOptions = [
  { id: 'lightgbm', name: 'LightGBM Pairwise Similarity' },
  { id: 'cf_mf', name: 'LightFM Collaborative Filtering' },
  { id: 'din_content', name: 'DIN Content-based Recommendation' },
]
const { t } = useI18n()

const bookErrorText = computed(() => bookErrorMessage.value || t('bookDetail.detail.error'))
const recErrorText = computed(() => recErrorMessage.value || t('bookDetail.similar.error'))
const algoErrorText = computed(() => algoErrorMessage.value || t('bookDetail.algorithm.error'))

const fetchBook = async () => {
  bookLoading.value = true
  bookErrorMessage.value = ''
  bookErrorActive.value = false
  try {
    const data = await getBookDetail(props.bookId)
    book.value = data.book || data
  } catch (error) {
    bookErrorMessage.value = error.message || ''
    bookErrorActive.value = true
  } finally {
    bookLoading.value = false
  }
}

const fetchRecommendations = async () => {
  recLoading.value = true
  recErrorMessage.value = ''
  recErrorActive.value = false
  try {
    const data = await getRecommendationsByBook(props.bookId)
    recommendations.value = data.recommendations || []
  } catch (error) {
    recErrorMessage.value = error.message || ''
    recErrorActive.value = true
    recommendations.value = []
  } finally {
    recLoading.value = false
  }
}

const fetchAlgorithmRecommendations = async () => {
  algoLoading.value = true
  algoErrorMessage.value = ''
  algoErrorActive.value = false
  try {
    const data = await getRecommendationsByBookAndAlgorithm(
      props.bookId,
      algorithm.value,
    )
    algoRecommendations.value = data.recommendations || []
  } catch (error) {
    algoErrorMessage.value = error.message || ''
    algoErrorActive.value = true
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
    <RouterLink class="link-button" :to="{ name: 'home' }">{{ t('bookDetail.back') }}</RouterLink>

    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">{{ t('bookDetail.detail.eyebrow') }}</p>
          <h1>{{ t('bookDetail.detail.title') }}</h1>
        </div>
      </header>
      <div v-if="bookLoading" class="placeholder">{{ t('bookDetail.detail.loading') }}</div>
      <div v-else-if="bookErrorActive" class="error">{{ bookErrorText }}</div>
      <BookCard v-else :book="book" :as-link="false" />
    </section>

    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">{{ t('bookDetail.similar.eyebrow') }}</p>
          <h2>{{ t('bookDetail.similar.title') }}</h2>
        </div>
      </header>
      <div v-if="recLoading" class="placeholder">{{ t('bookDetail.similar.loading') }}</div>
      <div v-else-if="recErrorActive" class="error">{{ recErrorText }}</div>
      <div v-else class="grid grid--compact">
        <BookCard v-for="book in recommendations" :key="book.book_id" :book="book" compact />
      </div>
    </section>

    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">{{ t('bookDetail.algorithm.eyebrow') }}</p>
          <h2>{{ t('bookDetail.algorithm.title') }}</h2>
        </div>
        <select v-model="algorithm" class="select">
          <option v-for="option in algorithmOptions" :key="option.id" :value="option.id">
            {{ option.name }}
          </option>
        </select>
      </header>
      <p class="muted">{{ t('bookDetail.algorithm.helper') }}</p>
      <div v-if="algoLoading" class="placeholder">{{ t('bookDetail.algorithm.loading') }}</div>
      <div v-else-if="algoErrorActive" class="warning">{{ algoErrorText }}</div>
      <div v-else class="grid grid--compact">
        <BookCard v-for="book in algoRecommendations" :key="book.book_id" :book="book" compact />
      </div>
    </section>
  </div>
</template>
