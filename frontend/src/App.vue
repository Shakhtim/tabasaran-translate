<script setup lang="ts">
import { useTranslator } from './composables/useTranslator'
import TranslatorInput from './components/TranslatorInput.vue'
import TranslatorResult from './components/TranslatorResult.vue'
import DirectionToggle from './components/DirectionToggle.vue'

const {
  inputText,
  direction,
  isLoading,
  error,
  result,
  useLlm,
  sourceLang,
  targetLang,
  translate,
  toggleDirection,
  clear
} = useTranslator()
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-5xl mx-auto px-4 py-4">
        <h1 class="text-2xl font-bold text-primary-800">
          Табасаранско-русский переводчик
        </h1>
        <p class="text-sm text-gray-500 mt-1">
          Перевод между табасаранским и русским языками
        </p>
      </div>
    </header>

    <!-- Main content -->
    <main class="max-w-5xl mx-auto px-4 py-8">
      <!-- Direction toggle -->
      <DirectionToggle
        :direction="direction"
        :source-lang="sourceLang"
        :target-lang="targetLang"
        @toggle="toggleDirection"
      />

      <!-- Translation panels -->
      <div class="grid md:grid-cols-2 gap-4 mt-6">
        <!-- Input -->
        <TranslatorInput
          v-model="inputText"
          :placeholder="`Введите текст на ${sourceLang.toLowerCase()} языке...`"
          :is-loading="isLoading"
          @translate="translate"
          @clear="clear"
        />

        <!-- Result -->
        <TranslatorResult
          :result="result"
          :is-loading="isLoading"
          :error="error"
        />
      </div>

      <!-- Options -->
      <div class="mt-4 flex items-center gap-4">
        <label class="flex items-center gap-2 text-sm text-gray-600">
          <input
            type="checkbox"
            v-model="useLlm"
            class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span>Использовать ИИ для контекстного перевода</span>
        </label>

        <span v-if="result?.llm_used" class="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
          ИИ использован
        </span>
      </div>
    </main>

    <!-- Footer -->
    <footer class="fixed bottom-0 left-0 right-0 bg-white border-t py-3">
      <div class="max-w-5xl mx-auto px-4 text-center text-sm text-gray-500">
        Табасаранский язык — один из языков Дагестана
      </div>
    </footer>
  </div>
</template>
