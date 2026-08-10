export default function CollapsibleSection({ title, meta, open, onToggle, children }) {
  return (
    <div className="collapsible-section">
      <button className="collapsible-header" onClick={onToggle}>
        <span className={`collapsible-caret ${open ? 'open' : ''}`}>{open ? '▾' : '▸'}</span>
        <span className="collapsible-title">{title}</span>
        <span className="collapsible-rule" />
        {meta && <span className="collapsible-meta">{meta}</span>}
      </button>
      <div className={`collapsible-body ${open ? 'open' : ''}`}>
        <div className="collapsible-body-inner">{children}</div>
      </div>
    </div>
  )
}
