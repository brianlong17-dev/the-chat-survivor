/**
 * RoundWidget — context-aware left-sidebar widget.
 *
 * Driven by `widget_update` events from the server.
 * Server sends: { type: 'widget_update', widget: { kind, ...data } }
 *
 * Supported kinds:
 *   'voting' — live vote tally
 *     data: {
 *       nominees: [{ name, votes }],
 *       voters_done: [{ name, voted_for } | string],
 *       voters_pending: string[],
 *       is_final: boolean,  // true → leader gets gold + sparks (count-based)
 *       winners: string[],  // optional override: these names go gold + sparks
 *       losers: string[],   // optional override: these names go red (executed)
 *     }
 *
 *   When `winners`/`losers` are present they take over highlighting entirely —
 *   count-based leading/winner coloring is ignored and only the listed names
 *   are colored (gold for winners, red/blood for losers, neutral otherwise).
 */

import { useEffect, useRef, useState } from 'react'

const GOLD_COLORS = ['#f5d376','#c9a84c','#e8c050','#fbeaa0','#a07820']
const BLOOD_COLORS = ['#8b1a1a','#a02020','#c0392b','#7b1010','#6b0f0f']

const THEME = {
  gold:  { winner: '#c9a84c', sparks: GOLD_COLORS },
  blood: { winner: '#c0392b', sparks: BLOOD_COLORS },
}

function SparkCanvas({ colors = GOLD_COLORS }) {
  const canvasRef = useRef(null)
  const rafRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const particles = []

    const syncSize = () => {
      if (canvas.offsetWidth > 0) {
        canvas.width = canvas.offsetWidth
        canvas.height = canvas.offsetHeight || 120
      }
    }
    syncSize()
    const ro = new ResizeObserver(syncSize)
    ro.observe(canvas)

    const spawn = () => {
      const x = Math.random() * canvas.width
      particles.push({
        x, y: 0,
        vx: (Math.random() - 0.5) * 0.4,
        vy: Math.random() * 0.7 + 0.2,
        life: 1,
        decay: Math.random() * 0.025 + 0.018,
        size: Math.random() * 0.9 + 0.3,
        color: colors[Math.floor(Math.random() * colors.length)],
        trail: [],
      })
    }

    const tick = () => {
      const spawnCount = Math.floor(Math.random() * 2) + 1
      for (let i = 0; i < spawnCount; i++) spawn()

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i]
        p.trail.push({ x: p.x, y: p.y, life: p.life })
        if (p.trail.length > 6) p.trail.shift()

        p.x += p.vx
        p.vy += 0.02
        p.vx *= 0.995
        p.y += p.vy
        p.life -= p.decay

        if (p.life <= 0 || p.y > canvas.height) { particles.splice(i, 1); continue }

        for (let t = 0; t < p.trail.length; t++) {
          const tp = p.trail[t]
          ctx.beginPath()
          ctx.arc(tp.x, tp.y, p.size * 0.5, 0, Math.PI * 2)
          ctx.fillStyle = p.color
          ctx.globalAlpha = (t / p.trail.length) * p.life * 0.2
          ctx.fill()
        }

        const s = p.size * 1.6
        ctx.fillStyle = p.color
        ctx.globalAlpha = p.life * 0.6
        ctx.fillRect(p.x - s / 2, p.y - s / 2, s, s)

        if (Math.random() < 0.02) {
          ctx.beginPath()
          ctx.arc(p.x, p.y, p.size * 2, 0, Math.PI * 2)
          ctx.fillStyle = '#fff8d0'
          ctx.globalAlpha = p.life * 0.15
          ctx.fill()
        }
      }

      ctx.globalAlpha = 1
      rafRef.current = requestAnimationFrame(tick)
    }

    rafRef.current = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(rafRef.current)
      ro.disconnect()
      ctx.clearRect(0, 0, canvas.width, canvas.height)
    }
  }, [colors])

  return (
    <div style={{ position: 'relative', height: 0, overflow: 'visible', pointerEvents: 'none' }}>
      <canvas
        ref={canvasRef}
        width="196"
        height="120"
        style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: 120, pointerEvents: 'none' }}
      />
    </div>
  )
}

