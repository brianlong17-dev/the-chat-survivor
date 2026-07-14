import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import './App.css'
import './App.mobile.css'
import { loadSettings, saveSettings } from './utils/settings'
import { useGameSocket } from './hooks/useGameSocket'
import LobbyRouter from './pages/LobbyRouter'
import DemosPage from './pages/DemosPage'
import AboutPage from './pages/AboutPage'
import GameViewRouter from './pages/GameViewRouter'
import RunthroughPage from './pages/RunthroughPage'
import IdleLayout from './components/IdleLayout'

export default function App() {
  const [settings, setSettings] = useState(loadSettings)
  const [transcriptionEnabled, setTranscriptionEnabled] = useState(false)
  const [devMode, setDevMode] = useState(false)

  useEffect(() => {
    fetch('/api/flags')
      .then(r => r.json())
      .then(data => {
        setTranscriptionEnabled(data.transcription_enabled)
        setDevMode(data.dev_mode)
      })
      .catch(() => { setTranscriptionEnabled(false); setDevMode(false) })
  }, [])

  const updateSetting = (key, value) => {
    setSettings(prev => {
      const next = { ...prev, [key]: value }
      saveSettings(next)
      return next
    })
  }

  const navigate = useNavigate()
  const socket = useGameSocket(settings.autoRun, settings.animateText, settings.mobileOutputs)
  const { status, startGame, startDemo, startReplay } = socket

  if (status !== 'idle') {
    const exitGame = () => { socket.exitGame(); navigate('/') }
    return <GameViewRouter {...socket} exitGame={exitGame} settings={settings} updateSetting={updateSetting} transcriptionEnabled={transcriptionEnabled} devMode={devMode} />
  }

  return (
    <Routes>
      <Route path="/" element={
        <IdleLayout view="lobby">
          <LobbyRouter onStart={startGame} />
        </IdleLayout>
      } />
      <Route path="/demos" element={
        <IdleLayout view="demos">
          <DemosPage onStart={startDemo} />
        </IdleLayout>
      } />
      <Route path="/about" element={
        <IdleLayout view="about">
          <AboutPage />
        </IdleLayout>
      } />
      <Route path="/runthrough/:runthroughId" element={<RunthroughPage onStart={startReplay} />} />
    </Routes>
  )
}
