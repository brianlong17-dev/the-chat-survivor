import { useState, useRef, useEffect } from 'react'
import { MAX_INPUT_CHARS } from '../utils/settings'

const SENT_FLASH_MS = 900

const autoSize = (el) => {
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}

const fontScaleFor = (text) => {
  const n = (text ?? '').length
  if (n > 260) return 0.8
  if (n > 130) return 0.88
  return 1
}

const MicIcon = ({ listening }) => listening ? (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <rect x="2" y="2" width="10" height="10" fill="currentColor" />
  </svg>
) : (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <rect x="4.5" y="1" width="5" height="7" rx="2.5" stroke="currentColor" strokeWidth="1.2" />
    <path d="M2.5 7.5C2.5 10.0376 4.46243 12 7 12C9.53757 12 11.5 10.0376 11.5 7.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="square" />
    <line x1="7" y1="12" x2="7" y2="13.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="square" />
    <line x1="4.5" y1="13.5" x2="9.5" y2="13.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="square" />
  </svg>
)

export default function InputRequest({ request, onSubmitForm, playerNames = [], transcribe, transcriptionEnabled = true, awaitingNext = false, sendNext, skipAnimation, isAnimating = false, awaitingNextRound = false, sendNextRound }) {
  const [values, setValues] = useState({})
  const [pageIndex, setPageIndex] = useState(0)
  const [listening, setListening] = useState(false)
  const [transcribing, setTranscribing] = useState(false)
  const [sentFlash, setSentFlash] = useState(false)
  const [textRevealed, setTextRevealed] = useState(false)
  const recorderRef = useRef(null)
  const micTargetRef = useRef(null)
  const textRefs = useRef({})

  const form = request?.form ?? null
  const pages = form?.pages ?? []
  const page = pages[pageIndex] ?? null
  const isLastPage = pageIndex >= pages.length - 1
  const inactive = !request && !awaitingNext && !awaitingNextRound && !isAnimating

  useEffect(() => {
    setValues({})
    setPageIndex(0)
  }, [request])

  useEffect(() => {
    setTextRevealed(false)
  }, [request, pageIndex])

  useEffect(() => {
    Object.values(textRefs.current).forEach(autoSize)
  }, [values, pageIndex, request])

  const nameLimit = Math.max(14, ...playerNames.map(n => n.length))

  const choiceInputs = (page?.inputs ?? []).filter(i => i.is_multiple_choice)
  const textInputs = (page?.inputs ?? []).filter(i => !i.is_multiple_choice)
  const pageChoice = choiceInputs.length ? values[choiceInputs[0].id] : null
  const choicesComplete = choiceInputs.length > 0 && choiceInputs.every(i => values[i.id])
  const showText = !choiceInputs.length || textRevealed

  useEffect(() => {
    if (choicesComplete) setTextRevealed(true)
  }, [choicesComplete])

  const applyToken = (title) => (title ?? '').replace(/\{choice\}/g, pageChoice ?? '')

  const setValue = (id, value) => setValues(prev => ({ ...prev, [id]: value }))

  const canSend = (() => {
    if (!page) return false
    if (choiceInputs.length) return choiceInputs.every(i => values[i.id])
    return textInputs.every(i => (values[i.id] ?? '').trim())
  })()

  const advance = () => {
    if (!canSend) return
    if (!isLastPage) {
      setPageIndex(pageIndex + 1)
      return
    }
    const payload = {}
    for (const p of pages) {
      for (const i of p.inputs) payload[i.id] = values[i.id] ?? ''
    }
    setSentFlash(true)
    setTimeout(() => setSentFlash(false), SENT_FLASH_MS)
    onSubmitForm(payload)
  }

  const micTargetId = () => micTargetRef.current ?? textInputs[textInputs.length - 1]?.id ?? null

  const toggleMic = async () => {
    if (listening) {
      recorderRef.current?.stop()
      return
    }
    const targetId = micTargetId()
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const recorder = new MediaRecorder(stream)
    const chunks = []
    recorder.ondataavailable = e => chunks.push(e.data)
    recorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop())
      setListening(false)
      setTranscribing(true)
      const blob = new Blob(chunks, { type: recorder.mimeType })
      const text = await transcribe(blob, playerNames)
      if (text && targetId) {
        setValues(prev => ({ ...prev, [targetId]: prev[targetId] ? prev[targetId] + ' ' + text : text }))
      }
      setTranscribing(false)
    }
    recorderRef.current = recorder
    recorder.start()
    setListening(true)
  }

  const actionLabel = isAnimating ? 'Skip ›'
    : awaitingNextRound ? 'Next Round ›'
    : (awaitingNext && !request) ? 'Next ›'
    : sentFlash ? '✓ Sent'
    : (form && !isLastPage) ? 'Next ›'
    : 'Send'

  const actionHandler = isAnimating ? skipAnimation
    : awaitingNextRound ? sendNextRound
    : (awaitingNext && !request) ? sendNext
    : advance

  const actionDisabled = form && !isAnimating && !awaitingNextRound && !(awaitingNext && !request) && !canSend

  const overflowing = Object.values(values).some(v => typeof v === 'string' && v.length > MAX_INPUT_CHARS)

  const promptRow = (input, withActions = true) => {
    const key = input?.id ?? 'waiting'
    const text = input ? (values[input.id] ?? '') : ''
    return (
    <div className="turn-input-prompt-row" key={key}>
      <span className="turn-input-caret">&gt;</span>
      <textarea
        ref={el => { textRefs.current[key] = el; autoSize(el) }}
        className="turn-input-text"
        rows={1}
        style={{ '--tf-scale': fontScaleFor(text) }}
        value={text}
        onChange={e => {
          autoSize(e.target)
          if (input) setValue(input.id, e.target.value)
        }}
        onFocus={() => { if (input) micTargetRef.current = input.id }}
        onKeyDown={e => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            if (input) advance()
          }
        }}
        placeholder={input?.placeholder || (request ? 'Type your response...' : 'Waiting...')}
        autoFocus={!inactive && !awaitingNext}
        disabled={!request}
      />
      {withActions && (
        <button
          className={`mic-btn ${listening ? 'active' : ''} ${transcribing ? 'transcribing' : ''}`}
          onClick={toggleMic}
          disabled={!transcriptionEnabled}
          title="Voice input"
        >
          <MicIcon listening={listening} />
        </button>
      )}
      {withActions && (
        <button className="turn-input-send" onClick={actionHandler} disabled={actionDisabled}>
          {actionLabel}
        </button>
      )}
    </div>
    )
  }

  return (
    <div className={`turn-input ${inactive ? 'inactive' : ''} ${!request ? 'waiting' : ''}`}>
      <div className="turn-input-inner">

        {form && page && choiceInputs.map(input => {
          const chosen = values[input.id]
          const visible = chosen ? input.choices.filter(c => c === chosen) : input.choices
          const stacked = input.choices.some(c => c.length > nameLimit)
          return (
            <div className="turn-input-section" key={input.id}>
              {!chosen && <span className="turn-input-label">{applyToken(input.title)}</span>}
              <div className={`turn-input-tiles ${input.choices.length <= 3 ? 'compact' : ''} ${stacked ? 'stacked' : ''} ${chosen ? 'collapsed' : ''}`}>
                {visible.map(choice => {
                  const selected = chosen === choice
                  return (
                    <button
                      key={choice}
                      className={`turn-input-tile ${selected ? 'selected' : ''}`}
                      onClick={() => setValue(input.id, selected ? undefined : choice)}
                    >
                      <span className="turn-input-tile-marker">{selected ? '▸' : String(input.choices.indexOf(choice) + 1).padStart(2, '0')}</span>
                      <span>{choice}</span>
                    </button>
                  )
                })}
              </div>
            </div>
          )
        })}

        {form && page && showText && textInputs.map((input, index) => (
          <div className="turn-input-section" key={input.id}>
            <span className={`turn-input-label ${sentFlash ? 'sent' : ''}`}>
              {sentFlash ? '✓ Sent' : applyToken(input.title)}
            </span>
            {promptRow(input, index === textInputs.length - 1)}
            {index === textInputs.length - 1 && page.underline && (
              <span className="turn-input-hint">{page.underline}</span>
            )}
          </div>
        ))}

        {form && page && !textInputs.length && (
          <div className="turn-input-section">
            <div className="turn-input-prompt-row bare">
              <button className="turn-input-send" onClick={actionHandler} disabled={actionDisabled}>
                {actionLabel}
              </button>
            </div>
            {page.underline && <span className="turn-input-hint">{page.underline}</span>}
          </div>
        )}

        {!form && (
          <div className="turn-input-section">
            {sentFlash && <span className="turn-input-label sent">✓ Sent</span>}
            {promptRow(null)}
          </div>
        )}

        {overflowing && (
          <span className="turn-input-truncate-warn">over {MAX_INPUT_CHARS} characters — will be truncated</span>
        )}

        {form && pages.length > 1 && (
          <span className="turn-input-pager">{String(pageIndex + 1).padStart(2, '0')} / {String(pages.length).padStart(2, '0')}</span>
        )}

      </div>
    </div>
  )
}
