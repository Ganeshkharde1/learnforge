// Zustand plan store — active learning plan
import { create } from 'zustand'
import type { LearningPlan } from '../types'

interface PlanState {
  activePlan: LearningPlan | null
  setActivePlan: (plan: LearningPlan | null) => void
  updateModuleCompletion: (moduleIndex: number, completed: boolean) => void
}

export const usePlanStore = create<PlanState>((set) => ({
  activePlan: null,
  setActivePlan: (plan) => set({ activePlan: plan }),
  updateModuleCompletion: (moduleIndex, completed) =>
    set((state) => {
      if (!state.activePlan) return state
      const modules = [...state.activePlan.modules]
      modules[moduleIndex] = { ...modules[moduleIndex], completed }
      return { activePlan: { ...state.activePlan, modules } }
    }),
}))
