import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { RUNTHROUGHS } from '../data/runthroughs'

export default function RunthroughPage({ onStart }) {
  const { runthroughId } = useParams()
  const navigate = useNavigate()
  const runthrough = RUNTHROUGHS.find(r => r.id === runthroughId)

  useEffect(() => {
    if (runthrough) onStart({ replayFile: runthrough.file })
  }, [runthrough, onStart])

  return (
    <div className="runthrough-page">
      <button className="runthrough-back" onClick={() => navigate('/')}>← Back</button>
      {runthrough ? (
        <div className="runthrough-detail">
          <h1 className="runthrough-title">{runthrough.name}</h1>
          <p className="runthrough-description">{runthrough.description}</p>
          <p className="runthrough-coming-soon">Loading replay…</p>
        </div>
      ) : (
        <div className="runthrough-detail">
          <h1 className="runthrough-title">Runthrough not found</h1>
          <p className="runthrough-description">No runthrough with id “{runthroughId}”.</p>
        </div>
      )}
    </div>
  )
}
