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
  <form class="search-bar" @submit.prevent="handleSubmit">
    <label class="search-bar__label" :for="inputId">{{ resolvedLabel }}</label>
    <div class="search-bar__controls">
      <input
        :id="inputId"
        class="search-bar__input"
        :placeholder="resolvedPlaceholder"
        :value="modelValue"
        :disabled="loading"
        @input="$emit('update:modelValue', $event.target.value)"
      />
      <button class="search-bar__button" type="submit" :disabled="isDisabled">
        {{ loading ? resolvedLoadingText : resolvedButtonText }}
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
  color: #4b5563;
}

.search-bar__controls {
  display: flex;
  gap: 0.75rem;
}

.search-bar__input {
  flex: 1;
  border-radius: 0.75rem;
  border: 1px solid #d1d5db;
  padding: 0.85rem 1rem;
  font-size: 1rem;
}

.search-bar__input:focus {
  outline: 2px solid #2563eb;
  border-color: #2563eb;
}

.search-bar__button {
  border: none;
  border-radius: 0.75rem;
  background: #2563eb;
  color: #fff;
  font-weight: 600;
  padding: 0 1.5rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.search-bar__button:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}
</style>
