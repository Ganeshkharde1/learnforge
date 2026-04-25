// Zustand auth store — user identity (X-User-ID based, no Firebase)
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  userId: string | null
  displayName: string | null
  isAuthenticated: boolean
  login: (userId: string, displayName: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      userId: null,
      displayName: null,
      isAuthenticated: false,
      login: (userId, displayName) =>
        set({ userId, displayName, isAuthenticated: true }),
      logout: () =>
        set({ userId: null, displayName: null, isAuthenticated: false }),
    }),
    { name: 'learnforge-auth' }
  )
)
