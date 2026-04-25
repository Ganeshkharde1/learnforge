import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { BookOpen, Loader2, RotateCcw, ThumbsUp, ThumbsDown, Meh } from 'lucide-react'
import { apiClient } from '../api/client'
import type { FlashcardDeck, Flashcard } from '../types'

function FlashCard({ card, onRate }: { card: Flashcard; onRate: (confidence: number) => void }) {
  const [flipped, setFlipped] = useState(false)
  const [rated, setRated] = useState(false)

  return (
    <div className="space-y-4">
      {/* 3D flip card */}
      <div
        className="relative h-56 cursor-pointer"
        style={{ perspective: '1000px' }}
        onClick={() => !rated && setFlipped(f => !f)}
        role="button"
        aria-label={flipped ? 'Show question' : 'Show answer'}
        tabIndex={0}
        onKeyDown={e => e.key === 'Enter' && setFlipped(f => !f)}
      >
        <motion.div
          animate={{ rotateY: flipped ? 180 : 0 }}
          transition={{ duration: 0.5, ease: 'easeInOut' }}
          style={{ transformStyle: 'preserve-3d' }}
          className="relative w-full h-full"
        >
          {/* Front */}
          <div
            className="absolute inset-0 card flex flex-col items-center justify-center text-center p-8"
            style={{ backfaceVisibility: 'hidden' }}
          >
            <div className="label mb-3">Question</div>
            <p className="font-mono text-text-primary text-lg font-semibold">{card.front}</p>
            <p className="text-text-muted text-xs mt-4">Click to reveal answer</p>
          </div>

          {/* Back */}
          <div
            className="absolute inset-0 card border-accent/20 bg-accent/5 flex flex-col items-center justify-center text-center p-8"
            style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
          >
            <div className="label mb-3 text-accent">Answer</div>
            <p className="text-text-primary">{card.back}</p>
          </div>
        </motion.div>
      </div>

      {/* Confidence rating */}
      <AnimatePresence>
        {flipped && !rated && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex justify-center gap-3">
            <p className="text-text-muted text-xs font-mono self-center">How well did you know it?</p>
            {[
              { icon: ThumbsDown, label: "Didn't know", confidence: 1, color: 'text-error', bg: 'hover:bg-error/10' },
              { icon: Meh, label: "Partially", confidence: 3, color: 'text-warning', bg: 'hover:bg-warning/10' },
              { icon: ThumbsUp, label: "Got it!", confidence: 5, color: 'text-success', bg: 'hover:bg-success/10' },
            ].map(({ icon: Icon, label, confidence, color, bg }) => (
              <button
                key={confidence}
                onClick={() => { setRated(true); onRate(confidence) }}
                className={`flex flex-col items-center gap-1 p-3 rounded-lg border border-border ${bg} transition-all`}
                aria-label={label}
              >
                <Icon className={`w-5 h-5 ${color}`} />
                <span className="text-xs text-text-muted">{label}</span>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function Flashcards() {
  const [form, setForm] = useState({ topic: '', num_cards: 10 })
  const [deck, setDeck] = useState<FlashcardDeck | null>(null)
  const [currentIdx, setCurrentIdx] = useState(0)

  const generateMutation = useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post('/flashcards/generate', form)
      return data as { deck_id: string; cards: Flashcard[] }
    },
    onSuccess: (data) => {
      setDeck({ deck_id: data.deck_id, deck_title: form.topic, topic: form.topic, cards: data.cards })
      setCurrentIdx(0)
    },
  })

  const rateMutation = useMutation({
    mutationFn: ({ deckId, cardId, confidence }: { deckId: string; cardId: string; confidence: number }) =>
      apiClient.patch(`/flashcards/${deckId}/review`, { card_id: cardId, confidence }),
    onSuccess: () => {
      setTimeout(() => setCurrentIdx(i => Math.min(i + 1, (deck?.cards.length || 1) - 1)), 600)
    },
  })

  const currentCard = deck?.cards[currentIdx]
  const progress = deck ? ((currentIdx + 1) / deck.cards.length) * 100 : 0

  return (
    <div className="max-w-2xl mx-auto animate-fade-in space-y-6">
      <div>
        <h2 className="text-2xl font-mono font-bold text-text-primary flex items-center gap-3">
          <BookOpen className="w-6 h-6 text-accent" /> Flashcards
        </h2>
        <p className="text-text-secondary text-sm mt-1">Spaced-repetition flashcards with Leitner system. Powered by Gemini Flash.</p>
      </div>

      {!deck ? (
        <div className="card space-y-4">
          <div>
            <label htmlFor="flash-topic" className="label">Topic *</label>
            <input id="flash-topic" value={form.topic} onChange={e => setForm(f => ({ ...f, topic: e.target.value }))} placeholder="e.g. React hooks" className="input" />
          </div>
          <div>
            <label htmlFor="flash-count" className="label">Number of Cards</label>
            <select id="flash-count" value={form.num_cards} onChange={e => setForm(f => ({ ...f, num_cards: +e.target.value }))} className="input">
              {[5,10,15,20].map(n => <option key={n}>{n}</option>)}
            </select>
          </div>
          {generateMutation.isError && <p className="text-error text-sm" role="alert">{String(generateMutation.error)}</p>}
          <button onClick={() => generateMutation.mutate()} disabled={!form.topic.trim() || generateMutation.isPending} className="btn-primary w-full flex items-center justify-center gap-2" aria-busy={generateMutation.isPending}>
            {generateMutation.isPending ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</> : 'Generate Deck →'}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Progress */}
          <div className="flex items-center justify-between text-xs font-mono text-text-muted mb-1">
            <span>{deck.deck_title}</span>
            <span>{currentIdx + 1} / {deck.cards.length}</span>
          </div>
          <div className="h-1.5 bg-surface-2 rounded-full overflow-hidden">
            <motion.div className="h-full bg-accent rounded-full" animate={{ width: `${progress}%` }} />
          </div>

          {currentCard && (
            <FlashCard
              key={currentCard.id}
              card={currentCard}
              onRate={confidence => rateMutation.mutate({
                deckId: deck.deck_id!,
                cardId: currentCard.id,
                confidence,
              })}
            />
          )}

          {currentIdx >= deck.cards.length - 1 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-8">
              <div className="text-2xl mb-2">🎉</div>
              <p className="font-mono font-semibold text-text-primary">Deck complete!</p>
              <button onClick={() => setDeck(null)} className="btn-secondary mt-3 flex items-center gap-2 mx-auto">
                <RotateCcw className="w-3.5 h-3.5" /> New Deck
              </button>
            </motion.div>
          )}
        </div>
      )}
    </div>
  )
}
