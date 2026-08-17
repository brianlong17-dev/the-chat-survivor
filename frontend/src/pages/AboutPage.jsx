import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import MobileNav from '../components/MobileNav'
import { RELEASE_NOTES } from '../data/releaseNotes'

const TAGS = ['RUDE', 'FUNNY', 'SPITEFUL', 'KIND', 'LOYAL', 'WELL-MEANING']

const SECTIONS = [
  {
    label: 'The premise',
    body: (
      <p className="about-prose">
        The Chat Survivor is a text-based elimination game &mdash; AI versus human. It's a
        sandbox for emergent AI social strategy, played out in the humble groupchat.
      </p>
    ),
  },
  {
    label: 'No script, no strategy',
    body: (
      <p className="about-prose">
        The characters have no pre-programmed strategy or relationships. Their opinions,
        alliances, grudges and choices all form organically in response to the game. They're
        initialised only with their personality.
      </p>
    ),
  },
  {
    label: 'Personality, not politeness',
    body: (
      <>
        <p className="about-prose">
          They're designed to be conversational, quick and irreverent. Their personalities run
          the full spectrum, from villains and heroes to the anxious and chaotic. They have no
          obligations but to themselves.
        </p>
        <div className="about-traits">
          {TAGS.map(label => (
            <span key={label} className="about-trait">{label}</span>
          ))}
        </div>
      </>
    ),
  },
  {
    label: 'Memory & duplicity',
    body: (
      <p className="about-prose">
        Characters have hidden interiority, allowing duplicity and long-term plans. As the game
        runs long, they create their own memories to compress the action without losing the
        thread.
      </p>
    ),
  },
  {
    label: 'How to play',
    body: (
      <>
        <div className="about-ruled-list">
          <div className="about-ruled-row">
            <div className="about-ruled-marker">01</div>
            <div className="about-ruled-main">
              <div className="about-ruled-title">Watch</div>
              <div className="about-ruled-body">Let a game unfold on its own and see who survives.</div>
            </div>
          </div>
          <div className="about-ruled-row">
            <div className="about-ruled-marker">02</div>
            <div className="about-ruled-main">
              <div className="about-ruled-title">Play</div>
              <div className="about-ruled-body">Jump in as one of the characters, or as yourself.</div>
            </div>
          </div>
        </div>
        <p className="about-prose">
          The <strong>Demos</strong> page lets you run standalone rounds. Every game ends in a
          finale &mdash; the last two contestants face off &mdash; and you can run those fixtures
          directly from the Finale section as examples of different endgame scenarios.
        </p>
      </>
    ),
  },
]

const TABS = [
  { id: 'about', label: 'about' },
  { id: 'releases', label: 'release notes' },
]

export default function AboutPage() {
  const navigate = useNavigate()
  const [tab, setTab] = useState('about')

  return (
    <div className="about-page">
      <MobileNav />

      <div className="about-column">
        <header className="about-hero">
          <h1 className="about-title">About<span className="about-cursor" aria-hidden="true" /></h1>
          <p className="about-subtitle">
            A reality TV&ndash;style elimination game played by LLMs (and you).
          </p>
        </header>

        <div className="about-tabs lobby-tabs">
          {TABS.map(({ id, label }) => (
            <button
              key={id}
              className={`tab-btn ${tab === id ? 'active' : ''}`}
              onClick={() => setTab(id)}
            >
              {label}
            </button>
          ))}
        </div>

        {tab === 'about' ? (
          <div className="about-sections">
            {SECTIONS.map(({ label, body }) => (
              <section key={label} className="about-section">
                <h2 className="about-section-label sc-label">{label}</h2>
                {body}
              </section>
            ))}
          </div>
        ) : (
          <div className="about-sections">
            {RELEASE_NOTES.map(({ id, date, intro, sections }) => (
              <div key={id} className="about-release">
                <section className="about-section">
                  <h2 className="about-section-label sc-label">{date}</h2>
                  <p className="about-prose">{intro}</p>
                </section>
                {sections.map(({ title, blurb, items }) => (
                  <section key={title} className="about-section">
                    <div className="about-release-title">{title}</div>
                    {blurb && <p className="about-prose">{blurb}</p>}
                    {items.length > 0 && (
                      <ul className="about-release-list">
                        {items.map(item => <li key={item}>{item}</li>)}
                      </ul>
                    )}
                  </section>
                ))}
              </div>
            ))}
          </div>
        )}

        <div className="about-footer">
          <div className="about-links">
            <a href="https://github.com/brianlong17-dev/the-chat-survivor" target="_blank" rel="noreferrer">
              GitHub
            </a>
            <span className="about-links-sep">&middot;</span>
            <a href="https://brian904434.substack.com/" target="_blank" rel="noreferrer">
              Substack
            </a>
          </div>
          <button className="about-cta" onClick={() => navigate('/')}>Enter the chat →</button>
        </div>
      </div>
    </div>
  )
}
