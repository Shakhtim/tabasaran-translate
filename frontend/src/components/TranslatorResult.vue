<script setup lang="ts">
import { ref } from 'vue'
import type { TranslateResponse, WordTranslation } from '../types'
import WordCard from './WordCard.vue'

const props = defineProps<{
  result: TranslateResponse | null
  isLoading: boolean
  error: string | null
}>()

const selectedWord = ref<WordTranslation | null>(null)

function selectWord(word: WordTranslation) {
  if (!word.is_unknown) {
    selectedWord.value = word
  }
}

function closeWordCard() {
  selectedWord.value = null
}

function copyToClipboard() {
  if (props.result) {
    navigator.clipboard.writeText(props.result.translated_text)
  }
}

function getWordClass(word: WordTranslation): string {
  if (word.is_unknown) {
    return 'text-red-600 bg-red-50 cursor-help'
  }
  if (word.confidence < 0.8) {
    return 'text-yellow-700 bg-yellow-50 cursor-pointer hover:bg-yellow-100'
  }
  return 'cursor-pointer hover:bg-primary-50'
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-lg overflow-hidden">
    <div class="p-4 min-h-[200px]">
      <!-- Loading state -->
      <div v-if="isLoading" class="flex items-center justify-center h-full text-gray-400">
        <svg class="animate-spin h-8 w-8 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>Переводим...</span>
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="text-red-600 bg-red-50 p-4 rounded-lg">
        <p class="font-medium">Ошибка</p>
        <p class="text-sm mt-1">{{ error }}</p>
      </div>

      <!-- Empty state -->
      <div v-else-if="!result" class="text-gray-400 text-center py-12">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto mb-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
        </svg>
        <p>Перевод появится здесь</p>
      </div>

      <!-- Result -->
      <div v-else>
        <!-- Main translated text -->
        <p class="text-lg leading-relaxed">
          {{ result.translated_text }}
        </p>

        <!-- Word-by-word breakdown -->
        <div class="mt-6 pt-4 border-t">
          <p class="text-xs text-gray-500 mb-2">Пословный разбор (нажмите на слово):</p>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="(word, index) in result.words"
              :key="index"
              @click="selectWord(word)"
              :class="[
                'px-1.5 py-0.5 rounded text-sm transition',
                getWordClass(word)
              ]"
              :title="word.is_unknown ? 'Слово не найдено в словаре' : word.translations.join(', ')"
            >
              {{ word.word }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div v-if="result" class="border-t px-4 py-3 bg-gray-50 flex items-center justify-between">
      <div class="text-sm text-gray-500">
        <span v-if="result.words.some(w => w.is_unknown)" class="text-red-600">
          {{ result.words.filter(w => w.is_unknown).length }} слов не найдено
        </span>
      </div>

      <button
        @click="copyToClipboard"
        class="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded transition flex items-center gap-1"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        Копировать
      </button>
    </div>

    <!-- Word details modal -->
    <WordCard
      v-if="selectedWord"
      :word="selectedWord"
      @close="closeWordCard"
    />
  </div>
</template>
