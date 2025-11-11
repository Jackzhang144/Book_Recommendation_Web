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
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
}

.language-toggle__option {
  background: transparent;
  border: none;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 0.1rem 0.2rem;
  font-weight: 600;
}

.language-toggle__option--active {
  color: #fff;
  text-decoration: underline;
}

.language-toggle__divider {
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.8rem;
}
</style>
