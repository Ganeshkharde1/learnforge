import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Brain, Zap, ArrowRight } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

export default function Auth() {
  const [userId, setUserId] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [error, setError] = useState('')
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!userId.trim()) {
      setError('User ID is required')
      return
    }
    login(userId.trim(), displayName.trim() || userId.trim())
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute inset-0 bg-gradient-glow pointer-events-none" />
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full bg-accent/5 blur-3xl pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="w-full max-w-md relative z-10"
      >
        {/* Brand */}
        <div className="text-center mb-10">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-accent/10 border border-accent/20 mb-4 shadow-glow-blue"
          >
            <Brain className="w-8 h-8 text-accent" />
          </motion.div>
          <h1 className="text-3xl font-mono font-bold text-text-primary">LearnForge AI</h1>
          <p className="text-text-secondary mt-2 text-sm">Intelligent Learning Companion</p>
          <div className="flex items-center justify-center gap-2 mt-3">
            <Zap className="w-3.5 h-3.5 text-accent" />
            <span className="text-xs font-mono text-text-muted">Powered by Gemini 1.5 Pro + Vertex AI</span>
          </div>
        </div>

        {/* Auth card */}
        <div className="card shadow-glow-blue">
          <h2 className="text-lg font-mono font-semibold mb-6 text-text-primary">Sign In</h2>

          <form onSubmit={handleSubmit} noValidate aria-label="Sign in form">
            <div className="space-y-4">
              <div>
                <label htmlFor="user-id" className="label">User ID *</label>
                <input
                  id="user-id"
                  type="text"
                  value={userId}
                  onChange={(e) => { setUserId(e.target.value); setError('') }}
                  placeholder="your_unique_user_id"
                  className="input font-mono"
                  autoComplete="username"
                  aria-required="true"
                  aria-describedby={error ? 'auth-error' : undefined}
                />
              </div>
              <div>
                <label htmlFor="display-name" className="label">Display Name (optional)</label>
                <input
                  id="display-name"
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="Your Name"
                  className="input"
                  autoComplete="name"
                />
              </div>

              {error && (
                <p id="auth-error" className="text-error text-sm font-mono" role="alert" aria-live="polite">
                  {error}
                </p>
              )}

              <button
                type="submit"
                id="signin-btn"
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                Enter LearnForge
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          <p className="text-text-muted text-xs mt-4 text-center font-mono">
            No password required — your User ID is your identity.
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-2 gap-3 mt-6">
          {[
            { label: 'Adaptive AI Tutor', desc: 'Socratic, streaming' },
            { label: 'RAG Doc Chat', desc: 'FAISS + Gemini' },
            { label: 'AI Quiz Engine', desc: 'Gemini evaluated' },
            { label: 'Video Generator', desc: 'Async pipeline' },
          ].map(({ label, desc }) => (
            <div key={label} className="bg-surface-2 rounded-lg p-3 border border-border">
              <div className="text-xs font-mono font-semibold text-text-primary">{label}</div>
              <div className="text-xs text-text-muted mt-0.5">{desc}</div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
