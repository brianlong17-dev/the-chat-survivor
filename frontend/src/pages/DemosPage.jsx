import { useState, useEffect, useRef } from 'react'

const DEMOS = [
  {
    id: 'reunion',
    title: 'Reunion Finale',
    description: 'The jury of eliminated players decides who wins, then a final split-or-steal.',
    fixtures: [
      {
        id: 'game_3',
        label: 'Game 3',
        description: 'Tied 39–39. Avatar Aang vs Morty Smith.',
        cast: ['Avatar Aang', 'Morty Smith', 'HAL 9000', 'Michael Jackson', 'Amy March', 'Benoit Blanc', 'Buffy Summers', 'Gollum', 'Lady Macbeth', 'Jo March', 'Lady Diana'],
      },
      {
        id: 'game_2',
        label: 'Game 2',
        description: 'Amy March (41) vs Lady Diana (48).',
        cast: ['Amy March', 'Lady Diana', 'Morty Smith', 'Lady Macbeth', 'HAL 9000', 'Jo March', 'Michael Jackson', 'Avatar Aang', 'Gollum', 'Buffy Summers', 'Benoit Blanc'],
      },
      {
        id: 'finn_lsp',
        label: 'Finn vs LSP',
        description: 'Tied 17–17. Finn vs Lumpy Space Princess.',
        cast: ['Finn', 'Lumpy Space Princess', 'BMO', 'Princess Bubblegum', 'Ice King', 'Jake the Dog'],
      },
      {
        id: 'adventure_time_pre_finale',
        label: 'Finn vs Jake',
        description: 'Jake (16) vs Finn (13).',
        cast: ['Finn', 'Jake the Dog', 'Princess Bubblegum', 'Ice King', 'Lumpy Space Princess', 'BMO'],
      },
      {
        id: 'brian_jake_pre_finale',
        label: 'Brian vs Finn',
        description: 'Finn (17) vs Brian (15).',
        cast: ['Finn the Human', 'Brian', 'Princess Bubblegum', 'Jake the Dog', 'Lumpy Space Princess', 'BMO'],
      },
      {
        id: 'aang_pb_pre_finale',
        label: 'Aang vs PB',
        description: 'Princess Bubblegum (18) vs Avatar Aang (11).',
        cast: ['Avatar Aang', 'Princess Bubblegum', 'Finn the Human', 'Jake the Dog', 'Lumpy Space Princess', 'BMO'],
      },
    ],
  },
  {
    id: 'pd_finale',
    title: "Prisoner's Dilemma Finale",
    description: 'Two finalists, one last split-or-steal. Trust, betrayal, or a tie.',
    fixtures: [
      {
        id: 'finn_lsp',
        label: 'Finn vs LSP',
        description: 'Tied 17–17. Finn vs Lumpy Space Princess.',
        cast: ['Finn', 'Lumpy Space Princess', 'BMO', 'Princess Bubblegum', 'Ice King', 'Jake the Dog'],
      },
      {
        id: 'adventure_time_pre_finale',
        label: 'Finn vs Jake',
        description: 'Jake (16) vs Finn (13).',
        cast: ['Finn', 'Jake the Dog', 'Princess Bubblegum', 'Ice King', 'Lumpy Space Princess', 'BMO'],
      },
      {
        id: 'brian_jake_pre_finale',
        label: 'Brian vs Finn',
        description: 'Finn (17) vs Brian (15).',
        cast: ['Finn the Human', 'Brian', 'Princess Bubblegum', 'Jake the Dog', 'Lumpy Space Princess', 'BMO'],
      },
      {
        id: 'aang_pb_pre_finale',
        label: 'Aang vs PB',
        description: 'Princess Bubblegum (18) vs Avatar Aang (11).',
        cast: ['Avatar Aang', 'Princess Bubblegum', 'Finn the Human', 'Jake the Dog', 'Lumpy Space Princess', 'BMO'],
      },
      {
        id: 'game_3',
        label: 'Game 3',
        description: 'Tied 39–39. Avatar Aang vs Morty Smith.',
        cast: ['Avatar Aang', 'Morty Smith', 'HAL 9000', 'Michael Jackson', 'Amy March', 'Benoit Blanc', 'Buffy Summers', 'Gollum', 'Lady Macbeth', 'Jo March', 'Lady Diana'],
      },
      {
        id: 'game_2',
        label: 'Game 2',
        description: 'Amy March (41) vs Lady Diana (48).',
        cast: ['Amy March', 'Lady Diana', 'Morty Smith', 'Lady Macbeth', 'HAL 9000', 'Jo March', 'Michael Jackson', 'Avatar Aang', 'Gollum', 'Buffy Summers', 'Benoit Blanc'],
      },
    ],
  },
  {
    id: 'game_phase',
    title: 'Game Phase',
    description: 'A full Knives + Vote round from mid-game state. 11 real players.',
    cast: ['Aang', 'Michael Jackson', 'HAL 9000', 'Jo March', 'Lady Macbeth', 'Lady Diana', 'Morty Smith', 'Amy March', 'Benoit Blanc', 'Gollum', 'Buffy Summers'],
    locked: false,
  },
]

