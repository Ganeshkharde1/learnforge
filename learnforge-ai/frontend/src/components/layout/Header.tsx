import { useLocation } from 'react-router-dom'
import { Zap } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/learn': 'AI Tutor',
  '/plan': 'Learning Plan',
  '/rag': 'Document Chat',
  '/quiz': 'Quiz',
  '/video': 'Video Generator',
  '/flashcards': 'Flashcards',
  '/summarizer': 'Summarizer',
  '/mindmap': 'Mind Map',
}

export function Header() {
  const location = useLocation()
  const { displayName } = useAuthStore()
  const title = PAGE_TITLES[location.pathname] || 'LearnForge AI'

  return (
    <header className="h-14 bg-surface border-b border-border flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-2">
        <h1 className="font-mono font-semibold text-sm text-text-primary">{title}</h1>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-xs text-text-muted font-mono">
          <Zap className="w-3.5 h-3.5 text-accent" aria-hidden />
          <span>Gemini 1.5</span>
        </div>
        {displayName && (
          <div className="w-7 h-7 rounded-full bg-accent/20 border border-accent/30 flex items-center justify-center">
            <span className="text-xs font-mono font-bold text-accent">
              {displayName.charAt(0).toUpperCase()}
            </span>
          </div>
        )}
      </div>
    </header>
  )
}
