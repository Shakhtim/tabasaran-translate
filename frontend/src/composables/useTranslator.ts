import { ref, computed } from 'vue'
import type { TranslationDirection, TranslateResponse, WordTranslation } from '../types'
import * as api from '../api/translator'

export function useTranslator() {
  const inputText = ref('')
  const direction = ref<TranslationDirection>('tab-rus')
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const result = ref<TranslateResponse | null>(null)
  const useLlm = ref(true)

  const sourceLang = computed(() =>
    direction.value === 'tab-rus' ? 'Табасаранский' : 'Русский'
  )

  const targetLang = computed(() =>
    direction.value === 'tab-rus' ? 'Русский' : 'Табасаранский'
  )

  const hasResult = computed(() => result.value !== null)

  const unknownWords = computed(() =>
    result.value?.words.filter(w => w.is_unknown) ?? []
  )

  async function translate() {
    if (!inputText.value.trim()) {
      error.value = 'Введите текст для перевода'
      return
    }

    isLoading.value = true
    error.value = null

    try {
      result.value = await api.translate(inputText.value, direction.value, useLlm.value)
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Ошибка перевода'
      result.value = null
    } finally {
      isLoading.value = false
    }
  }

  function toggleDirection() {
    direction.value = direction.value === 'tab-rus' ? 'rus-tab' : 'tab-rus'
    // Swap texts
    if (result.value) {
      inputText.value = result.value.translated_text
      result.value = null
    }
  }

  function clear() {
    inputText.value = ''
    result.value = null
    error.value = null
  }

  return {
    inputText,
    direction,
    isLoading,
    error,
    result,
    useLlm,
    sourceLang,
    targetLang,
    hasResult,
    unknownWords,
    translate,
    toggleDirection,
    clear
  }
}
