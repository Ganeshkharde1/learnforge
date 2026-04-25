import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Map, Loader2, ChevronDown, ChevronUp, CheckCircle2, Circle } from 'lucide-react'
import { planApi } from '../api/plan'
import type { Module } from '../types'
import { usePlanStore } from '../store/planStore'

function ModuleCard({ module, index, planId }: { module: Module; index: number; planId: string }) {
  const [open, setOpen] = useState(false)
  const { updateModuleCompletion } = usePlanStore()

  const toggleComplete = async () => {
    const newVal = !module.completed
    updateModuleCompletion(index, newVal)
    await planApi.updateProgress(planId, index, newVal)
  }

  return (
    <div className={`card border transition-colors ${module.completed ? 'border-success/30 bg-success/5' : 'border-border'}`}>
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setOpen(!open)}
        role="button"
        aria-expanded={open}
        aria-controls={`module-${index}`}
      >
        <div className="flex items-center gap-3">
          <button
            onClick={e => { e.stopPropagation(); toggleComplete() }}
            className="shrink-0"
            aria-label={module.completed ? 'Mark incomplete' : 'Mark complete'}
          >
            {module.completed
              ? <CheckCircle2 className="w-5 h-5 text-success" />
              : <Circle className="w-5 h-5 text-text-muted hover:text-accent transition-colors" />
            }
          </button>
          <div>
            <div className="text-xs text-text-muted font-mono">Week {module.week}</div>
            <div className="font-mono font-semibold text-sm text-text-primary">{module.title}</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-text-muted">{module.estimated_hours}h</span>
          {open ? <ChevronUp className="w-4 h-4 text-text-muted" /> : <ChevronDown className="w-4 h-4 text-text-muted" />}
        </div>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            id={`module-${index}`}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="pt-4 mt-4 border-t border-border space-y-3">
              <p className="text-sm text-text-secondary">{module.description}</p>
              <div>
                <div className="label">Topics</div>
                <div className="flex flex-wrap gap-2">
                  {module.topics.map(t => <span key={t} className="badge-blue">{t}</span>)}
                </div>
              </div>
              {module.milestones.length > 0 && (
                <div>
                  <div className="label">Milestones</div>
                  <ul className="space-y-1">
                    {module.milestones.map(m => (
                      <li key={m} className="text-sm text-text-secondary flex gap-2">
                        <span className="text-accent mt-0.5">›</span>{m}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {module.hands_on_project && (
                <div className="p-3 rounded-lg bg-accent/5 border border-accent/20">
                  <div className="label text-accent">Project</div>
                  <p className="text-sm text-text-primary">{module.hands_on_project}</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function PlanGenerator() {
  const [form, setForm] = useState({
    goal: '', current_level: 'beginner' as const,
    hours_per_week: 10, duration_weeks: 4
  })
  const { activePlan, setActivePlan } = usePlanStore()

  const { mutate, isPending, error } = useMutation({
    mutationFn: planApi.generate,
    onSuccess: ({ plan }) => setActivePlan(plan),
  })

  return (
    <div className="max-w-3xl mx-auto animate-fade-in space-y-8">
      <div>
        <h2 className="text-2xl font-mono font-bold text-text-primary flex items-center gap-3">
          <Map className="w-6 h-6 text-accent" /> Learning Plan Generator
        </h2>
        <p className="text-text-secondary text-sm mt-1">AI generates a structured week-by-week plan for any learning goal.</p>
      </div>

      {/* Form */}
      <div className="card">
        <div className="space-y-4">
          <div>
            <label htmlFor="plan-goal" className="label">Learning Goal *</label>
            <textarea
              id="plan-goal"
              value={form.goal}
              onChange={e => setForm(f => ({ ...f, goal: e.target.value }))}
              placeholder="e.g. Learn Kubernetes in 3 weeks, I know Docker basics"
              className="textarea"
              rows={3}
              aria-required="true"
            />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label htmlFor="plan-level" className="label">Current Level</label>
              <select
                id="plan-level"
                value={form.current_level}
                onChange={e => setForm(f => ({ ...f, current_level: e.target.value as any }))}
                className="input"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
            <div>
              <label htmlFor="plan-hours" className="label">Hours/Week</label>
              <input
                id="plan-hours"
                type="number"
                value={form.hours_per_week}
                onChange={e => setForm(f => ({ ...f, hours_per_week: +e.target.value }))}
                className="input"
                min={1} max={60}
              />
            </div>
            <div>
              <label htmlFor="plan-weeks" className="label">Duration (weeks)</label>
              <input
                id="plan-weeks"
                type="number"
                value={form.duration_weeks}
                onChange={e => setForm(f => ({ ...f, duration_weeks: +e.target.value }))}
                className="input"
                min={1} max={52}
              />
            </div>
          </div>

          {error && <p className="text-error text-sm font-mono" role="alert">{String(error)}</p>}

          <button
            onClick={() => mutate(form)}
            disabled={!form.goal.trim() || isPending}
            className="btn-primary w-full flex items-center justify-center gap-2"
            aria-label="Generate learning plan"
            aria-busy={isPending}
          >
            {isPending ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</> : 'Generate Plan →'}
          </button>
        </div>
      </div>

      {/* Plan result */}
      <AnimatePresence>
        {activePlan && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
            <div className="card border-accent/20 bg-accent/5">
              <h3 className="font-mono font-bold text-text-primary">{activePlan.goal}</h3>
              <p className="text-text-secondary text-sm mt-1">{activePlan.summary}</p>
              <div className="flex gap-3 mt-3">
                <span className="badge-blue">{activePlan.duration_weeks} weeks</span>
                <span className="badge-blue">{activePlan.modules.length} modules</span>
                {activePlan.prerequisites.length > 0 && (
                  <span className="badge-yellow">Needs: {activePlan.prerequisites.slice(0, 2).join(', ')}</span>
                )}
              </div>
            </div>

            <div className="space-y-3">
              {activePlan.modules.map((mod, i) => (
                <ModuleCard key={i} module={mod} index={i} planId={activePlan.plan_id || ''} />
              ))}
            </div>

            {activePlan.final_project && (
              <div className="card border-warning/20 bg-warning/5">
                <div className="label text-warning">Final Project</div>
                <div className="font-mono font-semibold">{activePlan.final_project.title}</div>
                <p className="text-sm text-text-secondary mt-1">{activePlan.final_project.description}</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
