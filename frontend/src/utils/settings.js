export const MAX_INPUT_CHARS = 1500

export const SETTINGS_KEY = 'game_settings'

export const SETTINGS_DEFS = [
  { key: 'showPrivateThoughts', label: 'Show private thoughts', default: true },
  { key: 'autoRun', label: 'Auto-run', default: true },
  { key: 'animateText', label: 'Animate messages', default: true },
  { key: 'autoExpandThoughts', label: 'Auto-expand thoughts', default: false },
  { key: 'showPrivateChats', label: 'Show private conversations', default: true },
  { key: 'mobileOutputs', label: 'Mobile outputs', default: false },
]

export const DEFAULT_SETTINGS = Object.fromEntries(SETTINGS_DEFS.map(t => [t.key, t.default]))

export const VISIBLE_TOGGLE_KEYS = new Set([
  //'showPrivateThoughts',
  'autoRun', 
  'animateText', 
  'autoExpandThoughts', 
  //'showPrivateChats', 
  //'mobileOutputs'
])

export const LOBBY_STORAGE_KEY = 'lobby_state'

export const LOBBY_LEVEL_STEP = 1

export function presetLobbyLevel(levelId) {
  try {
    const prev = JSON.parse(localStorage.getItem(LOBBY_STORAGE_KEY) || '{}')
    localStorage.setItem(LOBBY_STORAGE_KEY, JSON.stringify({ ...prev, selectedLevel: levelId }))
  } catch { }
}

export function loadSettings() {
  try { return { ...DEFAULT_SETTINGS, ...JSON.parse(localStorage.getItem(SETTINGS_KEY)) } }
  catch { return DEFAULT_SETTINGS }
}

export function saveSettings(s) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(s))
}
