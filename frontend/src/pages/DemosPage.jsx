import { useState, useEffect, useRef } from 'react'
import MobileNav from '../components/MobileNav'
import CollapsibleSection from '../components/CollapsibleSection'
import RunthroughsSection from '../components/RunthroughsSection'

const GAME_MODULE_DEMO = {
  id: 'game_phase',
  title: 'Game Phase',
  description: 'A full Knives + Vote round from mid-game state. 11 real players.',
  cast: ['Aang', 'Michael Jackson', 'HAL 9000', 'Jo March', 'Lady Macbeth', 'Lady Diana', 'Morty Smith', 'Amy March', 'Benoit Blanc', 'Gollum', 'Buffy Summers'],
  locked: false,
}

function FinaleSection({ onStart, turnstileEnabled }) {
  const [fixtures, setFixtures] = useState([])
  const [modules, setModules] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [finaleType, setFinaleType] = useState(null)
  const [mode, setMode] = useState('watch')
  const [humanName, setHumanName] = useState('')
  const [turnstileToken, setTurnstileToken] = useState(null)
  const turnstileRef = useRef(null)

  useEffect(() => {
    fetch('/api/fixtures')
      .then(r => r.json())
      .then(data => {
        const finaleFixtures = data.fixtures.filter(f => f.finale)
        setFixtures(finaleFixtures)
        if (finaleFixtures.length > 0) setSelectedId(finaleFixtures[0].id)
      })
    fetch('/api/modules')
      .then(r => r.json())
      .then(data => {
        const finaleModules = data.modules.filter(m => m.finale)
        setModules(finaleModules)
        if (finaleModules.length > 0) setFinaleType(finaleModules[0].id)
      })
  }, [])

  useEffect(() => {
    if (!turnstileEnabled) return
    let widgetId = null
    const renderWidget = () => {
      if (turnstileRef.current) {
        widgetId = window.turnstile.render(turnstileRef.current, {
          sitekey: '0x4AAAAAADhT2idZkL-1k2P0',
          appearance: 'interaction-only',
          callback: (token) => setTurnstileToken(token),
          'expired-callback': () => setTurnstileToken(null),
          'error-callback': () => setTurnstileToken(null),
        })
      }
    }
    if (window.turnstile) renderWidget()
    else window.onTurnstileLoad = renderWidget
    return () => { if (widgetId !== null) window.turnstile?.remove(widgetId) }
  }, [turnstileEnabled])

  const canStart = (mode === 'watch' || humanName.trim()) && (!turnstileEnabled || turnstileToken)

  const selected = fixtures.find(f => f.id === selectedId)

  const handleSelect = (id) => {
    setSelectedId(id)
    setMode('watch')
    setHumanName('')
  }

  return (
    <div className="finale-section">
      <div className="finale-row-label">Fixtures</div>
      <div className="fixture-card-grid">
        {fixtures.map(fx => (
          <button
            key={fx.id}
            className={`fixture-card${selectedId === fx.id ? ' fixture-card--selected' : ''}`}
            onClick={() => handleSelect(fx.id)}
          >
            <span className="fixture-card-title">{fx.title}</span>
          </button>
        ))}
      </div>

      <div className="finale-row-label">Finale Level</div>
      <div className="fixture-card-grid fixture-card-grid--small">
        {modules.map(ft => (
          <button
            key={ft.id}
            className={`fixture-card${finaleType === ft.id ? ' fixture-card--selected' : ''}`}
            onClick={() => setFinaleType(ft.id)}
          >
            <span className="fixture-card-title">{ft.title}</span>
          </button>
        ))}
      </div>

      <div className="finale-row-label">Watch / Play</div>
      <div className="demo-card finale-controls">
        {selected?.alive?.length > 0 && (
          <div className="demo-cast">
            {selected.alive.map(name => (
              <span
                key={name}
                className={`demo-cast-chip demo-cast-chip--clickable${humanName === name && mode === 'play' ? ' demo-cast-chip--selected' : ''}`}
                onClick={() => { setMode('play'); setHumanName(name) }}
              >{name}</span>
            ))}
          </div>
        )}
        {mode === 'play' && (
          <input
            className="lobby-name-input lobby-name-input-wide"
            placeholder="Your name"
            value={humanName}
            onChange={e => setHumanName(e.target.value)}
            autoFocus
          />
        )}
        <div className="lobby-footer-btns">
          <div className="mode-switch">
            <button className={`mode-switch-opt${mode === 'watch' ? ' active' : ''}`} onClick={() => { setMode('watch'); setHumanName('') }}>Watch</button>
            <button className={`mode-switch-opt${mode === 'play' ? ' active' : ''}`} onClick={() => setMode('play')}>Play</button>
          </div>
          {turnstileEnabled && <div ref={turnstileRef} />}
          <button
            className="lobby-start-btn"
            disabled={!canStart}
            onClick={() => onStart({
              demoId: finaleType,
              humanName: mode === 'play' ? humanName.trim() : null,
              fixtureChoice: selectedId,
              turnstileToken,
            })}
          >
            Run Demo
          </button>
        </div>
      </div>
    </div>
  )
}

