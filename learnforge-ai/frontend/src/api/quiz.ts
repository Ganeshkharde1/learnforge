// API functions for quiz endpoints
import { apiClient } from './client'
import type { Quiz, QuizResult, QuizHistoryItem } from '../types'

export const quizApi = {
  generate: async (params: {
    topic: string
    num_questions: number
    difficulty: string
    types: string[]
  }): Promise<{ quiz_id: string; questions: Quiz['questions'] }> => {
    const { data } = await apiClient.post('/quiz/generate', params)
    return data
  },

  submit: async (quiz_id: string, answers: { question_id: string; answer: string }[]): Promise<QuizResult> => {
    const { data } = await apiClient.post('/quiz/submit', { quiz_id, answers })
    return data
  },

  history: async (): Promise<QuizHistoryItem[]> => {
    const { data } = await apiClient.get('/quiz/history')
    return data
  },
}
