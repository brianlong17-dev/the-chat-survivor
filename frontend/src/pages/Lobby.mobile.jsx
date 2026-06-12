import { useState, useEffect, useRef } from 'react'
import MobileNav from '../components/MobileNav'
import './Lobby.mobile.css'

// Mobile lobby for The Chat Survivor.
// Same data contract as the desktop Lobby:
//   • fetches /api/characters, /api/levels, /api/flags
//   • persists to localStorage 'lobby_state' (shape stays desktop-compatible)
//   • calls onStart({ names, humanName, levelId, turnstileToken })
// Difference from desktop: Watch/Play is an explicit fork. Tapping PLAY opens a
// name sheet; confirming seats "You" at the front (humanIndex 0). You can't be
// reordered — switch back via the toggle or the You chip's ×.

const LOBBY_STORAGE_KEY = 'lobby_state'
const HARD_CAP = 12

export default function LobbyMobile({ onStart, view, setView }) {
  const saved = JSON.parse(localStorage.getItem(LOBBY_STORAGE_KEY) || '{}')

  const [tabs, setTabs] = useState({})
  const [activeTab, setActiveTab] = useState('')
  const [selected, setSelected] = useState(saved.selected || [])
  const [playing, setPlaying] = useState(saved.humanIndex != null)
  const [humanName, setHumanName] = useState(saved.humanName || '')
  const [customNames, setCustomNames] = useState(saved.customNames || [])
  const [customInput, setCustomInput] = useState('')
  const [query, setQuery] = useState('')
  const [gameEnabled, setGameEnabled] = useState(false)
  const [levels, setLevels] = useState([])
  const [selectedLevel, setSelectedLevel] = useState(saved.selectedLevel || null)
  const [turnstileEnabled, setTurnstileEnabled] = useState(null)
  const [turnstileToken, setTurnstileToken] = useState(null)
  const [nameSheet, setNameSheet] = useState(false)
  const [draftName, setDraftName] = useState('')
  const [hint, setHint] = useState(false)
  const turnstileRef = useRef(null)

  // ── Turnstile (identical to desktop) ──
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

  // ── Persist (desktop-compatible shape) ──
  useEffect(() => {
    localStorage.setItem(LOBBY_STORAGE_KEY, JSON.stringify({
      selected, humanIndex: playing ? 0 : null, humanName, customNames, selectedLevel,
    }))
  }, [selected, playing, humanName, customNames, selectedLevel])

  // ── Initial data ──
  useEffect(() => {
    fetch('/api/characters').then(r => r.json()).then(data => {
      setTabs(data.tabs)
      setActiveTab(Object.keys(data.tabs)[0])
    })
    fetch('/api/flags').then(r => r.json()).then(data => {
      setGameEnabled(data.game_enabled)
      setTurnstileEnabled(data.turnstile_enabled)
    })
    fetch('/api/levels').then(r => r.json()).then(data => {
      setLevels(data.levels)
      const ids = data.levels.map(l => l.id)
      if (!ids.includes(selectedLevel)) setSelectedLevel(data.levels[0]?.id ?? null)
    }).catch(err => console.error('Error fetching levels:', err))
  }, [])

  const levelObj = levels.find(l => l.id === selectedLevel)
  const maxPlayers = levelObj?.max_players || 12
  const minPlayers = levelObj?.min_players || 2

  const aiCap = Math.min(HARD_CAP, maxPlayers) - (playing ? 1 : 0)
  const count = selected.length + (playing ? 1 : 0)
  const need = Math.max(0, minPlayers - count)

  const toggle = (name) => setSelected(s =>
    s.includes(name) ? s.filter(n => n !== name) : (s.length >= aiCap ? s : [...s, name]))
  const remove = (name) => setSelected(s => s.filter(n => n !== name))

  // ── Watch / Play fork ──
  const goWatch = () => { setPlaying(false); setHint(false) }
  const goPlay = () => {
    if (playing) return
    if (selected.length >= Math.min(HARD_CAP, maxPlayers)) { setHint(true); return } // table full
    setHint(false); setDraftName(humanName); setNameSheet(true)
  }
  const confirmName = () => {
    if (!draftName.trim()) return
    setHumanName(draftName.trim()); setPlaying(true); setNameSheet(false)
  }

  // ── Custom names ──
  const addCustom = () => {
    const name = customInput.trim()
    if (!name) return
    const lower = name.toLowerCase()
    const existing = [...customNames, ...Object.values(tabs).flat()].find(n => n.toLowerCase() === lower)
    if (existing) { toggle(existing); setCustomInput(''); return }
    setCustomNames([...customNames, name])
    if (selected.length < aiCap) setSelected([...selected, name])
    setCustomInput('')
  }
  const removeCustom = (name) => { setCustomNames(customNames.filter(n => n !== name)); remove(name) }

  const humanNameMissing = playing && !humanName.trim()
  const canStart = gameEnabled && count >= minPlayers && count <= maxPlayers
    && selectedLevel && !humanNameMissing && (!turnstileEnabled || turnstileToken)

  const q = query.trim().toLowerCase()
  const allNames = [...Object.values(tabs).flat(), ...customNames]
  const names = activeTab === 'Custom' ? customNames : (tabs[activeTab] || [])
  const filtered = q ? allNames.filter(n => n.toLowerCase().includes(q)) : names

  const handleStart = () => onStart({
    names: selected,
    humanName: playing ? humanName.trim() : null,
    levelId: selectedLevel,
    turnstileToken,
  })

  return (
    <div className="ml-lobby">
      <div className="ml-body">
        <MobileNav view={view} setView={setView} />
        <div className="ml-title">THE CHAT SURVIVOR</div>
        {/* levels */}
        <div style={{ padding: '2px 0 18px' }}>
          <div className="ml-label" style={{ padding: '0 16px 9px' }}>Level</div>
          <div className="ml-levels ml-hscroll">
            {levels.map(level => (
              <button key={level.id}
                className={`ml-level ${selectedLevel === level.id ? 'selected' : ''} ${level.locked ? 'locked' : ''}`}
                onClick={() => !level.locked && setSelectedLevel(level.id)} disabled={level.locked}>
                <div className="ml-level-head">
                  <span className="ml-level-name">{level.name}</span>
                  {level.locked && <span style={{ opacity: .6 }}>🔒</span>}
                </div>
                <div className="ml-level-desc">{level.description}</div>
                <div className="ml-level-info">{level.min_players}-{level.max_players} players</div>
              </button>
            ))}
          </div>
        </div>

        {/* player tray */}
        <div className="ml-tray">
          <div className="ml-label">Players ({count}/{maxPlayers})</div>
          <div className="ml-chips">
            {playing && (
              <span className="ml-chip">{humanName || 'You'}<span className="you"> (you)</span>
                <button className="ml-chip-x" onClick={goWatch}>×</button></span>
            )}
            {selected.map(n => (
              <span key={n} className="ml-chip">{n}
                <button className="ml-chip-x" onClick={() => remove(n)}>×</button></span>
            ))}
            {count === 0 && <span className="ml-hint">Select players below</span>}
          </div>
        </div>

        {/* cast */}
        <div style={{ marginTop: 18 }}>
          <div className="ml-cast-sticky">
            <div className="ml-label" style={{ padding: '0 16px 9px' }}>Cast</div>
            <div style={{ padding: '0 16px 10px' }}>
              <div className="ml-search">
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                  <circle cx="5.5" cy="5.5" r="4" stroke="var(--text-dim)" strokeWidth="1.3" />
                  <path d="M8.7 8.7L12 12" stroke="var(--text-dim)" strokeWidth="1.3" strokeLinecap="round" />
                </svg>
                <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search cast…" />
                {query && <button className="ml-x" onClick={() => setQuery('')}>×</button>}
              </div>
            </div>
            {!q && (
              <div className="ml-tabs ml-hscroll">
                {Object.keys(tabs).map(t => (
                  <button key={t} className={`ml-tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>{t}</button>
                ))}
                <button className={`ml-tab ${activeTab === 'Custom' ? 'active' : ''}`} onClick={() => setActiveTab('Custom')}>Custom</button>
              </div>
            )}
          </div>

          {!q && activeTab === 'Custom' && (
            <div className="ml-custom-row" style={{ paddingTop: 12 }}>
              <input value={customInput} maxLength={40} placeholder="Enter a name…"
                onChange={e => setCustomInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter') addCustom() }} />
              <button onClick={addCustom}>ADD</button>
            </div>
          )}

          <div className="ml-grid">
            {filtered.map(name => {
              const sel = selected.includes(name)
              const dis = !sel && selected.length >= aiCap
              const isCustom = !q && activeTab === 'Custom'
              return isCustom ? (
                <span key={name} className="ml-name-wrap">
                  <button className={`ml-name ${sel ? 'selected' : ''}`} onClick={() => toggle(name)} disabled={dis}>{name}</button>
                  <button className="ml-name-rm" onClick={() => removeCustom(name)}>×</button>
                </span>
              ) : (
                <button key={name} className={`ml-name ${sel ? 'selected' : ''}`} onClick={() => toggle(name)} disabled={dis}>{name}</button>
              )
            })}
            {!q && activeTab === 'Custom' && customNames.length === 0 && <span className="ml-hint">Add names above.</span>}
            {q && filtered.length === 0 && <span className="ml-hint">No matches.</span>}
            {!q && activeTab !== 'Custom' && filtered.length === 0 && <span className="ml-hint">No matches.</span>}
          </div>
        </div>

        {turnstileEnabled && <div className="ml-turnstile" ref={turnstileRef} />}
      </div>

      {/* footer */}
      <div className="ml-footer">
        <div className="ml-footer-row">
          <div className="ml-toggle">
            <button className={!playing ? 'active' : ''} onClick={goWatch}>WATCH</button>
            <button className={playing ? 'active' : ''} onClick={goPlay}>PLAY</button>
          </div>
          <span className={`ml-meta ${hint ? 'error' : ''}`}>
            {hint ? 'Table full — remove a player first' : (levelObj?.name || '')}
          </span>
        </div>
        <button className="ml-start" disabled={!canStart} onClick={handleStart}>
          {!gameEnabled ? 'COMING SOON' : count < minPlayers ? `SELECT ${need} MORE` : 'START GAME'}
        </button>
      </div>

      {/* name sheet */}
      {nameSheet && (
        <div className="ml-sheet-overlay">
          <div className="ml-sheet-backdrop" onClick={() => setNameSheet(false)} />
          <div className="ml-sheet">
            <div className="ml-grabber" />
            <div className="ml-label">Play as yourself</div>
            <div className="ml-sheet-sub">You'll join as a contestant and take a seat at the table.</div>
            <input className="ml-sheet-input" autoFocus value={draftName} maxLength={40}
              placeholder="Your name"
              onChange={e => setDraftName(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') confirmName() }} />
            <button className="ml-sheet-btn" disabled={!draftName.trim()} onClick={confirmName}>
              ADD ME TO THE GAME
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
