import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

import { AppShell } from './components/layout/AppShell'
import Auth from './pages/Auth'
import Dashboard from './pages/Dashboard'
import Learn from './pages/Learn'
import PlanGenerator from './pages/PlanGenerator'
import RAGChat from './pages/RAGChat'
import Quiz from './pages/Quiz'
import VideoGen from './pages/VideoGen'
import Flashcards from './pages/Flashcards'
import Summarizer from './pages/Summarizer'
import MindMap from './pages/MindMap'
import { useAuthStore } from './store/authStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 60 * 5,
      refetchOnWindowFocus: false,
    },
  },
})

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/auth" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            style: { background: '#111827', color: '#F1F5F9', border: '1px solid #1E293B', fontFamily: 'IBM Plex Mono' },
          }}
        />
        <Routes>
          <Route path="/auth" element={<Auth />} />
          <Route
            path="/"
            element={
              <RequireAuth>
                <AppShell />
              </RequireAuth>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="learn" element={<Learn />} />
            <Route path="plan" element={<PlanGenerator />} />
            <Route path="rag" element={<RAGChat />} />
            <Route path="quiz" element={<Quiz />} />
            <Route path="video" element={<VideoGen />} />
            <Route path="flashcards" element={<Flashcards />} />
            <Route path="summarizer" element={<Summarizer />} />
            <Route path="mindmap" element={<MindMap />} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
