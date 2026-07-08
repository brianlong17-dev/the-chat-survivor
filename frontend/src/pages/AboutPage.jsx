import MobileNav from '../components/MobileNav'

export default function AboutPage() {
  return (
    <div className="demos-page about-page">
      <MobileNav />
      <h1 className="lobby-title">About</h1>
      <p className="demos-subtitle">A reality TV–style elimination game played entirely by LLMs.</p>

      <div className="about-body">
        <p>
          The Chat Survivor drops a cast of AI characters into a reality
          competition. They talk, scheme, play mini-games, and vote each other
          out round by round until one is left standing.
        </p>
        <p>
          Each agent carries an evolving inner life — a persona, a speaking
          style, a shifting strategy, and lessons learned from earlier phases.
          As the game runs long, their memories are compressed so the drama can
          keep going without losing the thread.
        </p>
        <p>
          You can watch a game unfold on its own, or jump in and play as one of
          the characters, or as yourself. The Demos page has pre-loaded scenarios from
          real playthroughs — finales, tense split-or-steal endings, and full
          game rounds mid-competition.
        </p>
      </div>
    </div>
  )
}
