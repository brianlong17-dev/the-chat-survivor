import { useState, useEffect, useRef } from 'react'

// --- WordByWord animation parameters ---
const WORD_ANIM_START_DELAY_MS = 80        // pause before first word begins
const WORD_ANIM_SPEED_BUDGET_MS = 500      // total ms per sentence; divided by word count for per-word delay
const WORD_ANIM_MAX_WORD_MS = 70           // cap per-word delay so short sentences don't drag (kicks in ≤6 words)

const WORD_ANIM_BETWEEN_SENTENCE_MS = 300  // base gap after finishing one sentence before the next starts
const WORD_ANIM_BETWEEN_SENTENCES_VARIANT = [100, 200, 300, 0, ]  // per-sentence offset added to base, cycles

const WORD_ANIM_DOT_START_DELAY_MS = 300   // pause before the "..." dots begin
const WORD_ANIM_DOT_STEP_MS = 400          // interval between each dot step ( . → .. → ... )
const WORD_ANIM_DOT_HOLD_MS = 600          // how long "..." shows before clearing and moving on
const WORD_ANIM_SNAP_ENABLED = false       // when false, all sentences animate word-by-word (no snapping)
const WORD_ANIM_SNAP_LIMIT = 3             // sentences animated word-by-word before rest is snapped instantly
const WORD_ANIM_SNAP_PAUSE_MS = 400        // pause before flushing snapped sentences
const WORD_ANIM_SNAP_FADE_S = 0.4          // CSS fade-in duration (seconds) for snapped text
const WORD_ANIM_END_LINGER_CHOICES_MS = [1000, 1500, 2000, 2500]  // cursor linger at end; one picked at random per message

const SPEAKER_COLORS = [
  '#e07b54', '#5b8dd9', '#67b37d', '#c97bc4',
  '#d4a84b', '#5bbccc', '#d9706a', '#8d7fd9',
]

export function getSpeakerColor(name, colorMap) {
  if (!colorMap[name]) {
    const idx = Object.keys(colorMap).length % SPEAKER_COLORS.length
    colorMap[name] = SPEAKER_COLORS[idx]
  }
  return colorMap[name]
}

function renderBold(text) {
  const parts = text.split(/(\*[^*\n]+\*)/g)
  return parts.map((part, i) => {
    if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
      return <span key={i} className="msg-bold">{part.slice(1, -1)}</span>
    }
    return part
  })
}

function HostStagger({ text, onComplete, skipRef, animateText }) {
  const onCompleteRef = useRef(onComplete)
  useEffect(() => { onCompleteRef.current = onComplete }, [onComplete])
  const doneRef = useRef(false)

  useEffect(() => {
    if (!animateText) { onCompleteRef.current?.(); return }

    const finish = () => {
      if (doneRef.current) return
      doneRef.current = true
      onCompleteRef.current?.()
    }
    const t = setTimeout(finish, 2000)               // 1s roll + 1s pause
    const skip = setInterval(() => {
      if (skipRef?.current) { clearInterval(skip); clearTimeout(t); finish() }
    }, 100)

    return () => { clearTimeout(t); clearInterval(skip) }
  }, [text])

  return <span className={animateText ? 'message-text host-roll' : 'message-text'}>{renderBold(text)}</span>
}

