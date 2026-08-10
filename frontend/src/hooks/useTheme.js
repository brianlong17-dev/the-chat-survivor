import { useEffect, useState } from 'react'

const THEME_KEY = 'theme'

// Applied at module load so the attribute is present before React's first
// paint — otherwise the bare `:root` (dark) tokens flash in before the effect.
const initialTheme = localStorage.getItem(THEME_KEY) || 'light'
document.documentElement.setAttribute('data-theme', initialTheme)

// Global theme toggle. Currently only Lobby styles react to `data-theme`
// on <html> — other pages remain on the fixed dark tokens in index.css.
// Expand consumers by scoping their CSS to `[data-theme="light"] .your-class`.
export default function useTheme() {
  const [theme, setTheme] = useState(initialTheme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem(THEME_KEY, theme)
  }, [theme])

  const toggleTheme = () => setTheme(t => (t === 'light' ? 'dark' : 'light'))

  return [theme, toggleTheme]
}
