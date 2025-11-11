<script setup>
import { computed, useId } from 'vue'
import { useI18n } from '../i18n'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '',
  },
  label: {
    type: String,
    default: '',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  buttonText: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'submit'])
const { t } = useI18n()
const uid = useId()
const inputId = computed(() => `search-bar-${uid}`)

const isDisabled = computed(() => props.loading)

const handleSubmit = () => {
  emit('submit')
}

const resolvedLabel = computed(() => props.label || t('searchBar.label'))
const resolvedPlaceholder = computed(() => props.placeholder || t('searchBar.placeholder'))
const resolvedButtonText = computed(() => props.buttonText || t('searchBar.button'))
const resolvedLoadingText = computed(() => t('searchBar.loading'))
</script>

<template>
  <form class="search-bar" :aria-busy="loading" @submit.prevent="handleSubmit">
    <label class="search-bar__label" :for="inputId">
      <span>{{ resolvedLabel }}</span>
      <span v-if="loading" class="search-bar__label-status">{{ resolvedLoadingText }}</span>
    </label>
    <div class="search-bar__controls">
      <div class="search-bar__field">
        <span class="search-bar__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none">
            <path
              d="M21 21l-4.35-4.35m1.513-4.663a6.5 6.5 0 1 1-13 0 6.5 6.5 0 0 1 13 0Z"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linecap="round"
            />
          </svg>
        </span>
        <input
          :id="inputId"
          class="search-bar__input"
          :placeholder="resolvedPlaceholder"
          :value="modelValue"
          :disabled="loading"
          @input="$emit('update:modelValue', $event.target.value)"
        />
      </div>
      <button class="search-bar__button" type="submit" :disabled="isDisabled">
        <span>{{ loading ? resolvedLoadingText : resolvedButtonText }}</span>
      </button>
    </div>
  </form>
</template>

<style scoped>
.search-bar {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.search-bar__label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.65);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar__label-status {
  font-size: 0.8rem;
  color: rgba(103, 232, 249, 0.9);
}

.search-bar__controls {
  display: flex;
  gap: 0.75rem;
  align-items: stretch;
}

.search-bar__field {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-radius: 999px;
  padding: 0.85rem 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(3, 7, 18, 0.5);
  backdrop-filter: blur(12px);
  transition: border-color 0.2s ease, background 0.2s ease;
}

.search-bar__field:focus-within {
  border-color: rgba(103, 232, 249, 0.7);
  background: rgba(3, 7, 18, 0.75);
}

.search-bar__icon {
  width: 1.25rem;
  height: 1.25rem;
  color: rgba(255, 255, 255, 0.6);
  display: inline-flex;
}

.search-bar__icon svg {
  width: 100%;
  height: 100%;
}

.search-bar__input {
  flex: 1;
  border: none;
  background: transparent;
  color: #fff;
  font-size: 1rem;
  font-family: inherit;
}

.search-bar__input::placeholder {
  color: rgba(255, 255, 255, 0.55);
}

.search-bar__input:focus {
  outline: none;
}

.search-bar__button {
  border: none;
  border-radius: 999px;
  min-width: 160px;
  background: linear-gradient(135deg, #22d3ee, #c084fc);
  color: #030712;
  font-weight: 600;
  padding: 0 1.75rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.search-bar__button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.search-bar__button:not(:disabled):hover {
  filter: brightness(1.06);
}

@media (max-width: 640px) {
  .search-bar__controls {
    flex-direction: column;
  }

  .search-bar__button {
    width: 100%;
  }
}
</style>
