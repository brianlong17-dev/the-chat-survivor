// Mobile header: burger (left) opens a slide-out drawer with Game/Demos/About nav;
// wordmark centered. Hidden ≥768px via CSS; the desktop .main-nav (in App.jsx)
// is hidden <768px. Rendered as the first child of each page's scroll area.
import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

export default function MobileNav() {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const go = (path) => { navigate(path); setOpen(false) }
  return (
    <>
      <header className="mobile-nav">
        <button className="mobile-nav-burger" aria-label="Menu" onClick={() => setOpen(true)}>
          <span /><span /><span />
        </button>
        <div className="mobile-nav-logo">THE CHAT SURVIVOR</div>
        <span className="mobile-nav-spacer" />
      </header>
      {open && (
        <div className="mobile-drawer-overlay">
          <div className="mobile-drawer-backdrop" onClick={() => setOpen(false)} />
          <nav className="mobile-drawer">
            <button className={`nav-btn ${pathname === '/' ? 'active' : ''}`} onClick={() => go('/')}>Game</button>
            <button className={`nav-btn ${pathname === '/demos' ? 'active' : ''}`} onClick={() => go('/demos')}>Demos</button>
            <button className={`nav-btn ${pathname === '/about' ? 'active' : ''}`} onClick={() => go('/about')}>About</button>
          </nav>
        </div>
      )}
    </>
  )
}
