export function SpeechBubbleIcon({ size = 16 }) {
  return (
    <svg viewBox="0 0 16 16" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 2h14a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H9l-3 3v-3H2a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1z" />
    </svg>
  )
}

export function LockIcon({ size = 16 }) {
  return (
    <svg viewBox="0 0 16 16" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="7" width="10" height="7" rx="1" />
      <path d="M5 7V5a3 3 0 0 1 6 0v2" />
      <circle cx="8" cy="11" r="0.5" fill="currentColor" />
    </svg>
  )
}
