import { NavLink, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Brain, LayoutDashboard, MessageSquare, Map, FileSearch,
  CircleHelp, Video, BookOpen, AlignLeft, Network, ChevronLeft, ChevronRight, LogOut
} from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '../../store/authStore'

const NAV_ITEMS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/learn', icon: MessageSquare, label: 'AI Tutor' },
  { to: '/plan', icon: Map, label: 'Learning Plan' },
  { to: '/rag', icon: FileSearch, label: 'Doc Chat' },
  { to: '/quiz', icon: CircleHelp, label: 'Quiz' },
  { to: '/video', icon: Video, label: 'Video Gen' },
  { to: '/flashcards', icon: BookOpen, label: 'Flashcards' },
  { to: '/summarizer', icon: AlignLeft, label: 'Summarizer' },
  { to: '/mindmap', icon: Network, label: 'Mind Map' },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const { logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/auth')
  }

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 64 : 240 }}
      transition={{ duration: 0.25, ease: 'easeInOut' }}
      className="flex flex-col h-full bg-surface border-r border-border relative z-10 shrink-0 overflow-hidden"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-border">
        <div className="w-8 h-8 rounded-lg bg-accent/20 border border-accent/30 flex items-center justify-center shrink-0">
          <Brain className="w-4 h-4 text-accent" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.span
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="font-mono font-bold text-sm text-text-primary whitespace-nowrap"
            >
              LearnForge AI
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto" role="navigation" aria-label="Main navigation">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `nav-item ${isActive ? 'active' : ''}`
            }
            aria-label={collapsed ? label : undefined}
          >
            <Icon className="w-4 h-4 shrink-0" />
            <AnimatePresence>
              {!collapsed && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="text-sm whitespace-nowrap"
                >
                  {label}
                </motion.span>
              )}
            </AnimatePresence>
          </NavLink>
        ))}
      </nav>

      {/* User + Logout */}
      <div className="px-2 py-3 border-t border-border space-y-1">
        <button
          onClick={handleLogout}
          className="nav-item w-full text-left text-error hover:text-error hover:bg-error/10"
          aria-label="Logout"
        >
          <LogOut className="w-4 h-4 shrink-0" />
          {!collapsed && <span className="text-sm">Logout</span>}
        </button>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-16 w-6 h-6 bg-surface border border-border rounded-full
                   flex items-center justify-center text-text-muted hover:text-text-primary
                   hover:border-accent transition-colors z-20"
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? (
          <ChevronRight className="w-3 h-3" />
        ) : (
          <ChevronLeft className="w-3 h-3" />
        )}
      </button>
    </motion.aside>
  )
}