function WordByWord({ text, onComplete, skipRef, animateText }) {
  const [typed, setTyped] = useState('')
  const [snapped, setSnapped] = useState('')
  const [dots, setDots] = useState('')
  const [typing, setTyping] = useState(false)
  const onCompleteRef = useRef(onComplete)
  useEffect(() => { onCompleteRef.current = onComplete }, [onComplete])
  useEffect(() => {
    setTyped('')
    setSnapped('')
    setDots('')
    let timeoutId = null

    if (!animateText) {
      setTyped(text)
      setTyping(false)
      onCompleteRef.current?.()
      return
    }

    setTyping(false)

    const snap = () => {
      clearTimeout(timeoutId)
      setTyped(text)
      setSnapped('')
      setDots('')
      setTyping(false)
      onCompleteRef.current?.()
    }

    const checkSkip = () => {
      if (skipRef?.current) { snap(); return true }
      return false
    }

    const paragraphs = text.split('\n\n')

    const showDots = (onDone) => {
      setTyping(true)
      const steps = ['.', '..', '...']
      let i = 0
      const tick = () => {
        if (checkSkip()) return
        setDots(steps[i]); i++
        if (i < steps.length) timeoutId = setTimeout(tick, WORD_ANIM_DOT_STEP_MS)
        else timeoutId = setTimeout(() => { setDots(''); onDone() }, WORD_ANIM_DOT_HOLD_MS)
      }
      timeoutId = setTimeout(tick, WORD_ANIM_DOT_START_DELAY_MS)
    }

    const ABBREVIATIONS = /(?:^|\s)(?:Mr|Mrs|Ms|Dr|Prof|St|Sr|Jr|vs|etc|[A-Z])\.\s*$/
    const splitSentences = (para) => {
      const matches = para.match(/[^.!?]+[.!?]+[\s]*/g) || []
      const consumed = matches.join('').length
      if (consumed < para.length) matches.push(para.slice(consumed))
      // Merge fragments that end on an abbreviation ("Mr.", initials) into the next sentence.
      const merged = []
      for (const frag of matches) {
        if (merged.length && ABBREVIATIONS.test(merged[merged.length - 1])) {
          merged[merged.length - 1] += frag
        } else {
          merged.push(frag)
        }
      }
      return merged.length ? merged : [para]
    }

    const runParagraph = (paraIdx, onDone) => {
      if (paraIdx >= paragraphs.length) return
      if (checkSkip()) return
      const para = paragraphs[paraIdx]
      const prefix = paragraphs.slice(0, paraIdx).join('\n\n') + (paraIdx > 0 ? '\n\n' : '')
      const sentences = splitSentences(para)
      const isLast = paraIdx === paragraphs.length - 1

      const runSentence = (sentIdx, soFar) => {
        if (checkSkip()) return
        if (sentIdx >= sentences.length) {
          if (isLast) { onDone(); return }
          showDots(onDone)
          return
        }
        
        if (WORD_ANIM_SNAP_ENABLED && sentIdx >= WORD_ANIM_SNAP_LIMIT) {
          const rest = sentences.slice(sentIdx).join('')
          setSnapped(rest)
          setTyping(true)
          timeoutId = setTimeout(() => {
            if (checkSkip()) return
            setTyped(prefix + para)
            setSnapped('')
            if (isLast) { onDone(); return }
            showDots(onDone)
          }, WORD_ANIM_SNAP_PAUSE_MS)
          return
        }
        const sentence = sentences[sentIdx]
        const words = sentence.split(/(\s+)/)
        const wordCount = words.filter(w => w.trim()).length || 1
        const wordDelay = Math.min(Math.round(WORD_ANIM_SPEED_BUDGET_MS / wordCount), WORD_ANIM_MAX_WORD_MS)
        
        let wordIdx = 0
        const tickWord = () => {
          if (checkSkip()) return
          wordIdx++
          const current = soFar + words.slice(0, wordIdx).join('')
          setTyped(prefix + current)
          if (wordIdx < words.length) {
            setTyping(false)  // hide cursor while words are flowing
            timeoutId = setTimeout(tickWord, wordDelay)
          } else {
            setTyping(true)   // cursor rests at end of sentence
            const variant = WORD_ANIM_BETWEEN_SENTENCES_VARIANT[sentIdx % WORD_ANIM_BETWEEN_SENTENCES_VARIANT.length]
            timeoutId = setTimeout(() => runSentence(sentIdx + 1, current), WORD_ANIM_BETWEEN_SENTENCE_MS + variant)
          }
        }
        tickWord()
      }

      runSentence(0, '')
    }

    const runAll = (paraIdx) => {
      if (paraIdx >= paragraphs.length) {
        // Let the cursor linger at the end before handing off to onComplete.
        setTyping(true)
        const linger = WORD_ANIM_END_LINGER_CHOICES_MS[Math.floor(Math.random() * WORD_ANIM_END_LINGER_CHOICES_MS.length)]
        timeoutId = setTimeout(() => {
          setTyping(false)
          onCompleteRef.current?.()
        }, linger)
        return
      }
      runParagraph(paraIdx, () => runAll(paraIdx + 1))
    }

    timeoutId = setTimeout(() => runAll(0), WORD_ANIM_START_DELAY_MS)
    return () => clearTimeout(timeoutId)
  }, [text])

  return (
    <span style={{ whiteSpace: 'pre-wrap' }}>
      {renderBold(typed)}
      {snapped && <span style={{ animation: `fadeIn ${WORD_ANIM_SNAP_FADE_S}s ease forwards` }}>{snapped}</span>}
      {dots && <span style={{ color: 'var(--text-dim)', marginLeft: 2 }}>{dots}</span>}
      {typing && <span className="type-cursor" />}
    </span>
  )
}

function PhaseHeader({ phase_number }) {
  return (
    <div className="msg phase-header">
      <span className="phase-line phase-line-left" />
      <span className="phase-label">PHASE {phase_number}</span>
      <span className="phase-line phase-line-right" />
    </div>
  )
}

