// Zustand chat store — active session state
import { create } from 'zustand'
import type { Message } from '../types'

interface ChatState {
  sessionId: string
  messages: Message[]
  isStreaming: boolean
  topic: string
  setTopic: (topic: string) => void
  addMessage: (msg: Message) => void
  appendToLastMessage: (chunk: string) => void
  setStreaming: (streaming: boolean) => void
  newSession: () => void
}

const generateSessionId = () =>
  `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`

export const useChatStore = create<ChatState>((set) => ({
  sessionId: generateSessionId(),
  messages: [],
  isStreaming: false,
  topic: '',

  setTopic: (topic) => set({ topic }),

  addMessage: (msg) =>
    set((state) => ({ messages: [...state.messages, msg] })),

  appendToLastMessage: (chunk) =>
    set((state) => {
      const msgs = [...state.messages]
      if (msgs.length === 0) return state
      const last = msgs[msgs.length - 1]
      msgs[msgs.length - 1] = { ...last, content: last.content + chunk }
      return { messages: msgs }
    }),

  setStreaming: (streaming) => set({ isStreaming: streaming }),

  newSession: () =>
    set({ sessionId: generateSessionId(), messages: [], topic: '' }),
}))
