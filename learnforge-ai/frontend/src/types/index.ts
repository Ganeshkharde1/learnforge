// All TypeScript types for LearnForge AI frontend

// ── User ──────────────────────────────────────────────────────────────────────
export interface UserProfile {
  skill_level: 'beginner' | 'intermediate' | 'advanced'
  mastered_topics: string[]
  weak_topics: string[]
  total_sessions: number
  study_streak: number
  last_active?: string
}

// ── Chat ──────────────────────────────────────────────────────────────────────
export interface Message {
  role: 'user' | 'model'
  content: string
  timestamp?: string
}

export interface ChatSession {
  session_id: string
  topic?: string
  created_at?: string
  message_count: number
}

export interface ChatRequest {
  session_id: string
  message: string
  topic?: string
}

// ── Learning Plan ─────────────────────────────────────────────────────────────
export interface Resource {
  type: 'article' | 'video' | 'book' | 'practice'
  title: string
  url_hint: string
}

export interface Module {
  week: number
  title: string
  description: string
  topics: string[]
  resources: Resource[]
  milestones: string[]
  estimated_hours: number
  hands_on_project?: string
  completed: boolean
  completed_at?: string
}

export interface AssessmentCheckpoint {
  after_week: number
  assessment_type: 'quiz' | 'project' | 'review'
}

export interface FinalProject {
  title: string
  description: string
}

export interface LearningPlan {
  plan_id?: string
  goal: string
  summary: string
  prerequisites: string[]
  duration_weeks: number
  modules: Module[]
  assessment_checkpoints: AssessmentCheckpoint[]
  final_project?: FinalProject
  status: 'active' | 'completed' | 'paused'
  created_at?: string
}

export interface GeneratePlanRequest {
  goal: string
  current_level: 'beginner' | 'intermediate' | 'advanced'
  hours_per_week: number
  duration_weeks: number
}

// ── Quiz ──────────────────────────────────────────────────────────────────────
export interface QuizQuestion {
  id: string
  type: 'mcq' | 'true_false' | 'short_answer' | 'fill_blank' | 'code_complete'
  question: string
  options?: string[]
  correct_answer: string
  explanation: string
  difficulty: 'easy' | 'medium' | 'hard'
}

export interface Quiz {
  quiz_id?: string
  quiz_title: string
  questions: QuizQuestion[]
}

export interface AnswerFeedback {
  question_id: string
  correct: boolean
  explanation: string
  score: number
}

export interface QuizResult {
  score: number
  total_questions: number
  correct_count: number
  feedback: AnswerFeedback[]
  weak_areas: string[]
}

export interface QuizHistoryItem {
  quiz_id: string
  topic: string
  score: number
  total_questions: number
  created_at?: string
}

// ── RAG ───────────────────────────────────────────────────────────────────────
export interface DocumentInfo {
  doc_id: string
  filename: string
  status: 'processing' | 'ready' | 'error'
  uploaded_at?: string
  chunk_count: number
}

export interface Citation {
  doc_id: string
  filename: string
  chunk_text: string
  page: number
  score: number
}

export interface RAGResponse {
  answer: string
  citations: Citation[]
}

// ── Flashcards ────────────────────────────────────────────────────────────────
export interface Flashcard {
  id: string
  front: string
  back: string
  difficulty: 'easy' | 'medium' | 'hard'
  tags: string[]
  box?: number
  last_reviewed?: string
  next_review?: string
}

export interface FlashcardDeck {
  deck_id?: string
  deck_title: string
  topic: string
  cards: Flashcard[]
}

// ── Video ─────────────────────────────────────────────────────────────────────
export interface VideoJob {
  job_id: string
  concept: string
  status: 'queued' | 'generating' | 'ready' | 'error'
  video_url?: string
  progress: number
  created_at?: string
  error_message?: string
}

// ── Summary ───────────────────────────────────────────────────────────────────
export interface SummaryResult {
  summary: string
  key_concepts: string[]
  definitions: { term: string; definition: string }[]
  analogies: string[]
}

// ── Mind Map ──────────────────────────────────────────────────────────────────
export interface MindMapNode {
  id: string
  label: string
  level: number
}

export interface MindMapEdge {
  source: string
  target: string
}

export interface MindMapData {
  nodes: MindMapNode[]
  edges: MindMapEdge[]
}

// ── Progress ──────────────────────────────────────────────────────────────────
export interface ProgressOverview {
  total_sessions: number
  topics_covered: number
  avg_quiz_score: number
  study_streak: number
  plans_active: number
  total_modules: number
  completed_modules: number
  completion_pct: number
}

export interface WeakArea {
  topic: string
  avg_score?: number
  last_tested?: string
  recommended_resources: string[]
}

// ── API Error ─────────────────────────────────────────────────────────────────
export interface APIError {
  detail: string
}
