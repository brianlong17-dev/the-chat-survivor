import { useState, useEffect, useRef } from 'react'
import MobileNav from '../components/MobileNav'
import CollapsibleSection from '../components/CollapsibleSection'
import RunthroughsSection from '../components/RunthroughsSection'

function FixtureModuleSection({ onStart, turnstileEnabled, finale, fixtureLabel, levelLabel, selectedId, setSelectedId, finaleType, setFinaleType }) {
  const [fixtures, setFixtures] = useState([])
  const [modules, setModules] = useState([])
  const [mode, setMode] = useState('watch')
  const [humanName, setHumanName] = useState('')
  const [turnstileToken, setTurnstileToken] = useState(null)
  const turnstileRef = useRef(null)

  useEffect(() => {
    fetch('/api/fixtures')
      .then(r => r.json())
      .then(data => {
        const matched = data.fixtures.filter(f => !!f.finale === finale)
        setFixtures(matched)
        if (matched.length > 0 && selectedId === null) setSelectedId(matched[0].id)
      })
    fetch('/api/modules')
      .then(r => r.json())
      .then(data => {
        const matched = data.modules.filter(m => !!m.finale === finale)
        setModules(matched)
        if (matched.length > 0 && finaleType === null) setFinaleType(matched[0].id)
      })
  }, [finale])

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

  const castDesc = selected && (
    finale
      ? (finaleType === 'reunion' ? selected.reunion_desc : selected.pd_desc)
      : selected.game_desc
  )

  const deadCast = selected ? selected.cast.filter(name => !selected.alive.includes(name)) : []

  const handleSelect = (id) => {
    setSelectedId(id)
    setMode('watch')
    setHumanName('')
  }

  return (
    <div className="finale-section">
      <div className="finale-row-label">{levelLabel}</div>
      <div className="fixture-card-grid fixture-card-grid--small">
        {modules.map(ft => (
          <button
            key={ft.id}
            className={`fixture-card${finaleType === ft.id ? ' fixture-card--selected' : ''}`}
            onClick={() => setFinaleType(ft.id)}
          >
            <span className="fixture-card-title">{ft.title}</span>
            {ft.description && <span className="fixture-card-desc">{ft.description}</span>}
          </button>
        ))}
      </div>

      <div className="finale-row-label">{fixtureLabel}</div>
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

      <div className="finale-row-label">Watch / Play</div>
      <div className="demo-card finale-controls">
        {castDesc && <div className="demo-cast-desc">{castDesc}</div>}
        {selected?.alive?.length > 0 && (
          <div className="demo-cast">
            {selected.alive.map(name => (
              <span
                key={name}
                className={`demo-cast-chip demo-cast-chip--clickable${humanName === name && mode === 'play' ? ' demo-cast-chip--selected' : ''}`}
                onClick={() => { setMode('play'); setHumanName(name) }}
              >{name}</span>
            ))}
            {finale && deadCast.length > 0 && (
              <>
                <span className="demo-cast-divider" />
                {deadCast.map(name => (
                  <span key={name} className="demo-cast-chip demo-cast-chip--dead">{name}</span>
                ))}
              </>
            )}
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

export default function DemosPage({ onStart }) {
  const [turnstileEnabled, setTurnstileEnabled] = useState(null)
  const [openSection, setOpenSection] = useState(null)
  const [finaleFixture, setFinaleFixture] = useState(() => localStorage.getItem('demo_finaleFixture') || null)
  const [finaleModule, setFinaleModule] = useState(() => localStorage.getItem('demo_finaleModule') || null)
  const [gameFixture, setGameFixture] = useState(() => localStorage.getItem('demo_gameFixture') || null)
  const [gameModule, setGameModule] = useState(() => localStorage.getItem('demo_gameModule') || null)

  useEffect(() => {
    fetch('/api/flags')
      .then(r => r.json())
      .then(data => setTurnstileEnabled(data.turnstile_enabled))
  }, [])

  const toggleSection = (key) => setOpenSection(prev => (prev === key ? null : key))

  const setFinaleFixturePersist = (v) => { setFinaleFixture(v); localStorage.setItem('demo_finaleFixture', v) }
  const setFinaleModulePersist = (v) => { setFinaleModule(v); localStorage.setItem('demo_finaleModule', v) }
  const setGameFixturePersist = (v) => { setGameFixture(v); localStorage.setItem('demo_gameFixture', v) }
  const setGameModulePersist = (v) => { setGameModule(v); localStorage.setItem('demo_gameModule', v) }

  return (
    <div className="demos-page">
      <MobileNav />
      <h1 className="lobby-title">Demos</h1>
      <p className="demos-subtitle">Pre-loaded game scenarios from real playthroughs.</p>

      <CollapsibleSection title="Finales" open={openSection === 'finales'} onToggle={() => toggleSection('finales')}>
        <FixtureModuleSection
          onStart={onStart}
          turnstileEnabled={turnstileEnabled}
          finale={true}
          fixtureLabel="Fixtures"
          levelLabel="Finale Level"
          selectedId={finaleFixture}
          setSelectedId={setFinaleFixturePersist}
          finaleType={finaleModule}
          setFinaleType={setFinaleModulePersist}
        />
      </CollapsibleSection>

      <CollapsibleSection title="Game modules" open={openSection === 'game-modules'} onToggle={() => toggleSection('game-modules')}>
        <FixtureModuleSection
          onStart={onStart}
          turnstileEnabled={turnstileEnabled}
          finale={false}
          fixtureLabel="Fixtures"
          levelLabel="Game Level"
          selectedId={gameFixture}
          setSelectedId={setGameFixturePersist}
          finaleType={gameModule}
          setFinaleType={setGameModulePersist}
        />
      </CollapsibleSection>

      <RunthroughsSection open={openSection === 'runthroughs'} onToggle={() => toggleSection('runthroughs')} />
    </div>
  )
}
