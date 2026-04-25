import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { CircleHelp, Loader2, CheckCircle, XCircle, RotateCcw } from 'lucide-react'
import { quizApi } from '../api/quiz'
import type { QuizQuestion, QuizResult } from '../types'

interface Answers { [questionId: string]: string }

function QuestionCard({ q, index, total, answer, onAnswer }: {
  q: QuizQuestion; index: number; total: number; answer?: string; onAnswer: (id: string, val: string) => void
}) {
  return (
    <motion.div
      key={q.id}
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      className="card space-y-4"
    >
      <div className="flex items-center justify-between">
        <span className="badge-blue">Q{index + 1} / {total}</span>
        <span className={`badge ${q.difficulty === 'easy' ? 'badge-green' : q.difficulty === 'hard' ? 'badge-red' : 'badge-yellow'}`}>
          {q.difficulty}
        </span>
      </div>
      <p className="font-mono text-text-primary font-medium">{q.question}</p>
      {q.type === 'mcq' && q.options ? (
        <div className="space-y-2">
          {q.options.map((opt, i) => (
            <button
              key={i}
              onClick={() => onAnswer(q.id, opt)}
              className={`w-full text-left p-3 rounded-lg border text-sm font-mono transition-all ${
                answer === opt
                  ? 'border-accent bg-accent/10 text-accent'
                  : 'border-border bg-surface-2 text-text-secondary hover:border-border-bright hover:text-text-primary'
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
      ) : q.type === 'true_false' ? (
        <div className="flex gap-3">
          {['True', 'False'].map(opt => (
            <button
              key={opt}
              onClick={() => onAnswer(q.id, opt)}
              className={`flex-1 p-3 rounded-lg border text-sm font-mono transition-all ${
                answer === opt ? 'border-accent bg-accent/10 text-accent' : 'border-border bg-surface-2 text-text-secondary hover:border-border-bright'
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
      ) : (
        <textarea
          value={answer || ''}
          onChange={e => onAnswer(q.id, e.target.value)}
          placeholder="Type your answer..."
          className="textarea w-full"
          rows={3}
          aria-label={`Answer for question ${index + 1}`}
        />
      )}
    </motion.div>
  )
}

function ScoreBoard({ result, onRetry }: { result: QuizResult; onRetry: () => void }) {
  return (
    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="space-y-4">
      <div className={`card text-center border ${result.score >= 80 ? 'border-success/30 bg-success/5' : result.score >= 50 ? 'border-warning/30 bg-warning/5' : 'border-error/30 bg-error/5'}`}>
        <div className={`text-5xl font-mono font-bold ${result.score >= 80 ? 'text-success' : result.score >= 50 ? 'text-warning' : 'text-error'}`}>
          {result.score}%
        </div>
        <p className="text-text-secondary text-sm mt-2">{result.correct_count} / {result.total_questions} correct</p>
        {result.weak_areas.length > 0 && (
          <div className="mt-3">
            <div className="label">Areas to Review</div>
            <div className="flex flex-wrap gap-2 justify-center mt-1">
              {result.weak_areas.map(a => <span key={a} className="badge-red">{a.slice(0, 40)}</span>)}
            </div>
          </div>
        )}
        <button onClick={onRetry} className="btn-secondary mt-4 flex items-center gap-2 mx-auto">
          <RotateCcw className="w-3.5 h-3.5" /> New Quiz
        </button>
      </div>

      <div className="space-y-3">
        {result.feedback.map(f => (
          <div key={f.question_id} className={`p-3 rounded-lg border ${f.correct ? 'border-success/20 bg-success/5' : 'border-error/20 bg-error/5'}`}>
            <div className="flex items-center gap-2 mb-1">
              {f.correct ? <CheckCircle className="w-4 h-4 text-success" /> : <XCircle className="w-4 h-4 text-error" />}
              <span className="text-xs font-mono text-text-muted">{f.question_id}</span>
              <span className="text-xs font-mono ml-auto">{(f.score * 100).toFixed(0)}%</span>
            </div>
            <p className="text-xs text-text-secondary">{f.explanation}</p>
          </div>
        ))}
      </div>
    </motion.div>
  )
}

export default function Quiz() {
  const [form, setForm] = useState({ topic: '', num_questions: 5, difficulty: 'medium', types: ['mcq'] })
  const [quizId, setQuizId] = useState<string | null>(null)
  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [answers, setAnswers] = useState<Answers>({})
  const [result, setResult] = useState<QuizResult | null>(null)

  const generateMutation = useMutation({
    mutationFn: quizApi.generate,
    onSuccess: (data) => { setQuizId(data.quiz_id); setQuestions(data.questions); setAnswers({}) },
  })

  const submitMutation = useMutation({
    mutationFn: () => quizApi.submit(quizId!, Object.entries(answers).map(([question_id, answer]) => ({ question_id, answer }))),
    onSuccess: setResult,
  })

  const reset = () => { setQuestions([]); setQuizId(null); setAnswers({}); setResult(null) }
  const answeredCount = Object.keys(answers).length

  if (result) return <ScoreBoard result={result} onRetry={reset} />

  return (
    <div className="max-w-2xl mx-auto animate-fade-in space-y-6">
      <div>
        <h2 className="text-2xl font-mono font-bold text-text-primary flex items-center gap-3">
          <CircleHelp className="w-6 h-6 text-accent" /> Quiz Engine
        </h2>
        <p className="text-text-secondary text-sm mt-1">AI-generated quizzes with Gemini semantic evaluation.</p>
      </div>

      {questions.length === 0 ? (
        <div className="card space-y-4">
          <div>
            <label htmlFor="quiz-topic" className="label">Topic *</label>
            <input id="quiz-topic" value={form.topic} onChange={e => setForm(f => ({ ...f, topic: e.target.value }))} placeholder="e.g. Python decorators" className="input" aria-required="true" />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label htmlFor="quiz-count" className="label">Questions</label>
              <select id="quiz-count" value={form.num_questions} onChange={e => setForm(f => ({ ...f, num_questions: +e.target.value }))} className="input">
                {[3,5,8,10].map(n => <option key={n}>{n}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="quiz-difficulty" className="label">Difficulty</label>
              <select id="quiz-difficulty" value={form.difficulty} onChange={e => setForm(f => ({ ...f, difficulty: e.target.value }))} className="input">
                <option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option>
              </select>
            </div>
            <div>
              <label htmlFor="quiz-types" className="label">Type</label>
              <select id="quiz-types" value={form.types[0]} onChange={e => setForm(f => ({ ...f, types: [e.target.value] }))} className="input">
                <option value="mcq">MCQ</option><option value="short_answer">Short Answer</option><option value="true_false">True/False</option>
              </select>
            </div>
          </div>
          {generateMutation.isError && <p className="text-error text-sm" role="alert">{String(generateMutation.error)}</p>}
          <button onClick={() => generateMutation.mutate(form)} disabled={!form.topic.trim() || generateMutation.isPending} className="btn-primary w-full flex items-center justify-center gap-2" aria-busy={generateMutation.isPending}>
            {generateMutation.isPending ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</> : 'Generate Quiz →'}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Progress bar */}
          <div className="h-1.5 bg-surface-2 rounded-full overflow-hidden">
            <motion.div className="h-full bg-accent rounded-full" animate={{ width: `${(answeredCount / questions.length) * 100}%` }} />
          </div>
          <p className="text-xs text-text-muted font-mono">{answeredCount} / {questions.length} answered</p>

          {questions.map((q, i) => (
            <QuestionCard key={q.id} q={q} index={i} total={questions.length} answer={answers[q.id]} onAnswer={(id, val) => setAnswers(a => ({ ...a, [id]: val }))} />
          ))}

          <div className="flex gap-3">
            <button onClick={reset} className="btn-secondary flex-1">Cancel</button>
            <button onClick={() => submitMutation.mutate()} disabled={answeredCount < questions.length || submitMutation.isPending} className="btn-primary flex-1 flex items-center justify-center gap-2" aria-busy={submitMutation.isPending}>
              {submitMutation.isPending ? <><Loader2 className="w-4 h-4 animate-spin" /> Evaluating...</> : 'Submit Quiz →'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
