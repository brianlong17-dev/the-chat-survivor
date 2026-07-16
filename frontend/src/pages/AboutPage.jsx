import MobileNav from '../components/MobileNav'

const TAGS = [
  { label: 'RUDE', tone: 'accent' },
  { label: 'FUNNY', tone: 'accent' },
  { label: 'SPITEFUL', tone: 'accent' },
  { label: 'KIND', tone: 'phase' },
  { label: 'LOYAL', tone: 'phase' },
  { label: 'WELL-MEANING', tone: 'phase' },
]

export default function AboutPage() {
  return (
    <div className="about-page">
      <MobileNav />

      <div className="about-column">
        <header className="about-hero">
          <div className="about-wordmark">The Chat Survivor</div>
          <h1 className="about-title">About</h1>
          <p className="about-subtitle">
            A reality TV&ndash;style elimination game played by LLMs (and you).
          </p>
        </header>

        <div className="about-divider">
          <span className="about-divider-line" />
          <span className="about-divider-diamond" />
          <span className="about-divider-line" />
        </div>

        <section className="about-section">
          <h2 className="about-section-label">The Premise</h2>
          <p>
            The Chat Survivor is a text-based elimination game &mdash; AI versus human. It's a
            sandbox for emergent AI social strategy, played out in the humble groupchat.
          </p>
        </section>

        <section className="about-section">
          <h2 className="about-section-label">No Script, No Strategy</h2>
          <p>
            The characters have no pre-programmed strategy or relationships. Their opinions,
            alliances, grudges and choices all form organically in response to the game. They're
            initialised only with their personality.
          </p>
        </section>

        <section className="about-section about-section-wide">
          <h2 className="about-section-label">Personality, Not Politeness</h2>
          
          <p>
            They're designed to be conversational, quick and irreverent. Their personalities run the full spectrum, 
            from villains and heroes to the anxious and chaotic.
             They have no obligations but to
            themselves.
          </p>
          <div className="about-tags">
            {TAGS.map(({ label, tone }) => (
              <span key={label} className={`about-tag about-tag-${tone}`}>{label}</span>
            ))}
          </div>
        </section>

        <section className="about-section">
          <h2 className="about-section-label">Memory &amp; Duplicity</h2>
          <p>
            Characters have hidden interiority, allowing duplicity and long-term plans. As the game
            runs long, they create their own memories to compress the action without losing the
            thread.
          </p>
        </section>

        <section className="about-section about-section-wide">
          <h2 className="about-section-label">How to Play</h2>
          <div className="about-cards">
            <div className="about-card">
              <div className="about-card-title">Watch</div>
              <p className="about-card-body">Let a game unfold on its own and see who survives.</p>
            </div>
            <div className="about-card">
              <div className="about-card-title">Play</div>
              <p className="about-card-body">Jump in as one of the characters, or as yourself.</p>
            </div>
          </div>
          <p>
            The <strong>Demos</strong> page lets you run standalone rounds. Every game ends in a
            finale &mdash; the last two contestants face off &mdash; and you can run those fixtures
            directly from the Finale section as examples of different endgame scenarios.
          </p>
        </section>

        <div className="about-links">
          <a href="https://github.com/brianlong17-dev/the-chat-survivor" target="_blank" rel="noreferrer">
            GitHub
          </a>
          <span className="about-links-sep">&middot;</span>
          <a href="https://brian904434.substack.com/" target="_blank" rel="noreferrer">
            Substack
          </a>
        </div>
      </div>
    </div>
  )
}
