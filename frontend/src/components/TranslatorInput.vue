<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  modelValue: string
  placeholder: string
  isLoading: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  translate: []
  clear: []
}>()

function handleInput(event: Event) {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}

function handleKeydown(event: KeyboardEvent) {
  // Ctrl+Enter to translate
  if (event.ctrlKey && event.key === 'Enter') {
    emit('translate')
  }
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-lg overflow-hidden">
    <div class="p-4">
      <textarea
        :value="modelValue"
        @input="handleInput"
        @keydown="handleKeydown"
        :placeholder="placeholder"
        :disabled="isLoading"
        rows="8"
        class="w-full resize-none border-0 focus:ring-0 text-lg placeholder-gray-400 disabled:bg-gray-50"
      ></textarea>
    </div>

    <div class="border-t px-4 py-3 bg-gray-50 flex items-center justify-between">
      <span class="text-sm text-gray-500">
        {{ modelValue.length }} символов
      </span>

      <div class="flex gap-2">
        <button
          v-if="modelValue"
          @click="emit('clear')"
          class="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded transition"
        >
          Очистить
        </button>

        <button
          @click="emit('translate')"
          :disabled="isLoading || !modelValue.trim()"
          class="px-4 py-1.5 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-2"
        >
          <svg v-if="isLoading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ isLoading ? 'Перевод...' : 'Перевести' }}</span>
        </button>
      </div>
    </div>

    <div class="px-4 py-2 text-xs text-gray-400 border-t">
      Ctrl+Enter для быстрого перевода
    </div>
  </div>
</template>
