<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

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

const coverUrl = computed(() => props.book.image_url_m || props.book.image_url_l || props.book.image_url_s)

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
</script>

<template>
  <component
    :is="asLink ? RouterLink : 'div'"
    :to="asLink ? { name: 'book-detail', params: { bookId: book.book_id } } : undefined"
  >
    <article class="book-card" :class="{ 'book-card--compact': compact }">
      <img
        v-if="coverUrl"
        class="book-card__cover"
        :src="coverUrl"
        :alt="book.title"
        loading="lazy"
      />
      <div class="book-card__content">
        <p class="book-card__title">{{ book.title }}</p>
        <p class="book-card__author">{{ book.author }}</p>
        <p v-if="bookMetadata" class="book-card__meta">{{ bookMetadata }}</p>
        <p v-if="scoreText" class="book-card__score">匹配度 {{ scoreText }}</p>
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
}

.book-card:hover {
  border-color: #2563eb;
  box-shadow: 0 10px 25px rgba(37, 99, 235, 0.08);
}

.book-card--compact {
  flex-direction: column;
  text-align: center;
}

.book-card__cover {
  width: 90px;
  height: 130px;
  object-fit: cover;
  border-radius: 0.5rem;
}

.book-card--compact .book-card__cover {
  width: 120px;
  height: 175px;
  align-self: center;
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
  margin-top: 0.5rem;
}
</style>
