import { useRef, useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { Send, Plus, Loader2, Bot, User } from 'lucide-react'
import { useChatStore } from '../store/chatStore'
import { useAuthStore } from '../store/authStore'
import { API_BASE } from '../api/client'
import type { Message } from '../types'

function TypingIndicator() {
  return (
    <div className="flex gap-1 p-3" aria-label="AI is typing" aria-live="polite">
      {[0, 1, 2].map(i => (
        <motion.div
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-accent"
          animate={{ y: [0, -6, 0] }}
          transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.15 }}
        />
      ))}
    </div>
  )
}

function MessageBubble({ msg, isStreaming }: { msg: Message; isStreaming?: boolean }) {
  const isUser = msg.role === 'user'
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${isUser ? 'bg-accent/20 border border-accent/30' : 'bg-surface-2 border border-border'}`}>
        {isUser ? <User className="w-3.5 h-3.5 text-accent" /> : <Bot className="w-3.5 h-3.5 text-text-secondary" />}
      </div>
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${isUser ? 'bg-accent text-white ml-auto' : 'bg-surface-2 border border-border text-text-primary'}`}>
        {isUser ? (
          <p>{msg.content}</p>
        ) : (
          <div className={`prose prose-sm prose-invert max-w-none prose-learnforge ${isStreaming ? 'streaming-cursor' : ''}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
              {msg.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default function Learn() {
  const { sessionId, messages, isStreaming, topic, setTopic, addMessage, appendToLastMessage, setStreaming, newSession } = useChatStore()
  const { userId } = useAuthStore()
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isStreaming])

  const sendMessage = async () => {
    if (!input.trim() || isStreaming || !userId) return

    const userMessage: Message = { role: 'user', content: input.trim() }
    addMessage(userMessage)
    setInput('')
    setStreaming(true)

    // Add empty model message that we'll stream into
    addMessage({ role: 'model', content: '' })

    try {
      const response = await fetch(`${API_BASE}/learn/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': userId,
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: input.trim(),
          topic: topic || undefined,
        }),
      })

      if (!response.ok) throw new Error('Chat request failed')

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) throw new Error('No response body')

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value)
        const lines = text.split('\n').filter(l => l.startsWith('data: '))

        for (const line of lines) {
          try {
            const data = JSON.parse(line.replace('data: ', ''))
            if (data.chunk) appendToLastMessage(data.chunk)
            if (data.done || data.error) break
          } catch {
            // ignore parse errors for partial chunks
          }
        }
      }
    } catch (err) {
      appendToLastMessage(`\n\n[Error: ${err instanceof Error ? err.message : 'Failed to connect'}]`)
    } finally {
      setStreaming(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col h-full" style={{ height: 'calc(100vh - 9rem)' }}>
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <input
            value={topic}
            onChange={e => setTopic(e.target.value)}
            placeholder="Current topic (optional)..."
            className="input text-sm py-1.5 px-3 w-56"
            aria-label="Learning topic"
          />
        </div>
        <button onClick={newSession} className="btn-secondary flex items-center gap-2 py-1.5 text-sm" aria-label="New chat session">
          <Plus className="w-3.5 h-3.5" /> New Session
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1" role="log" aria-label="Chat messages" aria-live="polite">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-16">
            <div className="w-12 h-12 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center mb-4">
              <Bot className="w-6 h-6 text-accent" />
            </div>
            <h3 className="font-mono font-semibold text-text-primary">Ask me anything</h3>
            <p className="text-text-muted text-sm mt-1">I'm your adaptive AI tutor powered by Gemini 1.5 Pro</p>
          </div>
        )}

        <AnimatePresence>
          {messages.map((msg, i) => (
            <MessageBubble
              key={i}
              msg={msg}
              isStreaming={isStreaming && i === messages.length - 1 && msg.role === 'model'}
            />
          ))}
        </AnimatePresence>

        {isStreaming && messages[messages.length - 1]?.role === 'user' && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="mt-4 flex gap-3 items-end">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask me anything... (Enter to send, Shift+Enter for newline)"
          className="textarea flex-1 min-h-[52px] max-h-32 py-3 text-sm resize-none"
          disabled={isStreaming}
          rows={1}
          aria-label="Message input"
        />
        <button
          onClick={sendMessage}
          disabled={isStreaming || !input.trim()}
          className="btn-primary p-3 shrink-0"
          aria-label="Send message"
        >
          {isStreaming ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </div>
    </div>
  )
}
