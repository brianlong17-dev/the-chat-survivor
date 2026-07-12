import { useState, useEffect, useRef, Fragment } from 'react'
import MobileNav from '../components/MobileNav'
import CollapsibleSection from '../components/CollapsibleSection'
import RunthroughsSection from '../components/RunthroughsSection'

function splitTitle(title) {
  const parts = title.split(' vs ')
  return parts.length === 2 ? parts : [title, null]
}

function linkify(text) {
  return text.split(/(\[[^\]]+\]\(https?:\/\/[^\s)]+\)|https?:\/\/[^\s]+)/g).map((part, i) => {
    const md = part.match(/^\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)$/)
    if (md) {
      return <a key={i} href={md[2]} target="_blank" rel="noopener noreferrer">{md[1]}</a>
    }
    if (/^https?:\/\//.test(part)) {
      return <a key={i} href={part} target="_blank" rel="noopener noreferrer">{part}</a>
    }
    return part
  })
}

function FixtureModuleSection({ onStart, turnstileEnabled, finale, fixtureLabel, levelLabel, selectedId, setSelectedId, finaleType, setFinaleType, intro, moduleRows }) {
  const [fixtures, setFixtures] = useState([])
  const [modules, setModules] = useState([])
  const [mode, setMode] = useState('watch')
  const [humanName, setHumanName] = useState('')
  const [turnstileToken, setTurnstileToken] = useState(null)
  const [fixturesOpenOverride, setFixturesOpenOverride] = useState(null)
  const [watchPlayOpenOverride, setWatchPlayOpenOverride] = useState(null)
  const turnstileRef = useRef(null)

  useEffect(() => { setFixturesOpenOverride(null) }, [finaleType])
  useEffect(() => { setWatchPlayOpenOverride(null) }, [selectedId])

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

  const activeModule = modules.find(m => m.id === finaleType)
  const selected = fixtures.find(f => f.id === selectedId)

  const renderModuleBtn = (ft) => (
    <button
      key={ft.id}
      className={`format-btn${finaleType === ft.id ? ' format-btn--selected' : ''}`}
      onClick={() => setFinaleType(ft.id)}
    >
      {ft.title}
    </button>
  )

  let moduleLayout
  if (moduleRows) {
    const grouped = moduleRows.map(ids => ids.map(id => modules.find(m => m.id === id)).filter(Boolean))
    const usedIds = new Set(moduleRows.flat())
    const rest = modules.filter(m => !usedIds.has(m.id))
    moduleLayout = (
      <div className="format-btn-rows">
        {grouped.map((row, i) => (
          <div key={i} className="format-btn-row">{row.map(renderModuleBtn)}</div>
        ))}
        {rest.length > 0 && <div className="format-btn-row">{rest.map(renderModuleBtn)}</div>}
      </div>
    )
  } else {
    moduleLayout = <div className="format-btn-stack">{modules.map(renderModuleBtn)}</div>
  }

  const castDesc = selected && (
    finale
      ? (finaleType === 'reunion' ? selected.reunion_desc : selected.pd_desc)
      : selected.game_desc
  )

  const deadCast = selected ? selected.cast.filter(name => !selected.alive.includes(name)) : []
  const [matchA, matchB] = selected ? splitTitle(selected.title) : [null, null]

  const fixturesOpen = fixturesOpenOverride !== null ? fixturesOpenOverride : !!finaleType
  const watchPlayOpen = watchPlayOpenOverride !== null ? watchPlayOpenOverride : (!!finaleType && !!selectedId)

  const handleSelect = (id) => {
    setSelectedId(id)
    setMode('watch')
    setHumanName('')
  }

  return (
    <div className="finale-section">
      {intro && <p className="finale-intro">{intro}</p>}
      <div className="finale-row-label">{levelLabel}</div>
      <div className="format-step">
        <div className={`format-info-card${activeModule ? ' format-info-card--active' : ''}`}>
          {activeModule ? (
            <div className="format-info-inner">
              <div className="format-info-title">{activeModule.title}</div>
              <div className="format-info-desc">{activeModule.description}</div>
            </div>
          ) : (
            <div className="format-info-empty">Select a format →</div>
          )}
        </div>
        {moduleLayout}
      </div>

      <div className="finale-substep">
        <button
          className="finale-subheader"
          onClick={() => setFixturesOpenOverride(!fixturesOpen)}
        >
          <span className="finale-subheader-left">
            <span className={`collapsible-caret${fixturesOpen ? ' open' : ''}`}>▸</span>
            {fixtureLabel}
          </span>
          <span className="finale-subcount">{fixtures.length} fixtures</span>
        </button>
        <div className={`finale-subbody${fixturesOpen ? ' open' : ''}`}>
          <div className="finale-subbody-inner">
            <div className="fixture-grid">
              {fixtures.map(fx => {
                const [fa, fb] = splitTitle(fx.title)
                const twoUp = fx.alive.length === 2
                const card = (
                  <button
                    key={fx.id}
                    className={`fixture-card2 fixture-card2--${finale ? 'stub' : 'simple'}${selectedId === fx.id ? ' fixture-card2--selected' : ''}`}
                    onClick={() => handleSelect(fx.id)}
                  >
                    {finale ? (
                      <>
                        <span className="fixture-card2-names">
                          <span className="fixture-card2-name">{fa}</span>
                          {fb && <span className="fixture-card2-name fixture-card2-name--b">{fb}</span>}
                        </span>
                        {twoUp && (
                          <span className="fixture-card2-stub">
                            <span>{fx.scores[fx.alive[0]]}</span>
                            <span className="fixture-card2-stub-dash">–</span>
                            <span>{fx.scores[fx.alive[1]]}</span>
                          </span>
                        )}
                      </>
                    ) : (
                      <>
                        <span className="fixture-card2-title">
                          <span>{fa}</span>
                          {fb && <><span className="fixture-vs">vs</span><span>{fb}</span></>}
                        </span>
                        {twoUp && (
                          <span className="fixture-card2-meta">
                            {fx.scores[fx.alive[0]]} — {fx.scores[fx.alive[1]]}
                          </span>
                        )}
                      </>
                    )}
                  </button>
                )
                if (fx.break_before) {
                  return (
                    <Fragment key={fx.id}>
                      <div className="fixture-grid-break" />
                      {card}
                    </Fragment>
                  )
                }
                return card
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="finale-substep">
        <button
          className="finale-subheader"
          onClick={() => setWatchPlayOpenOverride(!watchPlayOpen)}
        >
          <span className="finale-subheader-left">
            <span className={`collapsible-caret${watchPlayOpen ? ' open' : ''}`}>▸</span>
            Watch / Play
          </span>
        </button>
        <div className={`finale-subbody${watchPlayOpen ? ' open' : ''}`}>
          <div className="finale-subbody-inner">
            <div className="watchplay-panel">
              <div className="matchup-line">
                <span className="matchup-name">{matchA}</span>
                {matchB && <>
                  <span className="matchup-vs">VS</span>
                  <span className="matchup-name">{matchB}</span>
                </>}
                {activeModule && <span className="matchup-round">— {activeModule.title}</span>}
              </div>
              {castDesc && <div className="matchup-desc">{linkify(castDesc)}</div>}
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
              <div className="watchplay-footer">
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
          intro="The finale game rounds to determine a winner. The Prisoner's Dilemma finale is currently in production; Reunion is still to be integrated."
          fixtureLabel="Fixtures"
          levelLabel="Finale Format"
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
          intro="These games haven't been integrated yet — they're works in progress. Some ideas just don't work well in practice, others just need refinement. The framework means implementing games is now quite straightforward. If you're interested the git is linked in info. "
          moduleRows={[
            ['knives', 'mob', 'circle'],
            ['sob_story', 'comedy_roast'],
            ['wisdom'],
            ['sacrifice', 'elect_leader'],
          ]}
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
