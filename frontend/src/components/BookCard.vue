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

// 统一拼接出版年份与出版社，避免模板中到处做空值判断
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

const { t } = useI18n()
</script>

<template>
  <component :is="isLinkable ? RouterLink : 'div'" :to="linkTarget || undefined">
    <article class="book-card" :class="{ 'book-card--compact': compact }">
      <div class="book-card__glow" aria-hidden="true" />
      <div
        class="book-card__media"
        :class="{ 'book-card__media--placeholder': !coverUrl, 'book-card__media--compact': compact }"
      >
        <img
          v-if="coverUrl"
          class="book-card__cover"
          :src="coverUrl"
          :alt="book.title"
          loading="lazy"
        />
        <div v-else class="book-card__placeholder">
          {{ t('bookCard.noCover') }}
        </div>
        <span v-if="scoreText" class="book-card__score-chip">{{ scoreText }}</span>
      </div>
      <div class="book-card__content">
        <p class="book-card__title">{{ book.title }}</p>
        <p class="book-card__author">{{ book.author }}</p>
        <p v-if="bookMetadata" class="book-card__meta">{{ bookMetadata }}</p>
      </div>
    </article>
  </component>
</template>

<style scoped>
.book-card {
  position: relative;
  display: flex;
  gap: 1.25rem;
  padding: 1.25rem;
  border-radius: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(4, 7, 22, 0.8);
  overflow: hidden;
  min-height: 260px;
  height: 100%;
  transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}

.book-card:hover {
  transform: translateY(-4px);
  border-color: rgba(103, 232, 249, 0.4);
  box-shadow: 0 25px 40px rgba(2, 6, 23, 0.6);
}

.book-card__glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 20% 20%, rgba(103, 232, 249, 0.18), transparent 60%);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 0;
}

.book-card:hover .book-card__glow {
  opacity: 1;
}

.book-card__media {
  position: relative;
  width: 110px;
  min-width: 110px;
  height: 150px;
  border-radius: 1rem;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
}

.book-card--compact .book-card__media {
  width: 100%;
  min-width: unset;
  height: 190px;
}

.book-card__media--compact {
  margin-inline: auto;
}

.book-card__cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-card__media--placeholder {
  background: repeating-linear-gradient(
    -45deg,
    rgba(255, 255, 255, 0.08),
    rgba(255, 255, 255, 0.08) 10px,
    rgba(255, 255, 255, 0.05) 10px,
    rgba(255, 255, 255, 0.05) 20px
  );
}

.book-card__placeholder {
  padding: 0 0.5rem;
  text-align: center;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
}

.book-card__score-chip {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  border-radius: 999px;
  padding: 0.2rem 0.65rem;
  font-size: 0.8rem;
  font-weight: 600;
  background: rgba(3, 7, 18, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #67e8f9;
}

.book-card__content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  flex: 1;
}

.book-card--compact {
  flex-direction: column;
  text-align: center;
  align-items: center;
  min-height: 320px;
}

.book-card--compact .book-card__content {
  align-items: center;
}

.book-card__title {
  font-weight: 600;
  font-size: 1.05rem;
  margin: 0;
}

.book-card__author {
  color: rgba(255, 255, 255, 0.75);
  font-size: 0.95rem;
  margin: 0;
}

.book-card__meta {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
  margin-top: 0.25rem;
}
</style>