function VoterSection({ voters_done, voters_pending, totalVoters }) {
  const [allOpen, setAllOpen] = useState(false)
  const [openSet, setOpenSet] = useState(new Set())

  const toggleAll = () => {
    if (allOpen) {
      setAllOpen(false)
      setOpenSet(new Set())
    } else {
      setAllOpen(true)
      setOpenSet(new Set(voters_done.map(v => typeof v === 'string' ? v : v.name)))
    }
  }

  const toggleOne = (name) => {
    setOpenSet(prev => {
      const next = new Set(prev)
      if (next.has(name)) next.delete(name)
      else next.add(name)
      return next
    })
  }

  return (
    <div className="rw-section">
      <h3 className="rw-label rw-label-toggle" onClick={toggleAll}>
        Voted
        <span className="rw-label-count">{voters_done.length}/{totalVoters}</span>
      </h3>
      <div className="rw-voters">
        {voters_done.map(v => {
          const name = typeof v === 'string' ? v : v.name
          const voted_for = typeof v === 'string' ? null : v.voted_for
          const isOpen = openSet.has(name)
          return (
            <div
              key={name}
              className={`rw-voter rw-voter--done ${isOpen ? 'expanded' : ''}`}
              onClick={() => voted_for && toggleOne(name)}
            >
              <div className="rw-voter-row">
                <span className="rw-voter-tick">›</span>
                <span className="rw-voter-name">{name}</span>
              </div>
              {isOpen && voted_for && (
                <div className="rw-voter-voted-for">↳ {voted_for}</div>
              )}
            </div>
          )
        })}
        {voters_pending.map(v => {
          const name = typeof v === 'string' ? v : v.name
          return (
            <div key={name} className="rw-voter rw-voter--pending">
              <div className="rw-voter-row">
                <span className="rw-voter-tick"> </span>
                <span className="rw-voter-name">{name}</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function VotingWidget({ nominees = [], voters_done = [], voters_pending = [], is_final = false, theme = 'gold', winners = [], losers = [] }) {
  const totalVoters = voters_done.length + voters_pending.length
  const sorted = [...nominees].sort((a, b) => (b.votes || 0) - (a.votes || 0))
  const maxVotes = sorted[0]?.votes || 1
  const t = THEME[theme] || THEME.gold
  const blood = THEME.blood

  const hasOverride = winners.length > 0 || losers.length > 0
  const winnerSet = new Set(winners)
  const loserSet = new Set(losers)

  return (
    <div className="round-widget">
      <div className="rw-section">
        <h3 className="rw-label">Vote</h3>
        <div className="rw-nominees">
          {sorted.map(({ name, votes = 0 }) => {
            let pct = maxVotes > 0 ? (votes / maxVotes) * 100 : 0

            let isWinner, isLoser, isLeading
            if (hasOverride) {
              // explicit lists take over — ignore count-based coloring
              isWinner = winnerSet.has(name)
              isLoser = loserSet.has(name)
              isLeading = false
            } else {
              isLeading = votes === maxVotes && votes > 0
              isWinner = is_final && isLeading
              isLoser = false
            }

            // a pushed winner/loser always shows a full bar, even at 0 votes
            if (isWinner || isLoser) pct = 100

            const highlightColor = isLoser ? blood.winner : (isWinner ? t.winner : undefined)
            const cls = isLoser ? 'loser' : (isWinner ? 'winner' : (isLeading ? 'leading' : ''))
            return (
              <div key={name} className={`rw-nominee ${cls}`}
                   style={highlightColor ? { '--winner-color': highlightColor } : {}}>
                <div className="rw-nominee-header">
                  <span className="rw-nominee-name">{name}</span>
                  <span className="rw-nominee-count">{votes}</span>
                </div>
                <div className="rw-bar-track">
                  <div className="rw-bar-fill" style={{ width: `${pct}%` }} />
                </div>
                {isWinner && <SparkCanvas colors={t.sparks} />}
                {isLoser && <SparkCanvas colors={blood.sparks} />}
              </div>
            )
          })}
        </div>
      </div>

      {(voters_done.length > 0 || voters_pending.length > 0) && (
        <VoterSection
          voters_done={voters_done}
          voters_pending={voters_pending}
          totalVoters={totalVoters}
        />
      )}
    </div>
  )
}

const RPS_RESULT_COLOR = { winner: '#67b37d', loser: '#d9706a', draw: '#67b37d' }

const ICON_PROPS = { width: '100%', height: '100%', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.6, strokeLinecap: 'round', strokeLinejoin: 'round' }

function IconRock() {
  return (
    <svg {...ICON_PROPS}>
      <path d="M12 4 L18.5 8.5 L19.5 15.5 L14 20 L8 19 L4.5 12.5 Z" />
    </svg>
  )
}

function IconPaper() {
  return (
    <svg {...ICON_PROPS}>
      <rect x="5.5" y="3.5" width="13" height="17" rx="0.5" />
      <line x1="8.5" y1="9" x2="15.5" y2="9" />
      <line x1="8.5" y1="12.5" x2="15.5" y2="12.5" />
      <line x1="8.5" y1="16" x2="13" y2="16" />
    </svg>
  )
}

function IconScissors() {
  return (
    <svg {...ICON_PROPS}>
      <circle cx="6" cy="6.5" r="2.25" />
      <circle cx="6" cy="17.5" r="2.25" />
      <line x1="8" y1="7.8" x2="20" y2="18.5" />
      <line x1="8" y1="16.2" x2="20" y2="5.5" />
    </svg>
  )
}

function IconLock() {
  return (
    <svg {...ICON_PROPS}>
      <rect x="6" y="11" width="12" height="9" rx="1.5" />
      <path d="M8.5 11 V8 a3.5 3.5 0 0 1 7 0 v3" />
    </svg>
  )
}

const CHOICE_ICON = { rock: IconRock, paper: IconPaper, scissors: IconScissors }

function RpsRow({ name, state, choice, result, points }) {
  const color = RPS_RESULT_COLOR[result]
  const ChoiceIcon = CHOICE_ICON[choice]

  return (
    <div
      className={`rw-rps-row rw-rps-row--${state}`}
      style={color ? { '--winner-color': color } : {}}
    >
      <span className="rw-rps-name" style={color ? { color } : {}}>
        {name}
        {state === 'revealed' && points > 0 && (
          <span className="rw-rps-points" style={color ? { color } : {}}> +{points}</span>
        )}
      </span>
      <span
        className={`rw-rps-icon rw-rps-icon--${state}`}
        style={state === 'revealed' && color ? { color } : {}}
      >
        {state === 'waiting'  && <span className="rw-rps-dots">···</span>}
        {state === 'picked'   && <IconLock />}
        {state === 'revealed' && ChoiceIcon && <ChoiceIcon />}
      </span>
    </div>
  )
}

function RpsWidget({ pairs = [] }) {
  return (
    <div className="round-widget">
      <div className="rw-section">
        <h3 className="rw-label">Rock Paper Scissors</h3>
        <div className="rw-nominees rw-nominees--rps">
          {pairs.map((pair, i) => (
            <div key={i} className="rw-pair">
              <RpsRow {...pair[0]} />
              <div className="rw-pair-vs">vs</div>
              <RpsRow {...pair[1]} />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

const GUESS_RESULT_COLOR = { correct: '#67b37d', incorrect: '#d9706a' }

function GuessRow({ name, state, guess, correct, points }) {
  const result = state === 'revealed' && correct != null ? (correct ? 'correct' : 'incorrect') : undefined
  const color = GUESS_RESULT_COLOR[result]

  return (
    <div className={`rw-guess-row rw-guess-row--${state}`}>
      <span className="rw-guess-name" style={color ? { color } : {}}>
        {name}
        {state === 'revealed' && points > 0 && (
          <span className="rw-guess-points" style={color ? { color } : {}}> +{points}</span>
        )}
      </span>
      <span
        className={`rw-guess-icon rw-guess-icon--${state}`}
        style={state === 'revealed' && color ? { color, borderColor: color } : {}}
      >
        {state === 'waiting' && <span className="rw-rps-dots">···</span>}
        {state === 'picked' && <IconLock />}
        {state === 'revealed' && <span className="rw-guess-number">{guess}</span>}
      </span>
    </div>
  )
}

function GuessWidget({ range, rows = [] }) {
  const rangeLabel = range ? `${range.min}–${range.max}?` : ''
  return (
    <div className="round-widget">
      <div className="rw-section">
        <h3 className="rw-label">
          Guess the Number
          {rangeLabel && <span className="rw-label-count rw-label-count-text">{rangeLabel}</span>}
        </h3>
        <div className="rw-nominees">
          {rows.map((row, i) => <GuessRow key={i} {...row} />)}
        </div>
      </div>
    </div>
  )
}

// Two overlapping circles — one shared glyph per pair, not per player.
// Each side independently can be: unknown (grey dashed), picked-but-not-final
// (colored dashed — backend reveals choices in order, so one side often lands
// before the other), or fully revealed (colored solid).
const PD_CHOICE_COLOR = { split: '#67b37d', steal: '#d9706a' }

function pdDotState(p) {
  if (!p.choice) return { color: '#444', dashed: true }
  return { color: PD_CHOICE_COLOR[p.choice], dashed: p.state !== 'revealed' }
}

function PdOutcomeIcon({ a, b }) {
  const dotA = pdDotState(a)
  const dotB = pdDotState(b)
  return (
    <svg width="100%" height="100%" viewBox="0 0 28 30" fill="none" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="14" cy="10.5" r="7.5" stroke={dotA.color} strokeDasharray={dotA.dashed ? '2.5 3' : undefined} />
      <circle cx="14" cy="19.5" r="7.5" stroke={dotB.color} strokeDasharray={dotB.dashed ? '2.5 3' : undefined} />
    </svg>
  )
}

function PdStatus({ state }) {
  if (state === 'revealed') return null
  if (state === 'picked') {
    return (
      <span className="rw-pd-status">
        <svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
          <rect x="6" y="11" width="12" height="9" rx="1.5" />
          <path d="M8.5 11 V8 a3.5 3.5 0 0 1 7 0 v3" />
        </svg>
      </span>
    )
  }
  return <span className="rw-pd-status rw-pd-status-dots">···</span>
}

function PdRow({ name, state, choice, points }) {
  const color = state === 'revealed' ? PD_CHOICE_COLOR[choice] : undefined
  return (
    <div className={`rw-pd-row rw-pd-row--${state}`}>
      <span className="rw-pd-name" style={color ? { color } : {}}>
        {name}
        {state === 'revealed' && points > 0 && (
          <span className="rw-pd-points" style={color ? { color } : {}}> +{points}</span>
        )}
      </span>
      <PdStatus state={state} />
    </div>
  )
}

function PdWidget({ pairs = [] }) {
  return (
    <div className="round-widget">
      <div className="rw-section">
        <h3 className="rw-label">Prisoner's Dilemma</h3>
        <div className="rw-nominees rw-nominees--rps">
          {pairs.map((pair, i) => {
            const [a, b] = pair
            return (
              <div key={i} className="rw-pair">
                <PdRow {...a} />
                <div className="rw-pair-vs">
                  <span className="rw-pair-vs-icon">
                    <PdOutcomeIcon a={a} b={b} />
                  </span>
                </div>
                <PdRow {...b} />
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

// Give & Take — a sequential turn list, not simultaneous pairs. Each turn is
// one player's move: they pick a target and either GIVE (target gains, actor
// unaffected — grows the shared pot) or TAKE (zero-sum — actor gains exactly
// what the target loses). The target/action only exist once a turn is
// revealed — pre-decision turns render as a single bare row (no placeholder
// pair), since there's nothing to show yet.
const GT_ACTION_COLOR = { give: '#67b37d', take: '#d9706a' }

function GtTurn({ order, actor, state, target, action, amount = 3, actor_amount, target_amount }) {
  if (state !== 'revealed') {
    // Name and pending label stack on separate lines — sharing one line made
    // longer names ("Princess Leia") truncate against the label.
    return (
      <div className={`rw-gt-turn rw-gt-turn--${state}`}>
        <div className="rw-gt-line">
          <span className="rw-gt-order">{order}</span>
          <span className="rw-gt-name">{actor}</span>
        </div>
        <span className="rw-gt-pending-label">{state === 'picked' ? 'deciding···' : 'awaiting turn'}</span>
      </div>
    )
  }

  if (action === 'pass') {
    return (
      <div className="rw-gt-turn rw-gt-turn--revealed">
        <div className="rw-gt-line">
          <span className="rw-gt-order">{order}</span>
          <span className="rw-gt-name">{actor}</span>
        </div>
        <span className="rw-gt-pending-label">passed</span>
      </div>
    )
  }

  const isGive = action === 'give'
  // actor_amount/target_amount let a turn specify independent deltas (e.g.
  // sacrifice: actor spends N, target only loses what they had left) instead
  // of assuming a single zero-sum `amount` shared by both sides.
  const actorDelta = actor_amount !== undefined ? actor_amount : (isGive ? 0 : amount)
  const targetDelta = target_amount !== undefined ? target_amount : (isGive ? amount : -amount)
  // Name colors follow each side's own gain/loss (green = up, red = down,
  // untinted = unaffected) — NOT the action itself. A 'take' still colors the
  // taking actor green, because they gained; only their victim goes red.
  const actorColor = actorDelta > 0 ? GT_ACTION_COLOR.give : (actorDelta < 0 ? GT_ACTION_COLOR.take : undefined)
  const targetColor = targetDelta > 0 ? GT_ACTION_COLOR.give : (targetDelta < 0 ? GT_ACTION_COLOR.take : undefined)

  // Stacked, not side-by-side: each name gets the full card width so it never
  // truncates in the ~200px sidebar, even for longer names. The connector row
  // (hairline — arrow — hairline) mirrors the existing .rw-pair-vs idiom, just
  // vertical and colored/directional instead of a static "vs".
  return (
    <div className="rw-gt-turn rw-gt-turn--revealed">
      <div className="rw-gt-line">
        <span className="rw-gt-order">{order}</span>
        <span className="rw-gt-name" style={actorColor ? { color: actorColor } : {}}>{actor}</span>
        {actorDelta !== 0 && (
          <span className="rw-gt-points" style={{ color: actorColor }}>{actorDelta > 0 ? ` +${actorDelta}` : ` ${actorDelta}`}</span>
        )}
      </div>
      <div className="rw-gt-line rw-gt-line--target">
        <span className="rw-gt-name" style={targetColor ? { color: targetColor } : {}}>{target}</span>
        {targetDelta !== 0 && (
          <span className="rw-gt-points" style={{ color: targetColor }}>{targetDelta > 0 ? ` +${targetDelta}` : ` ${targetDelta}`}</span>
        )}
      </div>
    </div>
  )
}

function GiveTakeWidget({ turns = [] }) {
  return (
    <div className="round-widget">
      <div className="rw-section">
        <div className="rw-nominees">
          {turns.map((turn, i) => <GtTurn key={i} order={i + 1} {...turn} />)}
        </div>
      </div>
    </div>
  )
}

export default function RoundWidget({ widget }) {
  if (!widget || !widget.kind) return null
  switch (widget.kind) {
    case 'voting':    return <VotingWidget {...widget} />
    case 'rps':       return <RpsWidget {...widget} />
    case 'pd':        return <PdWidget {...widget} />
    case 'give_take': return <GiveTakeWidget {...widget} />
    case 'guess':     return <GuessWidget {...widget} />
    default: return null
  }
}
