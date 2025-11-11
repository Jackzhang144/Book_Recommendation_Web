<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import SearchBar from '../components/SearchBar.vue'
import BookCard from '../components/BookCard.vue'
import { searchBooks, getRecommendationsByTitle } from '../services/api'
import { appConfig } from '../config/appConfig'
import { useI18n } from '../i18n'

const query = ref('')
const searchResults = ref([])
const searchLoading = ref(false)
const searchErrorMessage = ref('')
const searchErrorKey = ref('')
const hasSearched = ref(false)

const featuredBooks = ref([])
const featuredLoading = ref(true)
const featuredErrorMessage = ref('')
const featuredErrorKey = ref('')

const demoBooks = [
  {
    book_id: null,
    title: "Harry Potter and the Sorcerer's Stone",
    author: 'J. K. Rowling',
    image_url_m: 'https://covers.openlibrary.org/b/id/7984916-M.jpg',
  },
  {
    book_id: null,
    title: 'Harry Potter and the Chamber of Secrets',
    author: 'J. K. Rowling',
    image_url_m: 'https://covers.openlibrary.org/b/id/8231856-M.jpg',
  },
  {
    book_id: null,
    title: 'Fantastic Beasts and Where to Find Them',
    author: 'J. K. Rowling',
    image_url_m: 'https://covers.openlibrary.org/b/id/10521281-M.jpg',
  },
]

let activeSearchController
const { t } = useI18n()

const searchError = computed(() => {
  const localized = searchErrorKey.value ? t(`home.errors.${searchErrorKey.value}`) : ''
  return searchErrorMessage.value || localized
})

const featuredError = computed(() => {
  const localized = featuredErrorKey.value ? t(`home.errors.${featuredErrorKey.value}`) : ''
  if (featuredErrorMessage.value && localized) {
    return `${featuredErrorMessage.value} · ${localized}`
  }
  return featuredErrorMessage.value || localized
})

const clearSearchError = () => {
  searchErrorMessage.value = ''
  searchErrorKey.value = ''
}

const handleSearch = async () => {
  const keyword = query.value.trim()
  clearSearchError()
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
      searchErrorKey.value = 'noKeywordMatch'
    }
  } catch (error) {
    if (error?.message) {
      searchErrorMessage.value = error.message
    } else {
      searchErrorKey.value = 'searchFailed'
    }
  } finally {
    searchLoading.value = false
    activeSearchController = null
  }
}

const fetchFeatured = async () => {
  featuredLoading.value = true
  featuredErrorMessage.value = ''
  featuredErrorKey.value = ''
  try {
    const data = await getRecommendationsByTitle(appConfig.showcaseTitle, 5)
    featuredBooks.value = data.recommendations || []
  } catch (error) {
    if (error?.message) {
      featuredErrorMessage.value = error.message
    }
    featuredErrorKey.value = 'featuredFailed'
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
      <p class="eyebrow">{{ t('home.hero.eyebrow') }}</p>
      <h1>{{ t('home.hero.title') }}</h1>
      <p class="description">{{ t('home.hero.description') }}</p>
      <div class="hero__actions">
        <SearchBar
          v-model="query"
          :loading="searchLoading"
          :label="t('home.searchBar.label')"
          :placeholder="t('home.searchBar.placeholder')"
          @submit="handleSearch"
        />
        <RouterLink class="link-button" :to="{ name: 'quick-recommend' }">
          {{ t('home.hero.cta') }}
        </RouterLink>
      </div>
      <p v-if="searchError" class="error">{{ searchError }}</p>
    </section>

    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">{{ t('home.sectionSearch.eyebrow') }}</p>
          <h2>
            {{ hasSearched ? t('home.sectionSearch.titleSearched') : t('home.sectionSearch.titleIdle') }}
          </h2>
          <p v-if="!hasSearched" class="muted">{{ t('home.sectionSearch.helper') }}</p>
        </div>
      </header>
      <div v-if="searchLoading" class="placeholder">{{ t('home.sectionSearch.loading') }}</div>
      <div v-else-if="hasSearched && !searchResults.length" class="placeholder">
        {{ searchError || t('home.sectionSearch.empty') }}
      </div>
      <div v-else class="grid">
        <BookCard v-for="book in searchResults" :key="book.book_id" :book="book" />
      </div>
    </section>

    <section class="section">
      <header class="section__header">
        <div>
          <p class="eyebrow">{{ t('home.sectionFeatured.eyebrow') }}</p>
          <h2>{{ t('home.sectionFeatured.title') }}</h2>
          <p class="muted">
            {{ t('home.sectionFeatured.helper', { title: appConfig.showcaseTitle }) }}
          </p>
        </div>
      </header>
      <div v-if="featuredLoading" class="placeholder">{{ t('home.sectionFeatured.loading') }}</div>
      <div v-else>
        <p v-if="featuredError" class="warning">{{ featuredError }}</p>
        <div class="grid grid--compact">
          <BookCard v-for="book in featuredBooks" :key="book.book_id" :book="book" compact />
        </div>
      </div>
    </section>
  </div>
</template>
