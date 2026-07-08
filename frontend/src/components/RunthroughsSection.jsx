import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { RUNTHROUGHS } from '../data/runthroughs'
import CollapsibleSection from './CollapsibleSection'

export default function RunthroughsSection({ open, onToggle }) {
  const [copiedId, setCopiedId] = useState(null)
  const navigate = useNavigate()

  const copyLink = async (id) => {
    const url = `${window.location.origin}/runthrough/${id}`
    try {
      await navigator.clipboard.writeText(url)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 1500)
    } catch {
      setCopiedId(null)
    }
  }

  return (
    <CollapsibleSection title="Completed Game Runs" open={open} onToggle={onToggle}>
      <div className="demos-grid">
        {RUNTHROUGHS.map(r => (
          <div key={r.id} className="demo-card runthrough-card">
            <div className="demo-title">{r.name}</div>
            <p className="demo-description">{r.description}</p>
            <div className="runthrough-card-actions">
              <button className="runthrough-watch-btn" onClick={() => navigate(`/runthrough/${r.id}`)}>
                Watch
              </button>
              <button className="runthrough-copy-btn" onClick={() => copyLink(r.id)}>
                {copiedId === r.id ? 'Copied!' : 'Copy link'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </CollapsibleSection>
  )
}
