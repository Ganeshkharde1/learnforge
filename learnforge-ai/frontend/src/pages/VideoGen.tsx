import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Video, Loader2, Play, Clock, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react'
import { videoApi } from '../api/video'
import type { VideoJob } from '../types'

function StatusBadge({ status }: { status: string }) {
  const classes = {
    queued: 'badge-yellow', generating: 'badge-blue', ready: 'badge-green', error: 'badge-red'
  }
  return <span className={classes[status as keyof typeof classes] || 'badge-yellow'}>{status}</span>
}

function VideoJobCard({ job }: { job: VideoJob }) {
  return (
    <div className="card flex items-center gap-4">
      <div className="w-10 h-10 rounded-lg bg-surface-2 flex items-center justify-center">
        {job.status === 'ready' ? <CheckCircle2 className="w-5 h-5 text-success" /> :
         job.status === 'error' ? <AlertCircle className="w-5 h-5 text-error" /> :
         job.status === 'generating' ? <Loader2 className="w-5 h-5 text-accent animate-spin" /> :
         <Clock className="w-5 h-5 text-warning" />}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-mono font-semibold text-sm text-text-primary truncate">{job.concept}</p>
        <div className="flex items-center gap-2 mt-0.5">
          <StatusBadge status={job.status} />
          {job.status === 'generating' && (
            <div className="flex-1 h-1 bg-surface-2 rounded-full overflow-hidden">
              <motion.div className="h-full bg-accent rounded-full" animate={{ width: `${job.progress}%` }} />
            </div>
          )}
        </div>
      </div>
      {job.status === 'ready' && job.video_url && (
        <a href={job.video_url} target="_blank" rel="noopener noreferrer" className="btn-secondary flex items-center gap-2 py-1.5 text-xs shrink-0">
          <Play className="w-3 h-3" /> Watch
        </a>
      )}
    </div>
  )
}

export default function VideoGen() {
  const [concept, setConcept] = useState('')
  const [depth, setDepth] = useState<'brief' | 'detailed'>('detailed')
  const [activeJobId, setActiveJobId] = useState<string | null>(null)
  const [pollingEnabled, setPollingEnabled] = useState(false)

  const { data: library = [], refetch: refetchLibrary } = useQuery<VideoJob[]>({
    queryKey: ['video-library'],
    queryFn: videoApi.library,
  })

  const generateMutation = useMutation({
    mutationFn: () => videoApi.generate(concept, depth),
    onSuccess: (data) => {
      setActiveJobId(data.job_id)
      setPollingEnabled(true)
      refetchLibrary()
    },
  })

  // Poll job status every 5 seconds while generating
  const { data: jobStatus } = useQuery({
    queryKey: ['video-status', activeJobId],
    queryFn: () => videoApi.status(activeJobId!),
    enabled: !!activeJobId && pollingEnabled,
    refetchInterval: 5000,
  })

  useEffect(() => {
    if (jobStatus?.status === 'ready' || jobStatus?.status === 'error') {
      setPollingEnabled(false)
      refetchLibrary()
    }
  }, [jobStatus?.status])

  return (
    <div className="max-w-3xl mx-auto animate-fade-in space-y-8">
      <div>
        <h2 className="text-2xl font-mono font-bold text-text-primary flex items-center gap-3">
          <Video className="w-6 h-6 text-accent" /> Video Generator
        </h2>
        <p className="text-text-secondary text-sm mt-1">AI generates narrated explainer videos (script → slides → TTS → MP4) asynchronously.</p>
      </div>

      {/* Generate form */}
      <div className="card">
        <div className="space-y-4">
          <div>
            <label htmlFor="video-concept" className="label">Concept to Explain *</label>
            <input
              id="video-concept"
              value={concept}
              onChange={e => setConcept(e.target.value)}
              placeholder="e.g. Transformer attention mechanism"
              className="input"
              aria-required="true"
            />
          </div>
          <div>
            <label htmlFor="video-depth" className="label">Detail Level</label>
            <select
              id="video-depth"
              value={depth}
              onChange={e => setDepth(e.target.value as any)}
              className="input"
            >
              <option value="brief">Brief (~2 min)</option>
              <option value="detailed">Detailed (~5 min)</option>
            </select>
          </div>

          <div className="p-3 rounded-lg bg-warning/5 border border-warning/20 text-xs text-warning font-mono">
            ⚠️ Rate limited to 5 videos/hour. Generation takes 2-5 minutes. You'll be notified when ready.
          </div>

          {generateMutation.isError && <p className="text-error text-sm" role="alert">{String(generateMutation.error)}</p>}

          <button
            onClick={() => generateMutation.mutate()}
            disabled={!concept.trim() || generateMutation.isPending}
            className="btn-primary w-full flex items-center justify-center gap-2"
            aria-label="Generate video"
            aria-busy={generateMutation.isPending}
          >
            {generateMutation.isPending ? <><Loader2 className="w-4 h-4 animate-spin" /> Queueing...</> : '🎬 Generate Video →'}
          </button>
        </div>
      </div>

      {/* Active job status */}
      <AnimatePresence>
        {activeJobId && jobStatus && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card border-accent/20">
            <div className="flex items-center justify-between mb-3">
              <div className="label">Active Job</div>
              <StatusBadge status={jobStatus.status} />
            </div>
            {jobStatus.status === 'generating' && (
              <div className="space-y-2">
                <div className="h-2 bg-surface-2 rounded-full overflow-hidden">
                  <motion.div className="h-full bg-accent rounded-full" animate={{ width: `${jobStatus.progress}%` }} />
                </div>
                <p className="text-xs text-text-muted font-mono">{jobStatus.progress}% complete — building your video...</p>
              </div>
            )}
            {jobStatus.status === 'ready' && jobStatus.video_url && (
              <div className="mt-3">
                <video controls className="w-full rounded-lg border border-border" src={jobStatus.video_url} aria-label="Generated video">
                  Your browser does not support the video tag.
                </video>
              </div>
            )}
            {jobStatus.status === 'error' && (
              <p className="text-error text-sm">{jobStatus.error_message || 'Video generation failed.'}</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Video library */}
      {library.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className="label">Video Library ({library.length})</div>
            <button onClick={() => refetchLibrary()} className="text-xs text-text-muted hover:text-accent font-mono flex items-center gap-1">
              <RefreshCw className="w-3 h-3" /> Refresh
            </button>
          </div>
          <div className="space-y-3">
            {library.map(job => <VideoJobCard key={job.job_id} job={job} />)}
          </div>
        </div>
      )}
    </div>
  )
}
