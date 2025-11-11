<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from '../i18n'

const props = defineProps({
  book: {
    type: Object,
    required: true,
  },
  compact: {
    type: Boolean,
    default: false,
  },
  asLink: {
    type: Boolean,
    default: true,
  },
})

const coverUrl = computed(
  () => props.book.image_url_m || props.book.image_url_l || props.book.image_url_s,
)

const isLinkable = computed(() => props.asLink && Boolean(props.book?.book_id))

const linkTarget = computed(() =>
  isLinkable.value ? { name: 'book-detail', params: { bookId: props.book.book_id } } : null,
)

const bookMetadata = computed(() => {
  const metadata = []
  if (props.book.year_of_publication) {
    metadata.push(props.book.year_of_publication)
  }
  if (props.book.publisher) {
    metadata.push(props.book.publisher)
  }
  return metadata.join(' · ')
})

const scoreText = computed(() => {
  const score = Number(props.book.score)
  return Number.isFinite(score) ? score.toFixed(2) : null
})

const scoreDisplay = computed(() => scoreText.value ?? '--')
const { t } = useI18n()
</script>

<template>
  <component :is="isLinkable ? RouterLink : 'div'" :to="linkTarget || undefined">
    <article class="book-card" :class="{ 'book-card--compact': compact }">
      <img
        v-if="coverUrl"
        class="book-card__cover"
        :src="coverUrl"
        :alt="book.title"
        loading="lazy"
      />
      <div v-else class="book-card__cover book-card__cover--placeholder">
        {{ t('bookCard.noCover') }}
      </div>
      <div class="book-card__content">
        <p class="book-card__title">{{ book.title }}</p>
        <p class="book-card__author">{{ book.author }}</p>
        <p v-if="bookMetadata" class="book-card__meta">{{ bookMetadata }}</p>
        <p class="book-card__score">
          {{ t('bookCard.score') }}
          <span class="book-card__score-value">{{ scoreDisplay }}</span>
        </p>
      </div>
    </article>
  </component>
</template>

<style scoped>
.book-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  background: #fff;
  height: 100%;
  min-height: 190px;
}

.book-card:hover {
  border-color: #2563eb;
  box-shadow: 0 10px 25px rgba(37, 99, 235, 0.08);
}

.book-card--compact {
  flex-direction: column;
  text-align: center;
  min-height: 260px;
}

.book-card__cover {
  width: 90px;
  height: 130px;
  object-fit: cover;
  border-radius: 0.5rem;
  background: #f3f4f6;
}

.book-card--compact .book-card__cover {
  width: 120px;
  height: 175px;
  align-self: center;
}

.book-card__content {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
}

.book-card__cover--placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 0.85rem;
  font-weight: 500;
  text-align: center;
  border: 1px dashed #d1d5db;
}

.book-card__title {
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.25rem;
}

.book-card__author {
  color: #4b5563;
  font-size: 0.95rem;
}

.book-card__meta {
  color: #6b7280;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.book-card__score {
  color: #2563eb;
  font-weight: 600;
  margin-top: auto;
  font-size: 0.9rem;
}

.book-card__score-value {
  margin-left: 0.25rem;
}
</style>