function DemoCard({ demo, onStart, turnstileEnabled }) {
  const [mode, setMode] = useState('watch')
  const [humanName, setHumanName] = useState('')
  const [turnstileToken, setTurnstileToken] = useState(null)
  const turnstileRef = useRef(null)

  useEffect(() => {
    if (!turnstileEnabled) return
    let widgetId = null
    const renderWidget = () => {
      if (turnstileRef.current) {
        widgetId = window.turnstile.render(turnstileRef.current, {
          sitekey: '0x4AAAAAADhT2idZkL-1k2P0',
          appearance: 'interaction-only',
          callback: (token) => setTurnstileToken(token),
          'expired-callback': () => setTurnstileToken(null),
          'error-callback': () => setTurnstileToken(null),
        })
      }
    }
    if (window.turnstile) renderWidget()
    else window.onTurnstileLoad = renderWidget
    return () => { if (widgetId !== null) window.turnstile?.remove(widgetId) }
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

  return (
    <div className="demo-card">
      <h2 className="demo-title">{demo.title}</h2>
      <p className="demo-description">{demo.description}</p>
      <div className="demo-cast">
        {demo.cast.map(name => (
          <span
            key={name}
            className={`demo-cast-chip demo-cast-chip--clickable${humanName === name && mode === 'play' ? ' demo-cast-chip--selected' : ''}`}
            onClick={() => { setMode('play'); setHumanName(name) }}
          >{name}</span>
        ))}
      </div>
      {mode === 'play' && (
        <input
          className="lobby-name-input lobby-name-input-wide"
          placeholder="Your name"
          value={humanName}
          onChange={e => setHumanName(e.target.value)}
          autoFocus
        />
      )}
      <div className="lobby-footer-btns">
        <div className="mode-switch">
          <button className={`mode-switch-opt${mode === 'watch' ? ' active' : ''}`} onClick={() => { setMode('watch'); setHumanName('') }}>Watch</button>
          <button className={`mode-switch-opt${mode === 'play' ? ' active' : ''}`} onClick={() => setMode('play')}>Play</button>
        </div>
        {turnstileEnabled && <div ref={turnstileRef} />}
        <button
          className="lobby-start-btn"
          disabled={!canStart}
          onClick={() => onStart({ demoId: demo.id, humanName: mode === 'play' ? humanName.trim() : null, fixtureChoice: null, turnstileToken })}
        >
          Run Demo
        </button>
      </div>
    </div>
  )
}

export default function DemosPage({ onStart }) {
  const [turnstileEnabled, setTurnstileEnabled] = useState(null)
  const [openSection, setOpenSection] = useState('finales')

  useEffect(() => {
    fetch('/api/flags')
      .then(r => r.json())
      .then(data => setTurnstileEnabled(data.turnstile_enabled))
  }, [])

  const toggleSection = (key) => setOpenSection(prev => (prev === key ? null : key))

  return (
    <div className="demos-page">
      <MobileNav />
      <h1 className="lobby-title">Demos</h1>
      <p className="demos-subtitle">Pre-loaded game scenarios from real playthroughs.</p>

      <CollapsibleSection title="Finales" open={openSection === 'finales'} onToggle={() => toggleSection('finales')}>
        <FinaleSection onStart={onStart} turnstileEnabled={turnstileEnabled} />
      </CollapsibleSection>

      <CollapsibleSection title="Game modules" open={openSection === 'game-modules'} onToggle={() => toggleSection('game-modules')}>
        <div className="demos-grid">
          <DemoCard demo={GAME_MODULE_DEMO} onStart={onStart} turnstileEnabled={turnstileEnabled} />
        </div>
      </CollapsibleSection>

      <RunthroughsSection open={openSection === 'runthroughs'} onToggle={() => toggleSection('runthroughs')} />
    </div>
  )
}
