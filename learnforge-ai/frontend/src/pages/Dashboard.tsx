import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, BookOpen, Target, Flame, Brain, AlertTriangle, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { apiClient } from '../api/client'
import type { ProgressOverview, WeakArea } from '../types'
import { useAuthStore } from '../store/authStore'

function StatCard({ icon: Icon, label, value, color = 'text-accent' }: {
  icon: React.ElementType; label: string; value: string | number; color?: string
}) {
  return (
    <div className="card flex items-center gap-4">
      <div className={`w-10 h-10 rounded-lg bg-surface-2 flex items-center justify-center`}>
        <Icon className={`w-5 h-5 ${color}`} />
      </div>
      <div>
        <div className={`text-2xl font-mono font-bold ${color}`}>{value}</div>
        <div className="text-xs text-text-muted">{label}</div>
      </div>
    </div>
  )
}

function SkeletonCard() {
  return <div className="card h-24 skeleton" aria-busy="true" role="status" />
}

export default function Dashboard() {
  const { displayName } = useAuthStore()

  const { data: overview, isLoading: loadingOverview } = useQuery<ProgressOverview>({
    queryKey: ['progress-overview'],
    queryFn: async () => (await apiClient.get('/progress/overview')).data,
  })

  const { data: weakAreas, isLoading: loadingWeak } = useQuery<WeakArea[]>({
    queryKey: ['weak-areas'],
    queryFn: async () => (await apiClient.get('/progress/weak-areas')).data,
  })



  return (
    <div className="max-w-6xl mx-auto animate-fade-in space-y-8">
      {/* Greeting */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h2 className="text-2xl font-mono font-bold text-text-primary">
          Welcome back, <span className="text-accent">{displayName || 'Learner'}</span>
        </h2>
        <p className="text-text-secondary text-sm mt-1">Your learning command center.</p>
      </motion.div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {loadingOverview ? (
          <>
            <SkeletonCard /><SkeletonCard /><SkeletonCard /><SkeletonCard />
          </>
        ) : (
          <>
            <StatCard icon={BookOpen} label="Total Sessions" value={overview?.total_sessions ?? 0} />
            <StatCard icon={Target} label="Avg Quiz Score" value={`${overview?.avg_quiz_score ?? 0}%`} color="text-success" />
            <StatCard icon={Flame} label="Study Streak" value={`${overview?.study_streak ?? 0}d`} color="text-warning" />
            <StatCard icon={TrendingUp} label="Plan Progress" value={`${overview?.completion_pct ?? 0}%`} color="text-accent" />
          </>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Completion bar */}
        <div className="card">
          <h3 className="font-mono font-semibold text-sm mb-4">Module Completion</h3>
          {loadingOverview ? (
            <div className="h-32 skeleton rounded" />
          ) : (
            <ResponsiveContainer width="100%" height={140}>
              <BarChart data={[{ name: 'Modules', completed: overview?.completed_modules ?? 0, remaining: (overview?.total_modules ?? 0) - (overview?.completed_modules ?? 0) }]}>
                <XAxis dataKey="name" tick={{ fill: '#94A3B8', fontSize: 11 }} />
                <YAxis tick={{ fill: '#94A3B8', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1E293B', borderRadius: 8 }} />
                <Bar dataKey="completed" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Completed" />
                <Bar dataKey="remaining" fill="#1E293B" radius={[4, 4, 0, 0]} name="Remaining" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Weak areas */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-mono font-semibold text-sm">Weak Areas</h3>
            {weakAreas && weakAreas.length > 0 && (
              <span className="badge-red">{weakAreas.length} topics</span>
            )}
          </div>
          {loadingWeak ? (
            <div className="space-y-2">
              {[1,2,3].map(i => <div key={i} className="h-8 skeleton rounded" />)}
            </div>
          ) : weakAreas && weakAreas.length > 0 ? (
            <div className="space-y-2">
              {weakAreas.slice(0, 5).map(w => (
                <div key={w.topic} className="flex items-center justify-between p-2 bg-surface-2 rounded-lg">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-3.5 h-3.5 text-warning shrink-0" />
                    <span className="text-sm text-text-primary font-mono">{w.topic}</span>
                  </div>
                  {w.avg_score !== undefined && w.avg_score !== null && (
                    <span className="badge-red">{w.avg_score}%</span>
                  )}
                </div>
              ))}
              <Link to="/quiz" className="flex items-center gap-1 text-xs text-accent hover:text-accent-hover font-mono mt-2 transition-colors">
                Practice weak areas <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          ) : (
            <p className="text-text-muted text-sm">No weak areas detected yet. Take some quizzes!</p>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div>
        <h3 className="font-mono font-semibold text-sm mb-3 text-text-secondary">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { to: '/learn', label: 'Start Tutoring', icon: Brain, color: 'text-accent' },
            { to: '/plan', label: 'New Plan', icon: Target, color: 'text-success' },
            { to: '/rag', label: 'Upload Docs', icon: BookOpen, color: 'text-warning' },
            { to: '/quiz', label: 'Take Quiz', icon: TrendingUp, color: 'text-error' },
          ].map(({ to, label, icon: Icon, color }) => (
            <Link key={to} to={to} className="card-hover flex items-center gap-3 cursor-pointer">
              <Icon className={`w-5 h-5 ${color}`} />
              <span className="text-sm font-mono font-medium">{label}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
