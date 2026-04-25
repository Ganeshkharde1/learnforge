// API functions for learning plan endpoints
import { apiClient } from './client'
import type { GeneratePlanRequest, LearningPlan } from '../types'

export const planApi = {
  generate: async (req: GeneratePlanRequest): Promise<{ plan_id: string; plan: LearningPlan }> => {
    const { data } = await apiClient.post('/plan/generate', req)
    return data
  },

  list: async (): Promise<LearningPlan[]> => {
    const { data } = await apiClient.get('/plan/')
    return data
  },

  updateProgress: async (planId: string, moduleIndex: number, completed: boolean) => {
    const { data } = await apiClient.patch(`/plan/${planId}/progress`, {
      module_index: moduleIndex,
      completed,
    })
    return data
  },
}
