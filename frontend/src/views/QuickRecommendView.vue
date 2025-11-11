<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import SearchBar from '../components/SearchBar.vue'
import BookCard from '../components/BookCard.vue'
import { getRecommendationsByTitle } from '../services/api'
import { useI18n } from '../i18n'

const title = ref('')
const loading = ref(false)
const errorMessage = ref('')
const errorKey = ref('')
const queryBook = ref(null)
const recommendations = ref([])
const { t } = useI18n()

const formError = computed(() => {
  const localized = errorKey.value ? t(`quick.errors.${errorKey.value}`) : ''
  if (errorMessage.value && localized) {
    return `${errorMessage.value} · ${localized}`
  }
  return errorMessage.value || localized
})

const clearError = () => {
  errorMessage.value = ''
  errorKey.value = ''
}

const handleSubmit = async () => {
  const keyword = title.value.trim()
  clearError()
  queryBook.value = null
  recommendations.value = []
  if (!keyword) {
    errorKey.value = 'missingKeyword'
    return
  }
  loading.value = true
  try {
    const data = await getRecommendationsByTitle(keyword)
    queryBook.value = data.query_book || null
    recommendations.value = data.recommendations || []
    if (!recommendations.value.length) {
      errorKey.value = 'noRecommendations'
    }
  } catch (err) {
    if (err?.message) {
      errorMessage.value = err.message
    }
    errorKey.value = 'apiUnavailable'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <RouterLink class="link-button" :to="{ name: 'home' }">{{ t('quick.back') }}</RouterLink>
    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">{{ t('quick.sectionIntro.eyebrow') }}</p>
          <h1>{{ t('quick.sectionIntro.title') }}</h1>
          <p class="muted">{{ t('quick.sectionIntro.helper') }}</p>
        </div>
      </header>
      <SearchBar
        v-model="title"
        :label="t('quick.searchBar.label')"
        :placeholder="t('quick.searchBar.placeholder')"
        :loading="loading"
        :button-text="t('quick.searchBar.button')"
        @submit="handleSubmit"
      />
      <p v-if="formError" class="warning">{{ formError }}</p>
    </section>

    <section v-if="queryBook" class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">{{ t('quick.sections.matchedEyebrow') }}</p>
          <h2>{{ queryBook.title }}</h2>
        </div>
      </header>
      <BookCard :book="queryBook" :as-link="false" />
    </section>

    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">{{ t('quick.sections.recommendEyebrow') }}</p>
          <h2>{{ t('quick.sections.recommendTitle') }}</h2>
        </div>
      </header>
      <div v-if="loading" class="placeholder">{{ t('quick.placeholders.loading') }}</div>
      <div v-else-if="!recommendations.length" class="placeholder">
        {{ t('quick.placeholders.empty') }}
      </div>
      <div v-else class="grid grid--compact">
        <BookCard v-for="book in recommendations" :key="book.book_id" :book="book" compact />
      </div>
    </section>
  </div>
</template>
