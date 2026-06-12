import { useRef, useEffect, useState } from 'react'
import '../App.whatsapp.css'
import { ThreadedFeed } from '../components/Messages'
import Scoreboard from '../components/Scoreboard'
import RoundTracker from '../components/RoundTracker'
import RoundWidget from '../components/RoundWidget'
import InputRequest from '../components/InputRequest'
import SegmentTracker from '../components/SegmentTracker'
import PrivateChatsPanel from '../components/PrivateChatsPanel'
import { SpeechBubbleIcon, LockIcon, InfoIcon, ListIcon } from '../components/FeedIcons'

export default function GameViewMobile({
  status, events, scores, evicted,
  inputRequest, awaitingNext, phaseRounds, currentRoundIndex,
  submitInput, sendNext, skipAnimation, exitGame, transcribe, onAnimationComplete, skipRef,
  isAnimating, settings, updateSetting, feedMarkers, segmentTitles, widget,
  privateConversations, playerNames = [], transcriptionEnabled, sendNextRound, awaitingNextRound
}) {
  const { showPrivate, autoRun, animateText, showPrivateChats, mobileOutputs } = settings

  const [settingsOpen, setSettingsOpen] = useState(false)
  const [mobileOutputsInfoOpen, setMobileOutputsInfoOpen] = useState(false)
  const [exitConfirmOpen, setExitConfirmOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('feed')
  const [seenPrivateCount, setSeenPrivateCount] = useState(0)
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(false)
  const [rightSidebarOpen, setRightSidebarOpen] = useState(false)
  const settingsRef = useRef(null)
  const colorMapRef = useRef({})
  const bottomRef = useRef(null)
  const feedRef = useRef(null)
  const privateBottomRef = useRef(null)
  const lastSeenPrivateCountRef = useRef(0)
  const userScrolledUpRef = useRef(false)
  const feedMouseDownPosRef = useRef(null)
  const feedMouseIsDownRef = useRef(false)

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
    if (activeTab !== 'private') return
    if (privateConversations.length > lastSeenPrivateCountRef.current) {
      lastSeenPrivateCountRef.current = privateConversations.length
      privateBottomRef.current?.scrollIntoView({ behavior: 'instant' })
    }
  }, [privateConversations, activeTab])

  const visibleEvents = showPrivate
    ? events
    : events.filter(e => e.type !== 'private_thought')

  return (
    <div className="app-mobile">
      <header className="app-header-mobile">
        <div className="header-left-mobile">
          <div className="settings-menu" ref={settingsRef}>
            <button className="hamburger-btn-mobile" onClick={() => setSettingsOpen(o => !o)} title="Menu">
              <span /><span /><span />
            </button>
            {settingsOpen && (
              <div className="settings-dropdown-mobile settings-dropdown-left-mobile">
                <label className="toggle-label">
                  <input type="checkbox" checked={showPrivate} onChange={e => updateSetting('showPrivate', e.target.checked)} />
                  Show private thoughts
                </label>
                <label className="toggle-label">
                  <input type="checkbox" checked={autoRun} onChange={e => updateSetting('autoRun', e.target.checked)} />
                  Auto-run
                </label>
                <label className="toggle-label">
                  <input type="checkbox" checked={animateText} onChange={e => updateSetting('animateText', e.target.checked)} />
                  Animate text
                </label>
                <label className="toggle-label">
                  <input type="checkbox" checked={showPrivateChats} onChange={e => updateSetting('showPrivateChats', e.target.checked)} />
                  Show private conversations
                </label>
                <div className="toggle-label-with-info">
                  <label className="toggle-label">
                    <input type="checkbox" checked={!!mobileOutputs} onChange={e => updateSetting('mobileOutputs', e.target.checked)} />
                    Mobile outputs
                  </label>
                  <button
                    className="setting-info-btn"
                    onClick={e => { e.stopPropagation(); setMobileOutputsInfoOpen(o => !o) }}
                    title="About mobile outputs"
                  >ⓘ</button>
                </div>
                {mobileOutputsInfoOpen && (
                  <p className="setting-info-text">Switch on for character output refined for mobile play.</p>
                )}
                <div className="settings-divider-mobile" />
                <button className="settings-lobby-btn-mobile" onClick={() => { setSettingsOpen(false); setExitConfirmOpen(true) }}>
                  Return to Lobby
                </button>
              </div>
            )}
          </div>
        </div>
        <div className="header-controls-mobile">
          {showPrivateChats && (
            <button
              className={`feed-switch-btn-mobile${activeTab === 'private' ? ' private' : ''}`}
              onClick={() => { setActiveTab(activeTab === 'feed' ? 'private' : 'feed'); if (activeTab === 'feed') setSeenPrivateCount(privateConversations.length) }}
              title={activeTab === 'feed' ? 'Switch to private' : 'Switch to feed'}
            >
              {activeTab === 'feed' ? <SpeechBubbleIcon size={16} /> : <LockIcon size={16} />}
            </button>
          )}
          <button
            className={`sidebar-toggle-btn-mobile${leftSidebarOpen ? ' active' : ''}`}
            onClick={() => setLeftSidebarOpen(o => !o)}
            title="Round info"
          >
            <InfoIcon size={16} />
          </button>
          <button
            className={`sidebar-toggle-btn-mobile${rightSidebarOpen ? ' active' : ''}`}
            onClick={() => setRightSidebarOpen(o => !o)}
            title="Scores"
          >
            <ListIcon size={16} />
          </button>
          {(() => {
            const skipOrNext = isAnimating
              ? { label: 'Skip', action: skipAnimation, active: true }
              : awaitingNextRound
              ? { label: 'Next Round', action: sendNextRound, active: true }
              : { label: 'Next Turn', action: sendNext, active: awaitingNext && !autoRun }
            return (
              <button className="next-turn-btn-mobile" onClick={skipOrNext.action} disabled={!skipOrNext.active}>
                {skipOrNext.label}
              </button>
            )
          })()}
          <span className={`start-btn-mobile status-${status}`} style={{ cursor: 'default' }}>
            {status === 'connecting' && '○'}
            {status === 'running' && (awaitingNext && !autoRun && !isAnimating ? '⋯' : '▶')}
            {status === 'done' && '✓'}
            {status === 'error' && '⚠'}
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

      <div className="app-body-mobile">
        {/* Main feed */}
        <div className="feed-col-mobile">
          <main
            className="feed-mobile"
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
              onAnimationComplete={onAnimationComplete}
              skipRef={skipRef}
              sendNextRound={sendNextRound}
              awaitingNextRound={awaitingNextRound}
            />
            <div ref={bottomRef} />
          </main>

          {showPrivateChats && (
            <main
              className="feed-mobile"
              style={{ display: activeTab === 'private' ? undefined : 'none' }}
            >
              <PrivateChatsPanel conversations={privateConversations} colorMap={colorMapRef.current} />
              <div ref={privateBottomRef} />
            </main>
          )}

          <InputRequest
            request={inputRequest}
            onSubmit={submitInput}
            playerNames={playerNames}
            transcribe={transcribe}
            transcriptionEnabled={transcriptionEnabled}
          />
        </div>

        {/* Left sidebar overlay - round info, widget, tracker */}
        {leftSidebarOpen && (
          <div className="sidebar-overlay-mobile" onClick={() => setLeftSidebarOpen(false)}>
            <aside
              className="sidebar-mobile sidebar-left-mobile"
              onClick={e => e.stopPropagation()}
            >
              <div className="sidebar-header-mobile">
                <button
                  className="sidebar-close-btn-mobile"
                  onClick={() => setLeftSidebarOpen(false)}
                >
                  ✕
                </button>
              </div>
              <div className="round-info">
                {phaseRounds.length > 0
                  ? <p className="round-info-name">{phaseRounds[currentRoundIndex]}</p>
                  : <p className="round-info-empty">—</p>
                }
              </div>
              <RoundWidget widget={widget} />
              <SegmentTracker titles={segmentTitles} markers={feedMarkers} />
            </aside>
          </div>
        )}

        {/* Right sidebar overlay - scoreboard, round tracker */}
        {rightSidebarOpen && (
          <div className="sidebar-overlay-mobile" onClick={() => setRightSidebarOpen(false)}>
            <aside
              className="sidebar-mobile sidebar-right-mobile"
              onClick={e => e.stopPropagation()}
            >
              <div className="sidebar-header-mobile">
                <button
                  className="sidebar-close-btn-mobile"
                  onClick={() => setRightSidebarOpen(false)}
                >
                  ✕
                </button>
              </div>
              <Scoreboard scores={scores} evicted={evicted} />
              <RoundTracker rounds={phaseRounds} currentIndex={currentRoundIndex} />
            </aside>
          </div>
        )}

      </div>
    </div>
  )
}
