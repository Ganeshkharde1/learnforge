import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Upload, FileText, Trash2, Send, Loader2, FileSearch, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import { ragApi } from '../api/rag'
import type { DocumentInfo, Citation } from '../types'

function StatusIcon({ status }: { status: string }) {
  if (status === 'ready') return <CheckCircle className="w-3.5 h-3.5 text-success" />
  if (status === 'processing') return <Clock className="w-3.5 h-3.5 text-warning animate-spin" />
  return <AlertCircle className="w-3.5 h-3.5 text-error" />
}

export default function RAGChat() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState<{ answer: string; citations: Citation[] } | null>(null)
  const queryClient = useQueryClient()

  const { data: docs = [], isLoading: loadingDocs } = useQuery<DocumentInfo[]>({
    queryKey: ['rag-documents'],
    queryFn: ragApi.listDocuments,
  })

  const uploadMutation = useMutation({
    mutationFn: ragApi.upload,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['rag-documents'] }),
  })

  const queryMutation = useMutation({
    mutationFn: ({ q }: { q: string }) => ragApi.query(q),
    onSuccess: (data) => setAnswer(data),
  })

  const deleteMutation = useMutation({
    mutationFn: ragApi.deleteDocument,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['rag-documents'] }),
  })

  const onDrop = useCallback((accepted: File[]) => {
    accepted.forEach(f => uploadMutation.mutate(f))
  }, [uploadMutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxSize: 20 * 1024 * 1024,
  })

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      <div className="mb-6">
        <h2 className="text-2xl font-mono font-bold text-text-primary flex items-center gap-3">
          <FileSearch className="w-6 h-6 text-accent" /> Document Chat
        </h2>
        <p className="text-text-secondary text-sm mt-1">Upload your documents and ask questions using FAISS + Gemini RAG.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left — upload + docs */}
        <div className="space-y-4">
          {/* Drop zone */}
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
              isDragActive ? 'border-accent bg-accent/5' : 'border-border hover:border-border-bright'
            }`}
            role="button"
            aria-label="Upload documents"
          >
            <input {...getInputProps()} />
            <Upload className="w-8 h-8 text-text-muted mx-auto mb-3" />
            <p className="text-sm font-mono text-text-secondary">
              {isDragActive ? 'Drop files here...' : 'Drag & drop PDF, DOCX, TXT or MD'}
            </p>
            <p className="text-xs text-text-muted mt-1">Max 20MB per file</p>
            {uploadMutation.isPending && (
              <div className="flex items-center justify-center gap-2 mt-3 text-accent text-xs">
                <Loader2 className="w-3 h-3 animate-spin" /> Uploading...
              </div>
            )}
            {uploadMutation.isError && (
              <p className="text-error text-xs mt-2" role="alert">Upload failed: {String(uploadMutation.error)}</p>
            )}
          </div>

          {/* Document list */}
          <div className="space-y-2">
            <div className="label">Uploaded Documents ({docs.length})</div>
            {loadingDocs ? (
              <div className="space-y-2">{[1,2].map(i => <div key={i} className="h-12 skeleton rounded-lg" />)}</div>
            ) : docs.length === 0 ? (
              <p className="text-text-muted text-sm">No documents uploaded yet.</p>
            ) : (
              docs.map(doc => (
                <div key={doc.doc_id} className="flex items-center justify-between p-3 bg-surface-2 rounded-lg border border-border">
                  <div className="flex items-center gap-2 min-w-0">
                    <FileText className="w-4 h-4 text-text-muted shrink-0" />
                    <div className="min-w-0">
                      <p className="text-sm font-mono text-text-primary truncate">{doc.filename}</p>
                      <p className="text-xs text-text-muted">{doc.chunk_count} chunks</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusIcon status={doc.status} />
                    <button
                      onClick={() => deleteMutation.mutate(doc.doc_id)}
                      className="text-text-muted hover:text-error transition-colors p-1"
                      aria-label={`Delete ${doc.filename}`}
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right — Q&A */}
        <div className="space-y-4">
          <div>
            <label htmlFor="rag-question" className="label">Ask about your documents</label>
            <div className="flex gap-2">
              <input
                id="rag-question"
                value={question}
                onChange={e => setQuestion(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && question.trim() && queryMutation.mutate({ q: question })}
                placeholder="What does the document say about...?"
                className="input flex-1"
              />
              <button
                onClick={() => question.trim() && queryMutation.mutate({ q: question })}
                disabled={!question.trim() || queryMutation.isPending || docs.length === 0}
                className="btn-primary px-4"
                aria-label="Ask question"
              >
                {queryMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>
            {docs.length === 0 && <p className="text-xs text-text-muted mt-1">Upload documents first to enable querying.</p>}
          </div>

          {/* Answer */}
          <AnimatePresence>
            {answer && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-3">
                <div className="card">
                  <div className="label mb-2">Answer</div>
                  <div className="prose prose-sm prose-invert max-w-none prose-learnforge text-text-primary">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{answer.answer}</ReactMarkdown>
                  </div>
                </div>

                {answer.citations.length > 0 && (
                  <div className="card">
                    <div className="label mb-2">Sources ({answer.citations.length})</div>
                    <div className="space-y-2">
                      {answer.citations.map((c, i) => (
                        <div key={i} className="p-2 bg-surface-2 rounded-lg text-xs">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-mono text-accent">{c.filename}</span>
                            <span className="text-text-muted">p.{c.page} · {(c.score * 100).toFixed(0)}% match</span>
                          </div>
                          <p className="text-text-secondary">{c.chunk_text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
