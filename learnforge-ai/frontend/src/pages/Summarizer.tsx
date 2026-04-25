import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { AlignLeft, Loader2, Link2, Type } from 'lucide-react'
import { apiClient } from '../api/client'
import type { SummaryResult } from '../types'

export default function Summarizer() {
  const [mode, setMode] = useState<'text' | 'url'>('text')
  const [text, setText] = useState('')
  const [url, setUrl] = useState('')
  const [result, setResult] = useState<SummaryResult | null>(null)

  const textMutation = useMutation({
    mutationFn: async () => (await apiClient.post('/summary/text', { text })).data as SummaryResult,
    onSuccess: setResult,
  })

  const urlMutation = useMutation({
    mutationFn: async () => (await apiClient.post('/summary/url', { url })).data as SummaryResult,
    onSuccess: setResult,
  })

  const isPending = textMutation.isPending || urlMutation.isPending
  const error = textMutation.error || urlMutation.error

  const submit = () => {
    setResult(null)
    if (mode === 'text') textMutation.mutate()
    else urlMutation.mutate()
  }

  return (
    <div className="max-w-3xl mx-auto animate-fade-in space-y-6">
      <div>
        <h2 className="text-2xl font-mono font-bold text-text-primary flex items-center gap-3">
          <AlignLeft className="w-6 h-6 text-accent" /> AI Summarizer
        </h2>
        <p className="text-text-secondary text-sm mt-1">Paste text or enter a URL — get a structured summary powered by Gemini Flash.</p>
      </div>

      <div className="card space-y-4">
        {/* Mode tabs */}
        <div className="flex gap-2">
          <button onClick={() => setMode('text')} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-mono transition-all ${mode === 'text' ? 'bg-accent text-white' : 'bg-surface-2 text-text-secondary hover:text-text-primary'}`}>
            <Type className="w-3.5 h-3.5" /> Text
          </button>
          <button onClick={() => setMode('url')} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-mono transition-all ${mode === 'url' ? 'bg-accent text-white' : 'bg-surface-2 text-text-secondary hover:text-text-primary'}`}>
            <Link2 className="w-3.5 h-3.5" /> URL
          </button>
        </div>

        {mode === 'text' ? (
          <div>
            <label htmlFor="summary-text" className="label">Text to Summarize *</label>
            <textarea id="summary-text" value={text} onChange={e => setText(e.target.value)} placeholder="Paste any text, article, or notes here..." className="textarea" rows={8} aria-required="true" />
          </div>
        ) : (
          <div>
            <label htmlFor="summary-url" className="label">URL to Summarize *</label>
            <input id="summary-url" type="url" value={url} onChange={e => setUrl(e.target.value)} placeholder="https://example.com/article" className="input" aria-required="true" />
          </div>
        )}

        {error && <p className="text-error text-sm" role="alert">{String(error)}</p>}

        <button
          onClick={submit}
          disabled={isPending || (mode === 'text' ? text.length < 50 : !url.trim())}
          className="btn-primary w-full flex items-center justify-center gap-2"
          aria-busy={isPending}
        >
          {isPending ? <><Loader2 className="w-4 h-4 animate-spin" /> Summarizing...</> : '✨ Summarize →'}
        </button>
      </div>

      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
            <div className="card">
              <div className="label mb-2">Summary</div>
              <p className="text-text-primary">{result.summary}</p>
            </div>

            {result.key_concepts.length > 0 && (
              <div className="card">
                <div className="label mb-2">Key Concepts</div>
                <div className="flex flex-wrap gap-2">
                  {result.key_concepts.map(c => <span key={c} className="badge-blue">{c}</span>)}
                </div>
              </div>
            )}

            {result.definitions.length > 0 && (
              <div className="card">
                <div className="label mb-3">Definitions</div>
                <div className="space-y-2">
                  {result.definitions.map(d => (
                    <div key={d.term} className="p-3 bg-surface-2 rounded-lg">
                      <span className="font-mono font-semibold text-accent text-sm">{d.term}</span>
                      <p className="text-text-secondary text-sm mt-0.5">{d.definition}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.analogies.length > 0 && (
              <div className="card">
                <div className="label mb-2">Analogies</div>
                <ul className="space-y-2">
                  {result.analogies.map((a, i) => (
                    <li key={i} className="flex gap-2 text-sm text-text-secondary">
                      <span className="text-accent mt-0.5">›</span>{a}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