function RoundHeader({ round_number, scores, onComplete }) {
  const [revealed, setRevealed] = useState('')
  const releasedRef = useRef(false)

  useEffect(() => {
    const t = setTimeout(() => {
      if (releasedRef.current) return
      releasedRef.current = true
      onComplete?.()
    }, 1500)
    return () => clearTimeout(t)
  }, [])

  useEffect(() => {
    if (!scores) return
    let i = 0
    const interval = 600 / scores.length
    const tick = setInterval(() => {
      i++
      setRevealed(scores.slice(0, i))
      if (i >= scores.length) clearInterval(tick)
    }, interval)
    return () => clearInterval(tick)
  }, [scores])

  return (
    <div className="msg round-header">
      <span className="round-label">Round {round_number}</span>
      {scores && <span className="round-scores">{revealed}</span>}
    </div>
  )
}

function PublicAction({ speaker, message, color, animate_as_player, onComplete, skipRef, animateText }) {
  const isHost = speaker === 'HOST'
  const isSystem = speaker === 'SYSTEM'   // shouldn't happen (backend asserts), render harmlessly

  const label = (isHost || isSystem)
    ? <span className="speaker system-speaker">{speaker}</span>
    : <span className="speaker" style={{ color }}>{speaker}</span>

  const body = () => {
    if (isSystem) return <span className="message-text">{renderBold(message)}</span>
    if (animate_as_player) return <WordByWord text={message} onComplete={onComplete} skipRef={skipRef} animateText={animateText} />
    if (isHost)   return <HostStagger text={message} onComplete={onComplete} skipRef={skipRef} animateText={animateText} />
    return <span className="message-text">{renderBold(message)}</span>
  }

  return (
    <div className={`msg public-action ${(isHost || isSystem) ? 'system' : ''}`}>
      {label}
      {body()}
    </div>
  )
}

function RoundSummary({ summary }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="msg round-summary">
      <button className="summary-toggle" onClick={() => setOpen(o => !o)}>
        {open ? '▼' : '▶'} Round Summary
      </button>
      {open && <p className="summary-text">{summary}</p>}
    </div>
  )
}

function PrivateThought({ speaker, message, color }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="msg private-thought">
      <button className="thought-toggle" onClick={() => setOpen(o => !o)}>
        {open ? '▼' : '▶'}{' '}
        <span style={{ color }}>{speaker}</span>
        <span className="thought-label"> (thinking...)</span>
      </button>
      {open && <p className="thought-text">{message}</p>}
    </div>
  )
}

function LoadingMessage({ message, done, completed_message }) {
  if (done && completed_message) {
    return (
      <div className="msg loading-message">
        <span className="loading-text">{completed_message}</span>
      </div>
    )
  }
  return (
    <div className="msg loading-message" style={done ? { visibility: 'hidden' } : undefined}>
      <span className="loading-text">{message}</span>
      <span className="loading-dot" style={{ animationDelay: '0s' }}>.</span>
      <span className="loading-dot" style={{ animationDelay: '0.2s' }}>.</span>
      <span className="loading-dot" style={{ animationDelay: '0.4s' }}>.</span>
    </div>
  )
}

function SystemPrivate({ message, border_bottom }) {
  return (
    <div className={`msg system-private${border_bottom ? ' border-bottom' : ''}`}>
      <span className="sys-icon">⚙</span>
      <span className="sys-text">{message}</span>
    </div>
  )
}

function SystemPublic({ message, border_bottom }) {
  return (
    <div className={`msg system-public${border_bottom ? ' border-bottom' : ''}`}>
      <span className="sys-icon">⚙</span>
      <span className="sys-text">{message}</span>
    </div>
  )
}

function GameOver({ winners }) {
  let text, trophy
  if (!winners || winners.length === 0) {
    text = 'No one wins, sadly enough.'
    trophy = ':('
  } else if (winners.length === 1) {
    text = `${winners[0]} wins!`
    trophy = '🏆'
  } else {
    text = `Winners: ${winners.join(' & ')}!`
    trophy = '🏆 '.repeat(winners.length)
  }
  return (
    <div className="msg game-over">
      <div className="trophy">{trophy}</div>
      <div className="winner-text">{text}</div>
    </div>
  )
}

function ErrorMsg({ message }) {
  return (
    <div className="msg error-msg">
      <span className="error-icon">⚠</span> {message}
    </div>
  )
}

function FeedMarker({ label }) {
  const id = `feed-${label.toLowerCase().replace(/\s+/g, '-')}`
  return <div id={id} style={{ height: 0 }} />
}

