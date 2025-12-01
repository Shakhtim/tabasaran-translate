import axios from 'axios'
import type {
  TranslationDirection,
  TranslateResponse,
  LookupResponse,
  SuggestResponse,
  DictionaryEntry
} from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export async function translate(
  text: string,
  direction: TranslationDirection = 'tab-rus',
  useLlm: boolean = true
): Promise<TranslateResponse> {
  const response = await api.post<TranslateResponse>('/translate', {
    text,
    direction,
    use_llm: useLlm
  })
  return response.data
}

export async function lookupWord(
  word: string,
  fuzzy: boolean = true
): Promise<LookupResponse> {
  const response = await api.get<LookupResponse>(`/dictionary/lookup/${encodeURIComponent(word)}`, {
    params: { fuzzy }
  })
  return response.data
}

export async function getSuggestions(
  query: string,
  limit: number = 10
): Promise<SuggestResponse> {
  const response = await api.get<SuggestResponse>('/dictionary/suggest', {
    params: { q: query, limit }
  })
  return response.data
}

export async function getWordDetails(wordId: number): Promise<DictionaryEntry> {
  const response = await api.get<DictionaryEntry>(`/dictionary/word/${wordId}`)
  return response.data
}

export async function searchByRussian(word: string): Promise<LookupResponse> {
  const response = await api.get<LookupResponse>('/dictionary/search/russian', {
    params: { word }
  })
  return response.data
}
