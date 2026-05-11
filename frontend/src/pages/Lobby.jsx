import { useState, useEffect } from 'react'

const LOBBY_STORAGE_KEY = 'lobby_state'

export default function Lobby({ onStart }) {
  const saved = JSON.parse(localStorage.getItem(LOBBY_STORAGE_KEY) || '{}')

  const [tabs, setTabs] = useState({})
  const [activeTab, setActiveTab] = useState('')
  const [selected, setSelected] = useState(saved.selected || [])
  const [mode, setMode] = useState(saved.mode || 'watch')
  const [humanName, setHumanName] = useState(saved.humanName || '')
  const [customNames, setCustomNames] = useState(saved.customNames || [])
  const [customInput, setCustomInput] = useState('')
  const [gameEnabled, setGameEnabled] = useState(false)
  const [levels, setLevels] = useState([])
  const [selectedLevel, setSelectedLevel] = useState(saved.selectedLevel || null)

  useEffect(() => {
    localStorage.setItem(LOBBY_STORAGE_KEY, JSON.stringify({ selected, mode, humanName, customNames, selectedLevel }))
  }, [selected, mode, humanName, customNames, selectedLevel])

  useEffect(() => {
    fetch('/api/characters')
      .then(r => r.json())
      .then(data => {
        setTabs(data.tabs)
        setActiveTab(Object.keys(data.tabs)[0])
      })
    fetch('/api/flags')
      .then(r => r.json())
      .then(data => setGameEnabled(data.game_enabled))
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

  const playerCountIncludingHuman = mode === 'play' ? selected.length + 1 : selected.length
  const maxSelectableAI = maxPlayers - (mode === 'play' ? 1 : 0)

  const toggle = (name) => {
    if (selected.includes(name)) {
      setSelected(selected.filter(n => n !== name))
    } else if (selected.length < maxSelectableAI) {
      setSelected([...selected, name])
    }
  }

  const addCustom = () => {
    const name = customInput.trim()
    if (!name || customNames.includes(name)) return
    setCustomNames([...customNames, name])
    if (selected.length < maxSelectableAI) setSelected([...selected, name])
    setCustomInput('')
  }

  const removeCustom = (name) => {
    setCustomNames(customNames.filter(n => n !== name))
    setSelected(selected.filter(n => n !== name))
  }

  const canStart = gameEnabled && playerCountIncludingHuman >= minPlayers && playerCountIncludingHuman <= maxPlayers && (mode === 'watch' || humanName.trim()) && selectedLevel

  return (
    <div className="lobby">
      <h1 className="lobby-title">THE GAME</h1>

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
        <span className="lobby-selected-label">Players ({playerCountIncludingHuman}/{maxPlayers})</span>
        <div className="lobby-chips">
          {selected.map(name => (
            <span key={name} className="chip">
              {name}
              <button className="chip-remove" onClick={() => toggle(name)}>×</button>
            </span>
          ))}
          {selected.length === 0 && <span className="lobby-hint">Select players below</span>}
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
          <input
            className="lobby-name-input"
            placeholder="Enter a name..."
            value={customInput}
            onChange={e => setCustomInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') addCustom() }}
          />
          <button className="input-submit" onClick={addCustom}>Add</button>
        </div>
      )}

      <div className="lobby-grid">
        {(activeTab === 'Custom' ? customNames : (tabs[activeTab] || [])).map(name => (
          activeTab === 'Custom' ? (
            <span key={name} className="name-btn-wrap">
              <button
                className={`name-btn ${selected.includes(name) ? 'selected' : ''}`}
                onClick={() => toggle(name)}
                disabled={!selected.includes(name) && selected.length >= maxSelectableAI}
              >
                {name}
              </button>
              <button className="name-btn-remove" onClick={() => removeCustom(name)}>×</button>
            </span>
          ) : (
            <button
              key={name}
              className={`name-btn ${selected.includes(name) ? 'selected' : ''}`}
              onClick={() => toggle(name)}
              disabled={!selected.includes(name) && selected.length >= maxSelectableAI}
            >
              {name}
            </button>
          )
        ))}
        {activeTab === 'Custom' && customNames.length === 0 && (
          <span className="lobby-hint">Add names above</span>
        )}
      </div>

      <div className="lobby-footer">
        <div className="lobby-mode">
          <label className="mode-opt">
            <input type="radio" name="mode" value="watch" checked={mode === 'watch'} onChange={() => setMode('watch')} />
            Watch only
          </label>
          <label className="mode-opt">
            <input type="radio" name="mode" value="play" checked={mode === 'play'} onChange={() => setMode('play')} />
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
        <button
          className="lobby-start-btn"
          disabled={!canStart}
          onClick={() => {
            const startData = { names: selected, humanName: mode === 'play' ? humanName.trim() : null, levelId: selectedLevel }
            onStart(startData)
          }}
        >
          {gameEnabled ? 'Start Game' : 'Coming Soon'}
        </button>
      </div>
    </div>
  )
}
