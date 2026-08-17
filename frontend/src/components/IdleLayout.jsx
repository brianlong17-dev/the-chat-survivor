import { useNavigate } from 'react-router-dom'
import useTheme, { SHOW_THEME_TOGGLE } from '../hooks/useTheme'

export default function IdleLayout({ view, children }) {
  const navigate = useNavigate()
  const [theme, toggleTheme] = useTheme()
  return (
    <div className="idle-layout">
      <nav className="main-nav">
        <div className="main-nav-brand sc-label">Chat Survivor</div>
        <div className="main-nav-right">
          <div className="main-nav-links">
            <button className={`nav-btn ${view === 'lobby' ? 'active' : ''}`} onClick={() => navigate('/')} aria-current={view === 'lobby' ? 'page' : undefined}>Game</button>
            <button className={`nav-btn ${view === 'demos' ? 'active' : ''}`} onClick={() => navigate('/demos')} aria-current={view === 'demos' ? 'page' : undefined}>Demos</button>
            <button className={`nav-btn ${view === 'about' ? 'active' : ''}`} onClick={() => navigate('/about')} aria-current={view === 'about' ? 'page' : undefined}>About</button>
          </div>
          {SHOW_THEME_TOGGLE && <button
            className="main-nav-theme-toggle"
            onClick={toggleTheme}
            title={theme === 'light' ? 'Switch to dark' : 'Switch to light'}
            aria-label={theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme'}
          >
            {theme === 'light' ? (
              <svg viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M13.5 9.3 A6 6 0 1 1 6.7 2.5 A4.8 4.8 0 0 0 13.5 9.3 Z" />
              </svg>
            ) : (
              <svg viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="8" cy="8" r="3.2" />
                <path d="M8 1.5 V3 M8 13 V14.5 M1.5 8 H3 M13 8 H14.5 M3.4 3.4 L4.5 4.5 M11.5 11.5 L12.6 12.6 M12.6 3.4 L11.5 4.5 M4.5 11.5 L3.4 12.6" />
              </svg>
            )}
          </button>}
        </div>
      </nav>
      {children}
    </div>
  )
}
