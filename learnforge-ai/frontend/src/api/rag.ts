// API functions for RAG (document upload + query)
import { apiClient } from './client'
import type { DocumentInfo, RAGResponse } from '../types'

export const ragApi = {
  upload: async (file: File): Promise<{ doc_id: string; status: string; chunk_count: number }> => {
    const form = new FormData()
    form.append('file', file)
    const { data } = await apiClient.post('/rag/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  query: async (question: string, doc_ids?: string[]): Promise<RAGResponse> => {
    const { data } = await apiClient.post('/rag/query', { question, doc_ids })
    return data
  },

  listDocuments: async (): Promise<DocumentInfo[]> => {
    const { data } = await apiClient.get('/rag/documents')
    return data
  },

  deleteDocument: async (doc_id: string) => {
    const { data } = await apiClient.delete(`/rag/documents/${doc_id}`)
    return data
  },
}