function DemoCard({ demo, onStart, turnstileEnabled }) {
  const [mode, setMode] = useState('watch')
  const [humanName, setHumanName] = useState('')
  const [fixtureId, setFixtureId] = useState(demo.fixtures ? demo.fixtures[0].id : null)
  const [turnstileToken, setTurnstileToken] = useState(null)
  const turnstileRef = useRef(null)

  useEffect(() => {
    if (!turnstileEnabled) return
    let widgetId = null
    const renderWidget = () => {
      if (turnstileRef.current) {
        widgetId = window.turnstile.render(turnstileRef.current, {
          sitekey: '0x4AAAAAADhT2idZkL-1k2P0',
          size: 'invisible',
          callback: (token) => setTurnstileToken(token),
          'expired-callback': () => setTurnstileToken(null),
          'error-callback': () => setTurnstileToken(null),
        })
      }
    }
    if (window.turnstile) {
      renderWidget()
    } else {
      window.onTurnstileLoad = renderWidget
    }
    return () => {
      if (widgetId !== null) window.turnstile?.remove(widgetId)
    }
  }, [turnstileEnabled])

  const canStart = (mode === 'watch' || humanName.trim()) && (!turnstileEnabled || turnstileToken)

  if (demo.locked) {
    return (
      <div className="demo-card demo-card--locked">
        <span className="demo-locked-badge">Coming Soon</span>
        <h2 className="demo-title">{demo.title}</h2>
        <p className="demo-description">{demo.description}</p>
        <div className="demo-cast">
          {demo.cast.map(name => (
            <span key={name} className="demo-cast-chip">{name}</span>
          ))}
        </div>
      </div>
    )
  }

  const activeFixture = demo.fixtures ? demo.fixtures.find(f => f.id === fixtureId) : null
  const cast = activeFixture ? activeFixture.cast : demo.cast

  const handleFixtureChange = (id) => {
    setFixtureId(id)
    setMode('watch')
    setHumanName('')
  }

  return (
    <div className="demo-card">
      <h2 className="demo-title">{demo.title}</h2>
      <p className="demo-description">{demo.description}</p>
      {demo.fixtures && (
        <div className="demo-fixture-select">
          {demo.fixtures.map(fx => (
            <label key={fx.id} className="mode-opt">
              <input
                type="radio"
                name={`fixture-${demo.id}`}
                value={fx.id}
                checked={fixtureId === fx.id}
                onChange={() => handleFixtureChange(fx.id)}
              />
              {fx.label}
            </label>
          ))}
        </div>
      )}
      {activeFixture && (
        <p className="demo-fixture-description">{activeFixture.description}</p>
      )}
      <div className="demo-cast">
        {cast.map(name => (
          <span
            key={name}
            className={`demo-cast-chip demo-cast-chip--clickable${humanName === name && mode === 'play' ? ' demo-cast-chip--selected' : ''}`}
            onClick={() => { setMode('play'); setHumanName(name) }}
          >{name}</span>
        ))}
      </div>
      <div className="demo-mode">
        <label className="mode-opt">
          <input type="radio" name={`mode-${demo.id}`} value="watch" checked={mode === 'watch'} onChange={() => setMode('watch')} />
          Watch
        </label>
        <label className="mode-opt">
          <input type="radio" name={`mode-${demo.id}`} value="play" checked={mode === 'play'} onChange={() => setMode('play')} />
          Play as:
        </label>
        {mode === 'play' && (
          <input
            className="lobby-name-input"
            placeholder="Your name"
            value={humanName}
            onChange={e => setHumanName(e.target.value)}
            autoFocus
          />
        )}
      </div>
      {turnstileEnabled && <div ref={turnstileRef} />}
      <button
        className="lobby-start-btn"
        disabled={!canStart}
        onClick={() => onStart({ demoId: demo.id, humanName: mode === 'play' ? humanName.trim() : null, fixtureChoice: fixtureId, turnstileToken })}
      >
        Run Demo
      </button>
    </div>
  )
}

export default function DemosPage({ onStart }) {
  const [turnstileEnabled, setTurnstileEnabled] = useState(null)

  useEffect(() => {
    fetch('/api/flags')
      .then(r => r.json())
      .then(data => setTurnstileEnabled(data.turnstile_enabled))
  }, [])

  return (
    <div className="demos-page">
      <h1 className="lobby-title">Demos</h1>
      <p className="demos-subtitle">Pre-loaded game scenarios from real playthroughs.</p>
      <div className="demos-grid">
        {DEMOS.map(demo => (
          <DemoCard key={demo.id} demo={demo} onStart={onStart} turnstileEnabled={turnstileEnabled} />
        ))}
      </div>
    </div>
  )
}
