import { useState, useEffect } from 'react'
import './App.css'
import './App.mobile.css'
import { loadSettings, saveSettings } from './utils/settings'
import { useGameSocket } from './hooks/useGameSocket'
import LobbyRouter from './pages/LobbyRouter'
import DemosPage from './pages/DemosPage'
import GameViewRouter from './pages/GameViewRouter'

export default function App() {
  const [view, setView] = useState('lobby')
  const [settings, setSettings] = useState(loadSettings)
  const [transcriptionEnabled, setTranscriptionEnabled] = useState(false)

  useEffect(() => {
    fetch('/api/flags')
      .then(r => r.json())
      .then(data => setTranscriptionEnabled(data.transcription_enabled))
      .catch(() => setTranscriptionEnabled(false))
  }, [])

  const updateSetting = (key, value) => {
    setSettings(prev => {
      const next = { ...prev, [key]: value }
      saveSettings(next)
      return next
    })
  }

  const socket = useGameSocket(settings.autoRun, settings.animateText, settings.mobileOutputs)
  const { status, startGame, startDemo } = socket

  if (status !== 'idle') {
    return <GameViewRouter {...socket} settings={settings} updateSetting={updateSetting} transcriptionEnabled={transcriptionEnabled} />
  }

  return (
    <>
      {status === 'idle' && (
        <div className="idle-layout">
          <nav className="main-nav">
            <button className={`nav-btn ${view === 'lobby' ? 'active' : ''}`} onClick={() => setView('lobby')}>Game</button>
            <button className={`nav-btn ${view === 'demos' ? 'active' : ''}`} onClick={() => setView('demos')}>Demos</button>
          </nav>
          {view === 'lobby'
            ? <LobbyRouter onStart={startGame} view={view} setView={setView} />
            : <DemosPage onStart={startDemo} view={view} setView={setView} />}
        </div>
      )}
    </>
  )
}
