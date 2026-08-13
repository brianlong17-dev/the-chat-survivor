import { useRef, useEffect, useState } from 'react'
import { ThreadedFeed } from '../components/Messages'
import Scoreboard from '../components/Scoreboard'
import RoundTracker from '../components/RoundTracker'
import RoundWidget from '../components/RoundWidget'
import InputRequest from '../components/InputRequest'
import SegmentTracker from '../components/SegmentTracker'
import PrivateChatsPanel from '../components/PrivateChatsPanel'
import useTheme from '../hooks/useTheme'
import { SETTINGS_DEFS, VISIBLE_TOGGLE_KEYS } from '../utils/settings'

const SETTINGS_TOGGLES = SETTINGS_DEFS.filter(t => VISIBLE_TOGGLE_KEYS.has(t.key))

export default function GameView({
  status, events, scores, evicted,
  inputRequest, awaitingNext, phaseRounds, currentRoundIndex,
  submitInputForm, sendNext, startLevel, skipAnimation, exitGame, restartGame, transcribe, onAnimationComplete, skipRef,
  isAnimating, settings, updateSetting, feedMarkers, segmentTitles, widget,
  privateConversations, playerNames = [], transcriptionEnabled, sendNextRound, awaitingNextRound, devMode
}) {
  const { showPrivateThoughts, animateText, showPrivateChats, mobileOutputs, autoExpandThoughts } = settings
  const [theme, toggleTheme] = useTheme()

  // A replay deep-link keeps the URL /runthrough/:id#<msgId> even after App swaps to GameView.
  // The msgId lives in the hash so clicking a link on an already-open replay only scrolls.
  const replayRunthroughId = (window.location.pathname.match(/^\/runthrough\/([^/]+)/) || [])[1] || null
  const scrolledToRef = useRef(null)
  const nextBtnRef = useRef(null)

  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.key !== 'Enter') return
      const btn = nextBtnRef.current
      if (!btn || btn.disabled || document.activeElement === btn) return
      e.preventDefault()
      btn.click()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

  const [settingsOpen, setSettingsOpen] = useState(false)
  const [exitConfirmOpen, setExitConfirmOpen] = useState(false)
  const [mobileOutputsInfoOpen, setMobileOutputsInfoOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('feed')
  const [seenPrivateCount, setSeenPrivateCount] = useState(0)
  const settingsRef = useRef(null)
  const colorMapRef = useRef({})
  const bottomRef = useRef(null)
  const feedRef = useRef(null)
  const privateBottomRef = useRef(null)
  const lastSeenPrivateCountRef = useRef(0)
  const userScrolledUpRef = useRef(false)
  const feedMouseDownPosRef = useRef(null)
  const feedMouseIsDownRef = useRef(false)
  const leftDragRef = useRef({ startX: 0, startWidth: 0, moved: false })
  const [leftToggleCursor, setLeftToggleCursor] = useState('col-resize')
  const rightDragRef = useRef({ startX: 0, startWidth: 0, moved: false })
  const [rightToggleCursor, setRightToggleCursor] = useState('col-resize')

  const onLeftResizeStart = (e) => {
    const startWidth = settings.leftSidebarWidth ?? 220
    leftDragRef.current = { startX: e.clientX, startWidth, moved: false }

    const onMove = (mv) => {
      const dx = mv.clientX - leftDragRef.current.startX
      if (Math.abs(dx) > 4) leftDragRef.current.moved = true
      const newWidth = Math.max(120, Math.min(500, leftDragRef.current.startWidth + dx))
      updateSetting('leftSidebarWidth', newWidth)
    }

    const onUp = () => {
      if (!leftDragRef.current.moved) {
        updateSetting('leftSidebarOpen', settings.leftSidebarOpen === false ? true : false)
      }
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }

    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
  }

  const onRightResizeStart = (e) => {
    const startWidth = settings.rightSidebarWidth ?? 200
    rightDragRef.current = { startX: e.clientX, startWidth, moved: false }

    const onMove = (mv) => {
      const dx = mv.clientX - rightDragRef.current.startX
      if (Math.abs(dx) > 4) rightDragRef.current.moved = true
      const newWidth = Math.max(120, Math.min(500, rightDragRef.current.startWidth - dx))
      updateSetting('rightSidebarWidth', newWidth)
    }

    const onUp = () => {
      if (!rightDragRef.current.moved) {
        updateSetting('sidebarOpen', settings.sidebarOpen === false ? true : false)
      }
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }

    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
  }

  const handleFeedScroll = () => {
    if (feedMouseIsDownRef.current) return
    const feed = feedRef.current
    if (!feed) return
    const distFromBottom = feed.scrollHeight - feed.scrollTop - feed.clientHeight
    if (distFromBottom < 20) userScrolledUpRef.current = false
  }

  const handleUserScrollIntent = (e) => {
    if (e.deltaY !== undefined) {
      if (e.deltaY < 0) userScrolledUpRef.current = true
    } else {
      const feed = feedRef.current
      if (!feed) return
      const distFromBottom = feed.scrollHeight - feed.scrollTop - feed.clientHeight
      if (distFromBottom > 5) userScrolledUpRef.current = true
    }
  }

  const handleFeedMouseDown = (e) => {
    userScrolledUpRef.current = true
    feedMouseIsDownRef.current = true
    feedMouseDownPosRef.current = { x: e.clientX, y: e.clientY }
  }
  const handleFeedMouseUp = (e) => {
    const start = feedMouseDownPosRef.current
    const dragged = start && Math.hypot(e.clientX - start.x, e.clientY - start.y) > 4
    if (dragged) return
    if (window.getSelection().toString() === '') {
      const feed = feedRef.current
      if (feed && feed.scrollHeight - feed.scrollTop - feed.clientHeight < 20) {
        userScrolledUpRef.current = false
      }
    }
  }

  useEffect(() => {
    if (!settingsOpen) return
    const handler = (e) => {
      if (settingsRef.current && !settingsRef.current.contains(e.target)) {
        setSettingsOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [settingsOpen])

  useEffect(() => {
    const onWindowMouseUp = () => { feedMouseIsDownRef.current = false }
    window.addEventListener('mouseup', onWindowMouseUp)
    return () => window.removeEventListener('mouseup', onWindowMouseUp)
  }, [])

  const pinFeedToBottom = () => {
    if (userScrolledUpRef.current || feedMouseIsDownRef.current) return
    const feed = feedRef.current
    if (!feed) return
    if (feed.scrollHeight - feed.scrollTop - feed.clientHeight > 1) feed.scrollTop = feed.scrollHeight
  }

  useEffect(() => {
    const id = setInterval(pinFeedToBottom, 100)
    return () => clearInterval(id)
  }, [status])

  useEffect(() => {
    pinFeedToBottom()
  }, [events.length])

  useEffect(() => {
    const scrollToHash = () => {
      const msgId = window.location.hash.slice(1)
      if (!msgId || scrolledToRef.current === msgId) return
      const el = document.getElementById(`msg-${msgId}`)
      if (!el) return
      scrolledToRef.current = msgId
      userScrolledUpRef.current = true   // stop the autopin from yanking back to bottom
      document.querySelectorAll('.msg-deeplink-target').forEach(n => n.classList.remove('msg-deeplink-target'))
      const feed = feedRef.current
      if (feed) feed.scrollTop += el.getBoundingClientRect().top - feed.getBoundingClientRect().top - feed.clientHeight * 0.10
      else el.scrollIntoView({ block: 'center' })
      el.classList.add('msg-deeplink-target')
    }
    scrollToHash()
    window.addEventListener('hashchange', scrollToHash)
    return () => window.removeEventListener('hashchange', scrollToHash)
  }, [events.length])

  useEffect(() => {
    if (activeTab !== 'private') return
    if (privateConversations.length > lastSeenPrivateCountRef.current) {
      lastSeenPrivateCountRef.current = privateConversations.length
      privateBottomRef.current?.scrollIntoView({ behavior: 'instant' })
    }
  }, [privateConversations, activeTab])

  const visibleEvents = showPrivateThoughts
    ? events
    : events.filter(e => e.type !== 'private_thought')

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <h1 className="app-title app-title-clickable" onClick={() => setExitConfirmOpen(true)}>Chat Survivor</h1>
          {showPrivateChats && (
            <div className="header-tabs">
              <button className={`header-tab${activeTab === 'feed' ? ' active' : ''}`} onClick={() => setActiveTab('feed')}>
                main feed
              </button>
              <button className={`header-tab${activeTab === 'private' ? ' active' : ''}`} onClick={() => { setActiveTab('private'); setSeenPrivateCount(privateConversations.length) }}>
                private conversations
                {privateConversations.length > seenPrivateCount && <span className="feed-tab-badge" />}
              </button>
            </div>
          )}
        </div>
        <div className="header-controls">
          <button
            className="header-theme-toggle"
            onClick={toggleTheme}
            title={theme === 'light' ? 'Switch to dark' : 'Switch to light'}
            aria-label={theme === 'light' ? 'Switch to dark' : 'Switch to light'}
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
          </button>
          <div className="settings-menu" ref={settingsRef}>
            <button className="gear-btn" onClick={() => setSettingsOpen(o => !o)}>⚙</button>
            {settingsOpen && (
              <div className="settings-dropdown">
                {SETTINGS_TOGGLES.map(t => (
                  t.key === 'mobileOutputs' ? (
                    <div className="toggle-label-with-info" key={t.key}>
                      <label className="toggle-label">
                        <input type="checkbox" checked={!!mobileOutputs} onChange={e => updateSetting('mobileOutputs', e.target.checked)} />
                        {t.label}
                      </label>
                      <button
                        className="setting-info-btn"
                        onClick={e => { e.stopPropagation(); setMobileOutputsInfoOpen(o => !o) }}
                        title="About mobile outputs"
                      >ⓘ</button>
                    </div>
                  ) : (
                    <label className="toggle-label" key={t.key}>
                      <input type="checkbox" checked={!!settings[t.key]} onChange={e => updateSetting(t.key, e.target.checked)} />
                      {t.label}
                    </label>
                  )
                ))}
                {mobileOutputsInfoOpen && VISIBLE_TOGGLE_KEYS.has('mobileOutputs') && (
                  <p className="setting-info-text">Switch on for character output refined for mobile play.</p>
                )}
              </div>
            )}
          </div>
          {(() => {
            const skipOrNext = isAnimating
              ? { label: 'Skip ›', action: skipAnimation, active: true }
              : awaitingNextRound
              ? { label: 'Next Round ›', action: sendNextRound, active: true }
              : { label: 'Next Turn ›', action: sendNext, active: awaitingNext }
            return (
              <button ref={nextBtnRef} className="next-turn-btn" onClick={skipOrNext.action} disabled={!skipOrNext.active}>
                {skipOrNext.label}
              </button>
            )
          })()}
          {devMode && (status === 'done' || status === 'error') && (
            <button className="next-turn-btn" onClick={restartGame} title="Restart from scratch (dev)">
              ⟳ Refresh
            </button>
          )}
          <span className={`start-btn status-${status}`} style={{ cursor: 'default' }}>
            {status === 'connecting' && 'Connecting…'}
            {status === 'running' && (awaitingNext && !isAnimating ? 'Waiting…' : 'Running…')}
            {status === 'done' && '✓ Done'}
            {status === 'error' && '⚠ Error'}
          </span>
        </div>
      </header>

      {exitConfirmOpen && (
        <div className="modal-overlay" onClick={() => setExitConfirmOpen(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <div className="modal-title">Exit game?</div>
            <div className="modal-body">Return to the lobby. The current game will end.</div>
            <div className="modal-actions">
              <button className="modal-btn" onClick={() => setExitConfirmOpen(false)}>Cancel</button>
              <button className="modal-btn modal-btn-primary" onClick={() => { setExitConfirmOpen(false); exitGame() }}>OK</button>
            </div>
          </div>
        </div>
      )}

      <div className="app-body">
        <aside
          className={`sidebar-left ${settings.leftSidebarOpen === false ? 'collapsed' : ''}`}
          style={{ width: settings.leftSidebarOpen === false ? 0 : (settings.leftSidebarWidth ?? 220) }}
        >
          <div className="round-info">
            {phaseRounds.length > 0
              ? <p className="round-info-name">{phaseRounds[currentRoundIndex]}</p>
              : <p className="round-info-empty">—</p>
            }
          </div>
          <RoundWidget widget={widget} />
          <SegmentTracker titles={segmentTitles} markers={feedMarkers} />

        </aside>
        <button
          className="sidebar-toggle sidebar-toggle-left"
          onMouseDown={onLeftResizeStart}
          onMouseMove={(e) => {
            const rect = e.currentTarget.getBoundingClientRect()
            const offsetY = e.clientY - rect.top
            const dist = Math.abs(offsetY - rect.height / 2)
            const next = dist <= 24 ? 'pointer' : 'col-resize'
            if (next !== leftToggleCursor) setLeftToggleCursor(next)
          }}
          style={{ cursor: leftToggleCursor }}
        >
          {settings.leftSidebarOpen === false ? '›' : '‹'}
        </button>

        <div className="feed-col">
          <main
            className="feed"
            ref={feedRef}
            onScroll={handleFeedScroll}
            onWheel={handleUserScrollIntent}
            onTouchMove={handleUserScrollIntent}
            onMouseDown={handleFeedMouseDown}
            onMouseUp={handleFeedMouseUp}
            style={{ display: showPrivateChats && activeTab === 'private' ? 'none' : undefined }}
          >
            <ThreadedFeed
              events={visibleEvents}
              colorMap={colorMapRef.current}
              animateText={animateText}
              autoExpandThoughts={!!autoExpandThoughts}
              onAnimationComplete={onAnimationComplete}
              skipRef={skipRef}
              sendNextRound={sendNextRound}
              awaitingNextRound={awaitingNextRound}
              sendNext={sendNext}
              awaitingNext={awaitingNext}
              startLevel={startLevel}
              runthroughId={replayRunthroughId}
            />
            <div ref={bottomRef} />
          </main>
          {showPrivateChats && (
            <main
              className="feed"
              style={{ display: activeTab === 'private' ? undefined : 'none' }}
            >
              <PrivateChatsPanel conversations={privateConversations} colorMap={colorMapRef.current} />
              <div ref={privateBottomRef} />
            </main>
          )}
          <InputRequest request={inputRequest} onSubmitForm={submitInputForm} playerNames={playerNames} transcribe={transcribe} transcriptionEnabled={transcriptionEnabled} awaitingNext={awaitingNext} sendNext={sendNext} skipAnimation={skipAnimation} isAnimating={isAnimating} awaitingNextRound={awaitingNextRound} sendNextRound={sendNextRound} />
        </div>

        <button
          className="sidebar-toggle"
          onMouseDown={onRightResizeStart}
          onMouseMove={(e) => {
            const rect = e.currentTarget.getBoundingClientRect()
            const offsetY = e.clientY - rect.top
            const dist = Math.abs(offsetY - rect.height / 2)
            const next = dist <= 24 ? 'pointer' : 'col-resize'
            if (next !== rightToggleCursor) setRightToggleCursor(next)
          }}
          style={{ cursor: rightToggleCursor }}
        >
          {settings.sidebarOpen === false ? '‹' : '›'}
        </button>
        <aside
          className={`sidebar ${settings.sidebarOpen === false ? 'collapsed' : ''}`}
          style={{ width: settings.sidebarOpen === false ? 0 : (settings.rightSidebarWidth ?? 200) }}
        >
          <Scoreboard scores={scores} evicted={evicted} />
          <RoundTracker rounds={phaseRounds} currentIndex={currentRoundIndex} />
        </aside>
      </div>
    </div>
  )
}
