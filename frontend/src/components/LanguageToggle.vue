<script setup>
import { computed } from 'vue'
import { useI18n } from '../i18n'

const { locale, setLocale, t } = useI18n()

const isActive = (lang) => locale.value === lang

const switchTo = (lang) => {
  if (!isActive(lang)) {
    setLocale(lang)
  }
}

const zhLabel = computed(() => t('language.zh'))
const enLabel = computed(() => t('language.en'))
</script>

<template>
  <div class="language-toggle" role="group" :aria-label="t('general.languageLabel')">
    <button
      type="button"
      class="language-toggle__option"
      :class="{ 'language-toggle__option--active': isActive('zh') }"
      @click="switchTo('zh')"
    >
      {{ zhLabel }}
    </button>
    <span class="language-toggle__divider">/</span>
    <button
      type="button"
      class="language-toggle__option"
      :class="{ 'language-toggle__option--active': isActive('en') }"
      @click="switchTo('en')"
    >
      {{ enLabel }}
    </button>
  </div>
</template>

<style scoped>
.language-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
}

.language-toggle__option {
  background: transparent;
  border: none;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.65);
  cursor: pointer;
  padding: 0.1rem 0.2rem;
  font-weight: 600;
  transition: color 0.2s ease;
}

.language-toggle__option--active {
  color: #fff;
}

.language-toggle__divider {
  color: rgba(255, 255, 255, 0.35);
  font-size: 0.8rem;
}
</style>
