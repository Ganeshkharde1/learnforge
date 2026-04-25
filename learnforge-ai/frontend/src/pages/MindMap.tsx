import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import ReactFlow, { Background, Controls, MiniMap, Node, Edge } from 'reactflow'
import 'reactflow/dist/style.css'
import { Network, Loader2 } from 'lucide-react'
import { apiClient } from '../api/client'
import type { MindMapData } from '../types'

const NODE_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EF4444', '#EC4899']

function buildReactFlowData(data: MindMapData): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = data.nodes.map((n, i) => ({
    id: n.id,
    data: { label: n.label },
    position: { x: (n.level * 250) + (i % 4) * 60, y: (i * 100) % 600 },
    style: {
      background: NODE_COLORS[n.level % NODE_COLORS.length] + '20',
      border: `1px solid ${NODE_COLORS[n.level % NODE_COLORS.length]}50`,
      borderRadius: 12,
      color: '#F1F5F9',
      fontFamily: 'IBM Plex Mono, monospace',
      fontSize: n.level === 0 ? 14 : 12,
      fontWeight: n.level === 0 ? '700' : '500',
      padding: '8px 14px',
      minWidth: 120,
    },
  }))

  const edges: Edge[] = data.edges.map((e, i) => ({
    id: `e${i}`,
    source: e.source,
    target: e.target,
    style: { stroke: '#3B82F620', strokeWidth: 2 },
    animated: false,
  }))

  return { nodes, edges }
}

export default function MindMap() {
  const [topic, setTopic] = useState('')
  const [depth, setDepth] = useState(2)
  const [mapData, setMapData] = useState<{ nodes: Node[]; edges: Edge[] } | null>(null)

  const generateMutation = useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post('/mindmap/generate', { topic, depth })
      return data as MindMapData
    },
    onSuccess: (data) => setMapData(buildReactFlowData(data)),
  })

  return (
    <div className="max-w-5xl mx-auto animate-fade-in space-y-6">
      <div>
        <h2 className="text-2xl font-mono font-bold text-text-primary flex items-center gap-3">
          <Network className="w-6 h-6 text-accent" /> Mind Map Generator
        </h2>
        <p className="text-text-secondary text-sm mt-1">AI-generated interactive knowledge maps with React Flow.</p>
      </div>

      <div className="card">
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label htmlFor="mindmap-topic" className="label">Topic *</label>
            <input
              id="mindmap-topic"
              value={topic}
              onChange={e => setTopic(e.target.value)}
              placeholder="e.g. Machine Learning"
              className="input"
              onKeyDown={e => e.key === 'Enter' && topic.trim() && generateMutation.mutate()}
            />
          </div>
          <div>
            <label htmlFor="mindmap-depth" className="label">Depth</label>
            <select id="mindmap-depth" value={depth} onChange={e => setDepth(+e.target.value)} className="input w-24">
              <option value={1}>1 — Core</option>
              <option value={2}>2 — Subtopics</option>
              <option value={3}>3 — Detailed</option>
            </select>
          </div>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={!topic.trim() || generateMutation.isPending}
            className="btn-primary flex items-center gap-2"
            aria-label="Generate mind map"
          >
            {generateMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : '⚡ Generate'}
          </button>
        </div>
        {generateMutation.isError && <p className="text-error text-sm mt-2" role="alert">{String(generateMutation.error)}</p>}
      </div>

      <AnimatePresence>
        {mapData && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card p-0 overflow-hidden" style={{ height: 500 }}>
            <ReactFlow
              nodes={mapData.nodes}
              edges={mapData.edges}
              fitView
              nodesDraggable
              style={{ background: '#0A0A0F' }}
              aria-label={`Mind map for ${topic}`}
            >
              <Background color="#1E293B" gap={20} />
              <Controls style={{ background: '#111827', border: '1px solid #1E293B' }} />
              <MiniMap
                nodeColor={() => '#3B82F6'}
                style={{ background: '#111827', border: '1px solid #1E293B' }}
              />
            </ReactFlow>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
