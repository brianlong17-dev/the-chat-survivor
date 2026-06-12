// In-flow Game/Demos nav for mobile. Hidden ≥768px via CSS; the desktop
// .main-nav (in App.jsx) is hidden <768px. Rendered as the first child of each
// page's scroll area so it scrolls away with the content.
export default function MobileNav({ view, setView }) {
  return (
    <nav className="mobile-nav">
      <button className={`nav-btn ${view === 'lobby' ? 'active' : ''}`} onClick={() => setView('lobby')}>Game</button>
      <button className={`nav-btn ${view === 'demos' ? 'active' : ''}`} onClick={() => setView('demos')}>Demos</button>
    </nav>
  )
}
