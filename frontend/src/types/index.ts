export type TranslationDirection = 'tab-rus' | 'rus-tab'

export interface WordTranslation {
  word: string
  translations: string[]
  part_of_speech?: string
  confidence: number
  is_unknown: boolean
}

export interface TranslateResponse {
  original_text: string
  translated_text: string
  words: WordTranslation[]
  direction: TranslationDirection
  llm_used: boolean
}

export interface DictionaryEntry {
  id: number
  word: string
  word_normalized?: string
  root?: string
  part_of_speech?: string
  translations: string[]
  examples: { tabasaran: string; russian: string; source?: string }[]
  is_verified: boolean
}

export interface LookupResponse {
  query: string
  results: DictionaryEntry[]
  total: number
}

export interface SuggestResponse {
  query: string
  suggestions: string[]
}
