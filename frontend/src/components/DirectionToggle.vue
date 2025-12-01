<script setup lang="ts">
import type { TranslationDirection } from '../types'

defineProps<{
  direction: TranslationDirection
  sourceLang: string
  targetLang: string
}>()

const emit = defineEmits<{
  toggle: []
}>()
</script>

<template>
  <div class="flex items-center justify-center gap-4">
    <span class="text-lg font-medium text-gray-700 min-w-[120px] text-right">
      {{ sourceLang }}
    </span>

    <button
      @click="emit('toggle')"
      class="p-2 rounded-full bg-white shadow-md hover:shadow-lg transition-all hover:scale-110 active:scale-95"
      title="Поменять направление"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
      </svg>
    </button>

    <span class="text-lg font-medium text-gray-700 min-w-[120px]">
      {{ targetLang }}
    </span>
  </div>
</template>
