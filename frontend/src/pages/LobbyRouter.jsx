import { useState, useEffect } from 'react'
import Lobby from './Lobby'
import LobbyMobile from './Lobby.mobile'

export default function LobbyRouter(props) {
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <>
      {isMobile && !dismissed && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 9999,
          background: 'rgba(0,0,0,0.85)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          padding: '32px 24px',
        }}>
          <div style={{
            background: '#161616', border: '1px solid #2a2a2a',
            padding: '28px 24px', maxWidth: 340, textAlign: 'center',
            display: 'flex', flexDirection: 'column', gap: 16,
            fontFamily: "'Courier New', monospace",
          }}>
            <div style={{ fontFamily: 'Georgia, serif', fontSize: 13, letterSpacing: '0.3em', color: '#e07b54' }}>
              THE CHAT SURVIVOR
            </div>
            <div style={{ fontSize: 13, color: '#d8d8d8', lineHeight: 1.6 }}>
              Mobile version is a work in progress.<br />For now, the game is best enjoyed on desktop.
            </div>
            <button
              onClick={() => setDismissed(true)}
              style={{
                background: 'transparent', border: '1px solid #e07b54',
                color: '#e07b54', fontFamily: "'Courier New', monospace",
                fontSize: 11, letterSpacing: '0.18em', padding: '10px 0',
                cursor: 'pointer',
              }}
            >
              CONTINUE ANYWAY
            </button>
          </div>
        </div>
      )}
      {isMobile ? <LobbyMobile {...props} /> : <Lobby {...props} />}
    </>
  )
}
