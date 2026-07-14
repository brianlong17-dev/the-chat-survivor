import { useState, useEffect, useRef } from 'react'

const LOBBY_STORAGE_KEY = 'lobby_state'
const HARD_CAP = 12

export default function Lobby({ onStart }) {
  const saved = JSON.parse(localStorage.getItem(LOBBY_STORAGE_KEY) || '{}')

  const [tabs, setTabs] = useState({})
  const [activeTab, setActiveTab] = useState('')
  const [selected, setSelected] = useState(saved.selected || [])
  const [humanIndex, setHumanIndex] = useState(saved.humanIndex !== undefined ? saved.humanIndex : 0)
  const [humanName, setHumanName] = useState(saved.humanName || '')
  const [customNames, setCustomNames] = useState(saved.customNames || [])
  const [customInput, setCustomInput] = useState('')
  const [query, setQuery] = useState('')
  const [gameEnabled, setGameEnabled] = useState(false)
  const [levels, setLevels] = useState([])
  const [selectedLevel, setSelectedLevel] = useState(saved.selectedLevel || null)
  const [dragIndex, setDragIndex] = useState(null)
  const [dragOverIndex, setDragOverIndex] = useState(null)
  const [turnstileEnabled, setTurnstileEnabled] = useState(null)
  const [turnstileToken, setTurnstileToken] = useState(null)
  const [clearConfirmOpen, setClearConfirmOpen] = useState(false)
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
    if (window.turnstile) {
      renderWidget()
    } else {
      window.onTurnstileLoad = renderWidget
    }
    return () => {
      if (widgetId !== null) window.turnstile?.remove(widgetId)
    }
  }, [turnstileEnabled])

  useEffect(() => {
    localStorage.setItem(LOBBY_STORAGE_KEY, JSON.stringify({ selected, humanIndex, humanName, customNames, selectedLevel }))
  }, [selected, humanIndex, humanName, customNames, selectedLevel])

  useEffect(() => {
    fetch('/api/characters')
      .then(r => r.json())
      .then(data => {
        setTabs(data.tabs)
        setActiveTab(Object.keys(data.tabs)[0])
      })
    fetch('/api/flags')
      .then(r => r.json())
      .then(data => {
        setGameEnabled(data.game_enabled)
        setTurnstileEnabled(data.turnstile_enabled)
      })
    fetch('/api/levels')
      .then(r => r.json())
      .then(data => {
        setLevels(data.levels)
        const ids = data.levels.map(l => l.id)
        if (!ids.includes(selectedLevel)) {
          setSelectedLevel(data.levels[0]?.id ?? null)
        }
      })
      .catch(err => console.error('Error fetching levels:', err))
  }, [])

  const selectedLevelObj = levels.find(l => l.id === selectedLevel)
  const maxPlayers = selectedLevelObj?.max_players || 12
  const minPlayers = selectedLevelObj?.min_players || 2

  const clampedHumanIndex = humanIndex !== null ? Math.min(humanIndex, selected.length) : null
  const humanSlotActive = clampedHumanIndex !== null
  const humanShown = humanSlotActive && humanName.trim().length > 0
  const hardSelectableAI = HARD_CAP - (humanSlotActive ? 1 : 0)

  const displayChips = humanSlotActive
    ? [
        ...selected.slice(0, clampedHumanIndex).map(name => ({ type: 'ai', name })),
        { type: 'human', name: humanName.trim() },
        ...selected.slice(clampedHumanIndex).map(name => ({ type: 'ai', name })),
      ]
    : selected.map(name => ({ type: 'ai', name }))

  const activeCount = Math.min(displayChips.length, maxPlayers)
  const inactiveCount = displayChips.length - activeCount
  const activeAINames = displayChips
    .map((c, i) => ({ ...c, active: i < maxPlayers }))
    .filter(c => c.type === 'ai' && c.active)
    .map(c => c.name)
  const mode = humanShown && clampedHumanIndex < maxPlayers ? 'play' : 'watch'
  const radioMode = humanIndex === null
    ? 'watch'
    : (humanShown && clampedHumanIndex >= maxPlayers ? 'watch' : 'play')
  const humanNameMissing = humanIndex !== null && !humanName.trim()

  const removeAI = (name) => {
    const idx = selected.indexOf(name)
    if (idx === -1) return
    setSelected(selected.filter(n => n !== name))
    if (humanIndex !== null && idx < clampedHumanIndex) {
      setHumanIndex(humanIndex - 1)
    }
  }

  const toggle = (name) => {
    if (selected.includes(name)) {
      removeAI(name)
    } else if (selected.length < hardSelectableAI) {
      setSelected([...selected, name])
    }
  }

  const randomize = () => {
    const target = Math.min(maxPlayers - (humanSlotActive ? 1 : 0), hardSelectableAI)
    const pool = [...new Set([...Object.values(tabs).flat(), ...customNames])]
    for (let i = pool.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[pool[i], pool[j]] = [pool[j], pool[i]]
    }
    setSelected(pool.slice(0, Math.max(0, target)))
  }

  const clearCast = () => {
    setSelected([])
    setHumanIndex(null)
  }

  const onChipDrop = (toIndex) => {
    if (dragIndex === null || dragIndex === toIndex) return
    const next = [...displayChips]
    const [moved] = next.splice(dragIndex, 1)
    next.splice(toIndex, 0, moved)
    const newHumanIdx = next.findIndex(c => c.type === 'human')
    setSelected(next.filter(c => c.type === 'ai').map(c => c.name))
    if (humanShown) setHumanIndex(newHumanIdx)
    setDragIndex(null)
    setDragOverIndex(null)
  }

  const addCustom = () => {
    const name = customInput.trim()
    if (!name) return
    const lower = name.toLowerCase()
    const allNames = [...customNames, ...Object.values(tabs).flat()]
    const existing = allNames.find(n => n.toLowerCase() === lower)
    if (existing) {
      toggle(existing)
      setCustomInput('')
      return
    }
    setCustomNames([...customNames, name])
    if (selected.length < hardSelectableAI) setSelected([...selected, name])
    setCustomInput('')
  }

  const removeCustom = (name) => {
    setCustomNames(customNames.filter(n => n !== name))
    removeAI(name)
  }

  const addFromSearch = () => {
    const name = query.trim()
    if (!name || selected.length >= hardSelectableAI) return
    setCustomNames([...customNames, name])
    setSelected([...selected, name])
    setQuery('')
  }

  const q = query.trim().toLowerCase()
  const allNames = [...new Set([...Object.values(tabs).flat(), ...customNames])]
  const tabNames = activeTab === 'Custom' ? customNames : (tabs[activeTab] || [])
  const filtered = q ? allNames.filter(n => n.toLowerCase().includes(q)) : tabNames

  const canStart = gameEnabled && activeCount >= minPlayers && activeCount <= maxPlayers && selectedLevel && !humanNameMissing && (!turnstileEnabled || turnstileToken)

  return (
    <div className="lobby">
      <h1 className="lobby-title">THE CHAT SURVIVOR</h1>

      {clearConfirmOpen && (
        <div className="modal-overlay" onClick={() => setClearConfirmOpen(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <div className="modal-title">Clear the current cast?</div>
            <div className="modal-actions">
              <button className="modal-btn" onClick={() => setClearConfirmOpen(false)}>Cancel</button>
              <button className="modal-btn modal-btn-primary" onClick={() => { clearCast(); setClearConfirmOpen(false) }}>Yes</button>
            </div>
          </div>
        </div>
      )}

      <div className="lobby-levels">
        <span className="lobby-selected-label">Level</span>
        <div className="level-cards">
          {levels.map(level => (
            <button
              key={level.id}
              className={`level-card ${selectedLevel === level.id ? 'selected' : ''} ${level.locked ? 'locked' : ''}`}
              onClick={() => !level.locked && setSelectedLevel(level.id)}
              disabled={level.locked}
            >
              <div className="level-card-name">{level.name}</div>
              <div className="level-card-description">{level.description}</div>
              <div className="level-card-info">
                {level.min_players}-{level.max_players} players
              </div>
              {level.locked && <div className="level-card-lock">🔒</div>}
            </button>
          ))}
        </div>
      </div>

      <div className="lobby-selected">
        <span className="lobby-selected-label">
          Players ({activeCount}/{maxPlayers}{inactiveCount > 0 ? ` (+${inactiveCount} inactive)` : ''})
          <button className="lobby-dice" onClick={randomize} title="Randomly fill players" aria-label="Randomly fill players">
            <svg viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M2.5 14 V5.5 L5 3 H13.5 V11.5 L11 14 Z" />
              <path d="M2.5 5.5 H11 M11 5.5 L13.5 3 M11 5.5 V14" />
              <circle cx="4.9" cy="7.7" r="0.9" fill="currentColor" stroke="none" />
              <circle cx="8.6" cy="11.8" r="0.9" fill="currentColor" stroke="none" />
              <circle cx="12.2" cy="8.4" r="0.75" fill="currentColor" stroke="none" />
            </svg>
          </button>
          {displayChips.length > 0 && (
            <button className="lobby-clear" onClick={() => setClearConfirmOpen(true)} title="Clear cast" aria-label="Clear cast">
              <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round">
                <path d="M4 4 L12 12 M12 4 L4 12" />
              </svg>
            </button>
          )}
        </span>
        <div className="lobby-chips">
          {displayChips.map((c, i) => {
            const isActive = i < maxPlayers
            const isHuman = c.type === 'human'
            return (
              <span
                key={isHuman ? '__human__' : c.name}
                className={`chip chip-draggable ${!isActive ? 'inactive' : ''} ${isHuman ? 'chip-human' : ''} ${dragIndex === i ? 'dragging' : ''} ${dragIndex !== null && dragOverIndex === i && dragIndex !== i ? 'drop-target' : ''}`}
                draggable
                onDragStart={() => setDragIndex(i)}
                onDragOver={(e) => { e.preventDefault(); if (dragOverIndex !== i) setDragOverIndex(i) }}
                onDrop={() => onChipDrop(i)}
                onDragEnd={() => { setDragIndex(null); setDragOverIndex(null) }}
              >
                {isHuman ? (c.name ? `${c.name} (you)` : '(you)') : c.name}
                <button
                  className="chip-remove"
                  onClick={() => isHuman ? setHumanIndex(null) : toggle(c.name)}
                >×</button>
              </span>
            )
          })}
          {displayChips.length === 0 && <span className="lobby-hint">Select players below</span>}
        </div>
      </div>

      <div className="lobby-search">
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
          <circle cx="5.5" cy="5.5" r="4" stroke="var(--text-dim)" strokeWidth="1.3" />
          <path d="M8.7 8.7L12 12" stroke="var(--text-dim)" strokeWidth="1.3" strokeLinecap="round" />
        </svg>
        <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search cast..." />
        {query && <button className="lobby-search-x" onClick={() => setQuery('')}>×</button>}
      </div>

      {!q && (
        <div className="lobby-tabs">
          {Object.keys(tabs).map(tab => (
            <button
              key={tab}
              className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
          <button
            className={`tab-btn ${activeTab === 'Custom' ? 'active' : ''}`}
            onClick={() => setActiveTab('Custom')}
          >
            Custom
          </button>
        </div>
      )}

      {!q && activeTab === 'Custom' && (
        <div className="custom-input-row">
          <div className="name-input-wrapper">
            <input
              className="lobby-name-input"
              placeholder="Enter a name..."
              value={customInput}
              maxLength={40}
              onChange={e => setCustomInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') addCustom() }}
            />
            <span className={`name-char-count${customInput.length >= 40 ? ' at-limit' : ''}`}>
              {customInput.length}/40
            </span>
          </div>
          <button className="input-submit" onClick={addCustom}>Add</button>
        </div>
      )}

      {q && filtered.length === 0 && (
        <div className="custom-input-row">
          <button
            className="input-submit"
            onClick={addFromSearch}
            disabled={selected.length >= hardSelectableAI}
          >
            + Add “{query.trim()}”
          </button>
        </div>
      )}

      <div className="lobby-grid">
        {filtered.map(name => {
          const isSelected = selected.includes(name)
          const isActive = activeAINames.includes(name)
          const selClass = isSelected ? (isActive ? 'selected' : 'selected inactive') : ''
          const isDisabled = !isSelected && selected.length >= hardSelectableAI
          const isCustom = !q && activeTab === 'Custom'
          return isCustom ? (
            <span key={name} className="name-btn-wrap">
              <button
                className={`name-btn ${selClass}`}
                onClick={() => toggle(name)}
                disabled={isDisabled}
              >
                {name}
              </button>
              <button className="name-btn-remove" onClick={() => removeCustom(name)}>×</button>
            </span>
          ) : (
            <button
              key={name}
              className={`name-btn ${selClass}`}
              onClick={() => toggle(name)}
              disabled={isDisabled}
            >
              {name}
            </button>
          )
        })}
        {!q && activeTab === 'Custom' && customNames.length === 0 && (
          <span className="lobby-hint">Add names above</span>
        )}
        {!q && activeTab !== 'Custom' && filtered.length === 0 && (
          <span className="lobby-hint">No matches</span>
        )}
      </div>

      <div className="lobby-footer">
        <input
          className={`lobby-name-input lobby-name-input-wide ${humanNameMissing ? 'invalid' : ''}`}
          placeholder="Your Name"
          value={humanName}
          disabled={humanIndex === null}
          onChange={e => setHumanName(e.target.value)}
        />
        <div className="lobby-footer-btns">
          <div className="mode-switch">
            <button
              className={`mode-switch-opt${radioMode === 'watch' ? ' active' : ''}`}
              onClick={() => setHumanIndex(null)}
            >Watch</button>
            <button
              className={`mode-switch-opt${radioMode === 'play' ? ' active' : ''}`}
              onClick={() => setHumanIndex(0)}
            >Play</button>
          </div>
          <button
            className="lobby-start-btn"
            disabled={!canStart}
            onClick={() => {
              const startData = { names: activeAINames, humanName: mode === 'play' ? humanName.trim() : null, levelId: selectedLevel, turnstileToken}
              onStart(startData)
            }}
          >
            {!gameEnabled ? 'Coming Soon' : humanNameMissing ? 'Enter Your Name' : activeCount < minPlayers ? `Select ${minPlayers - activeCount} more ${minPlayers - activeCount === 1 ? 'player' : 'players'}` : 'Start Game'}
          </button>
        </div>
      </div>
      {turnstileEnabled && <div ref={turnstileRef} style={{ display: 'flex', justifyContent: 'center' }} />}
    </div>
  )
}
