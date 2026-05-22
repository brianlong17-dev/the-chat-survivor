export default function Scoreboard({ scores, evicted }) {
  if (scores == null) return null
  const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1])
  return (
    <div className="scoreboard">
      <h2 className="scoreboard-title">Scores</h2>
      <ol className="score-list">
        {sorted.length === 0 ? (
          <li className="score-row score-empty">🪦</li>
        ) : sorted.map(([name, score], i) => (
          <li key={name} className="score-row">
            <span className="score-rank">{i + 1}</span>
            <span className="score-name">{name}</span>
            <span className="score-pts">{score}</span>
          </li>
        ))}
      </ol>
      <div className="graveyard">
        <h2 className="scoreboard-title">Graveyard</h2>
        {evicted.map(name => (
          <div key={name} className="evicted-row"> ☠ {name}</div>
        ))}
      </div>
    </div>
  )
}
