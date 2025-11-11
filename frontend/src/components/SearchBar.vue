<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '输入书名或关键词',
  },
  label: {
    type: String,
    default: '搜索图书 / 推荐',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  buttonText: {
    type: String,
    default: '开始检索',
  },
})

const emit = defineEmits(['update:modelValue', 'submit'])

const isDisabled = computed(() => props.loading)

const handleSubmit = () => {
  emit('submit')
}
</script>

<template>
  <form class="search-bar" @submit.prevent="handleSubmit">
    <label class="search-bar__label" :for="label">{{ label }}</label>
    <div class="search-bar__controls">
      <input
        :id="label"
        class="search-bar__input"
        :placeholder="placeholder"
        :value="modelValue"
        :disabled="loading"
        @input="$emit('update:modelValue', $event.target.value)"
      />
      <button class="search-bar__button" type="submit" :disabled="isDisabled">
        {{ loading ? '查询中...' : buttonText }}
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
