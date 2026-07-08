import { useNavigate } from 'react-router-dom'

export default function IdleLayout({ view, children }) {
  const navigate = useNavigate()
  return (
    <div className="idle-layout">
      <nav className="main-nav">
        <button className={`nav-btn ${view === 'lobby' ? 'active' : ''}`} onClick={() => navigate('/')}>Game</button>
        <button className={`nav-btn ${view === 'demos' ? 'active' : ''}`} onClick={() => navigate('/demos')}>Demos</button>
        <button className={`nav-btn ${view === 'about' ? 'active' : ''}`} onClick={() => navigate('/about')}>About</button>
      </nav>
      {children}
    </div>
  )
}
