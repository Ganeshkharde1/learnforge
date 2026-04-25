// API functions for video generation
import { apiClient } from './client'
import type { VideoJob } from '../types'

export const videoApi = {
  generate: async (concept: string, depth: 'brief' | 'detailed' = 'detailed'): Promise<{ job_id: string; status: string }> => {
    const { data } = await apiClient.post('/video/generate', { concept, depth })
    return data
  },

  status: async (job_id: string): Promise<{ status: string; video_url?: string; progress: number; error_message?: string }> => {
    const { data } = await apiClient.get(`/video/status/${job_id}`)
    return data
  },

  library: async (): Promise<VideoJob[]> => {
    const { data } = await apiClient.get('/video/library')
    return data
  },
}