export function groupThread(msgs) {
  const groups = []
  for (const m of msgs) {
    const last = groups.length > 0 ? groups[groups.length - 1] : null
    if (m.child && last) {
      if (last.kind === 'thread') {
        last.children.push(m)
      } else {
        groups[groups.length - 1] = { kind: 'thread', root: last.msg, children: [m] }
      }
    } else if (m.type === 'private_thought' && last && last.kind === 'thread') {
      last.children.push(m)
    } else {
      groups.push({ kind: 'single', msg: m })
    }
  }
  return groups
}

function packBlocks(children) {
  const blocks = []
  let i = 0
  while (i < children.length) {
    const c = children[i]
    const next = children[i + 1]
    if (
      c.type === 'public_action' &&
      next && next.type === 'private_thought' && next.speaker === c.speaker
    ) {
      blocks.push({ msg: c, thinking: next })
      i += 2
    } else {
      blocks.push({ msg: c })
      i++
    }
  }
  return blocks
}

function NextRoundButton({ onSend, nextRoundButtonActive}) {
  return (
    <div
      className={`feed-next-round-btn${!nextRoundButtonActive ? ' clicked' : ''}`}
      onClick={() => { if (nextRoundButtonActive) onSend?.() }}
    >
      NEXT ROUND ›
    </div>
  )
}

const HOST_RAIL = '#8a8a8a'

function railColor(msg, colorMap) {
  if (msg.speaker === 'HOST' || msg.speaker === 'SYSTEM') return HOST_RAIL
  return getSpeakerColor(msg.speaker, colorMap)
}

export function ThreadedFeed({ events, colorMap, animateText, onAnimationComplete, skipRef, sendNextRound, awaitingNextRound}) {
  const groups = groupThread(events)
  const lastEvent = events[events.length - 1]
  const lastNextRoundIdx = events.reduce((acc, e, i) => e.type === 'next_round_request' ? i : acc, -1)

  function onRoundHeaderComplete() {
    onAnimationComplete()
  }

  const renderMsg = (evt) => {
    const isLast = evt === lastEvent
    return (
      <Message
        event={evt}
        colorMap={colorMap}
        onComplete={isLast ? onAnimationComplete : undefined}
        onRoundHeaderComplete={onRoundHeaderComplete}
        skipRef={isLast ? skipRef : undefined}
        animateText={animateText}
        sendNextRound={sendNextRound}
        awaitingNextRound={awaitingNextRound && events.indexOf(evt) === lastNextRoundIdx}
      />
    )
  }

  return groups.map((g, gi) => {
    if (g.kind === 'single') {
      return <div key={gi}>{renderMsg(g.msg)}</div>
    }
    const blocks = packBlocks(g.children)
    return (
      <div className="thread" key={gi}>
        {renderMsg(g.root)}
        <div className="thread-children">
          {blocks.map((b, bi) => (
            <div
              key={bi}
              className="reply-block"
              style={{ '--reply-color': railColor(b.msg, colorMap) }}
            >
              {renderMsg(b.msg)}
              {b.thinking && renderMsg(b.thinking)}
            </div>
          ))}
        </div>
      </div>
    )
  })
}

export function Message({ event, colorMap, onComplete, onRoundHeaderComplete, skipRef, animateText, sendNextRound, awaitingNextRound }) {
  switch (event.type) {
    case 'phase_header':
      return <PhaseHeader {...event} />
    case 'round_start':
      return <RoundHeader {...event} onComplete={onRoundHeaderComplete} />
    case 'public_action':
      return <PublicAction {...event} color={getSpeakerColor(event.speaker, colorMap)} onComplete={onComplete} skipRef={skipRef} 
      animateText={animateText}/>
    case 'round_summary':
      return <RoundSummary {...event} />
    case 'private_thought':
      return <PrivateThought {...event} color={getSpeakerColor(event.speaker, colorMap)} />
    case 'system_private':
      return <SystemPrivate {...event} />
    case 'system_public':
      return <SystemPublic {...event} />
    case 'game_intro':
      return <PublicAction speaker="HOST" message={event.message} color="#aaa" />
    case 'game_over':
      return <GameOver winners={event.winners} />
    case 'error':
      return <ErrorMsg message={event.message} />
    case 'loading':
      return <LoadingMessage message={event.message} done={event.done} completed_message={event.completed_message} />
    case 'feed_marker':
      return <FeedMarker label={event.label} />
    case 'next_round_request':
      return <NextRoundButton onSend={sendNextRound} nextRoundButtonActive={awaitingNextRound} />
    case 'points_update':
    case 'turn_header':
    case 'phase_intro':
    case 'evicted_update':
    case 'loading_done':
    default:
      return null
  }
}
