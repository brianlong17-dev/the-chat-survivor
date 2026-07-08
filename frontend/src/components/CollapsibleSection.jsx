export default function CollapsibleSection({ title, open, onToggle, children }) {
  return (
    <div className="collapsible-section">
      <button className="collapsible-header" onClick={onToggle}>
        <span className={`collapsible-caret ${open ? 'open' : ''}`}>▸</span>
        {title}
      </button>
      <div className={`collapsible-body ${open ? 'open' : ''}`}>
        <div className="collapsible-body-inner">{children}</div>
      </div>
    </div>
  )
}
