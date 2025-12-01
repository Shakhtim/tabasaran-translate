<script setup lang="ts">
import type { WordTranslation } from '../types'

defineProps<{
  word: WordTranslation
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <div
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @click.self="emit('close')"
  >
    <div class="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 overflow-hidden">
      <!-- Header -->
      <div class="bg-primary-600 text-white px-6 py-4 flex items-center justify-between">
        <h3 class="text-xl font-bold">{{ word.word }}</h3>
        <button
          @click="emit('close')"
          class="p-1 hover:bg-white/20 rounded transition"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6">
        <!-- Part of speech -->
        <div v-if="word.part_of_speech" class="mb-4">
          <span class="text-xs text-gray-500 uppercase tracking-wide">Часть речи</span>
          <p class="text-gray-700">{{ word.part_of_speech }}</p>
        </div>

        <!-- Translations -->
        <div class="mb-4">
          <span class="text-xs text-gray-500 uppercase tracking-wide">Переводы</span>
          <ul class="mt-1">
            <li
              v-for="(translation, index) in word.translations"
              :key="index"
              class="text-gray-700 py-1"
            >
              {{ translation }}
            </li>
          </ul>
        </div>

        <!-- Confidence -->
        <div class="mt-4 pt-4 border-t">
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">Уверенность:</span>
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                :class="[
                  'h-full rounded-full transition-all',
                  word.confidence >= 0.8 ? 'bg-green-500' :
                  word.confidence >= 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                ]"
                :style="{ width: `${word.confidence * 100}%` }"
              ></div>
            </div>
            <span class="text-xs text-gray-500">{{ Math.round(word.confidence * 100) }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
