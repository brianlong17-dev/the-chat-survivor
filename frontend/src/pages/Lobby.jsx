import { useState, useEffect, useRef } from 'react'

const LOBBY_STORAGE_KEY = 'lobby_state'
const HARD_CAP = 12

export default function Lobby({ onStart }) {
  const saved = JSON.parse(localStorage.getItem(LOBBY_STORAGE_KEY) || '{}')

  const [tabs, setTabs] = useState({})
  const [activeTab, setActiveTab] = useState('')
  const [selected, setSelected] = useState(saved.selected || [])
  const [humanIndex, setHumanIndex] = useState(saved.humanIndex ?? (saved.mode === 'play' ? 0 : null))
  const [humanName, setHumanName] = useState(saved.humanName || '')
  const [customNames, setCustomNames] = useState(saved.customNames || [])
  const [customInput, setCustomInput] = useState('')
  const [gameEnabled, setGameEnabled] = useState(false)
  const [levels, setLevels] = useState([])
  const [selectedLevel, setSelectedLevel] = useState(saved.selectedLevel || null)
  const [dragIndex, setDragIndex] = useState(null)
  const [dragOverIndex, setDragOverIndex] = useState(null)
  const [turnstileEnabled, setTurnstileEnabled] = useState(null)
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
  const humanShown = clampedHumanIndex !== null && humanName.trim().length > 0
  const hardSelectableAI = HARD_CAP - (humanShown ? 1 : 0)

  const displayChips = humanShown
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

  const canStart = gameEnabled && activeCount >= minPlayers && activeCount <= maxPlayers && selectedLevel && !humanNameMissing && (!turnstileEnabled || turnstileToken)

  return (
    <div className="lobby">
      <h1 className="lobby-title">THE CHAT SURVIVOR</h1>

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
        <span className="lobby-selected-label">Players ({activeCount}/{maxPlayers}{inactiveCount > 0 ? ` (+${inactiveCount} inactive)` : ''})</span>
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
                {isHuman ? `${c.name} (you)` : c.name}
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

      {activeTab === 'Custom' && (
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

      <div className="lobby-grid">
        {(activeTab === 'Custom' ? customNames : (tabs[activeTab] || [])).map(name => {
          const isSelected = selected.includes(name)
          const isActive = activeAINames.includes(name)
          const selClass = isSelected ? (isActive ? 'selected' : 'selected inactive') : ''
          const isDisabled = !isSelected && selected.length >= hardSelectableAI
          return activeTab === 'Custom' ? (
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
        {activeTab === 'Custom' && customNames.length === 0 && (
          <span className="lobby-hint">Add names above</span>
        )}
      </div>

      <div className="lobby-footer">
        <div className="lobby-mode">
          <label className="mode-opt">
            <input type="radio" name="mode" value="watch" checked={radioMode === 'watch'} onChange={() => setHumanIndex(null)} />
            Watch only
          </label>
          <label className="mode-opt">
            <input type="radio" name="mode" value="play" checked={radioMode === 'play'} onChange={() => setHumanIndex(0)} />
            Play as:
          </label>
          {humanIndex !== null && (
            <input
              className={`lobby-name-input ${humanNameMissing ? 'invalid' : ''}`}
              placeholder="Your name"
              value={humanName}
              onChange={e => setHumanName(e.target.value)}
              autoFocus
            />
          )}
        </div>
        <button
          className="lobby-start-btn"
          disabled={!canStart}
          onClick={() => {
            const startData = { names: activeAINames, humanName: mode === 'play' ? humanName.trim() : null, levelId: selectedLevel, turnstileToken}
            onStart(startData)
          }}
        >
          {!gameEnabled ? 'Coming Soon' : activeCount < minPlayers ? `Select ${minPlayers - activeCount} more ${minPlayers - activeCount === 1 ? 'player' : 'players'}` : 'Start Game'}
        </button>
      </div>
      {turnstileEnabled && <div ref={turnstileRef} style={{ display: 'flex', justifyContent: 'center' }} />}
    </div>
  )
}
