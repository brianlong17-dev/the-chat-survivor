export const RELEASE_NOTES = [
  {
    id: '2026-08-17',
    date: '17 August 2026',
    intro:
      "Everything below has landed since the last deploy on 30 July. Mostly UX — a lobby redesign, a tutorial mode, a smoother in-game feed, and player input rebuilt with intention.",
    sections: [
      {
        title: 'Play the game yourself',
        blurb:
          'The human turn used to be a stack of terminal-style questions, one field at a time. It’s now a proper form.',
        items: [
          'Questions written for the moment you’re in — "You’re at risk. Make your plea.", "You win! A final word to the fans?", "Say something to Gollum" — rather than a generic prompt.',
          'Placeholders that tell you what’s wanted: "your victory speech", "explain your vote or plead your case", "why should they spare you?"',
          'A note under each page telling you who’s listening — "everyone hears this", "your vote is revealed with your message", "you alone are sending them home".',
          'Multi-page turns: where a round asks you to make a choice and say something about it, the choice comes first, so you speak with the decision already made.',
        ],
      },
      {
        title: 'A tutorial game',
        blurb: 'A new two-player quickstart level built to teach the game.',
        items: [
          'The host walks you through it in gold tutorial messages only you can see.',
          'Mid-game the host nudges you toward the point of the thing — "can you use your next turn to influence your opponent’s decision?"',
          'At the end, a Next Level prompt drops you back to the lobby with the following game already selected.',
        ],
      },
      {
        title: 'Pick your models',
        blurb:
          'You can now choose which model each character runs on, per player, from the lobby. Gemini 2.5, 3.1 and 3.5 Flash Lite are available at launch.',
        items: [],
      },
      {
        title: 'Rounds have names now',
        blurb:
          'Every round announces itself with its type and title — Discussion Round, Game Round, Elimination Round, Finale — rather than just a number.',
        items: [],
      },
      {
        title: 'Players are typing…',
        blurb:
          'A live indicator shows who’s mid-turn — "Lady Macbeth is typing…", or "3 players are typing…" when several are thinking at once. The wait is no longer a blank screen.',
        items: [],
      },
      {
        title: 'End-of-phase commentary',
        blurb:
          'When a phase closes and the characters go away to write their memories, they leave a private line about how it went — a confessional booth for the parts of the game they aren’t saying out loud.',
        items: [
          'Again... no longer a dead screen while this work happens. It’s often quite funny, which is nice.' 
        ],
      },
      {
        title: 'The cast got better',
        blurb: 'An important rewrite of how characters are generated.',
        items: [
          'They want to win now — and specifically, to win in their own way. Generation asks why this particular person would want it and what winning looks like to them.',
          'This makes the game a bit more fun and challenging, without having characters devolve into terminators.',
          'Better contradictions. The old "hidden depth" instruction pushed every character toward a wound; it now asks for whatever’s truest — a private appetite, a vanity, a grudge they enjoy, a hypocrisy they can’t see.',
          'A vocal register is part of every profile, which holds characters’ voices apart from each other for longer.',
          'Characters are generated while the game screen loads, so you’re looking at the arena instead of a spinner.',
        ],
      },
      {
        title: 'The whole thing looks different',
        blurb: 'A full visual overhaul.',
        items: [
          'Starting on a new paper visual language',
          'The lobby has a splash page and walks you through the level selection, rather than everything landing at once',
          'About and Demos pages reworked.',
          'Settings trimmed to the toggles that matter: Auto-run, Animate messages, Auto-expand thoughts.',
        ],
      },
      {
        title: 'Under the hood',
        blurb: 'Not visible in play, but worth recording.',
        items: [
          'Every game now has an ID, carried through the logs, the API cost accounting and the start-of-game record.',
          'Per-turn tracing — each turn is timed and measured for token cost, attributed to the character and the model.',
          'New log-analysis tools for the MCP service, including diffing a character’s system prompt across a game to see how far they drifted.',
          'Round-by-round host summaries are switched off',
          'Character context reformatted for clarity — consistent headers, phase progress in the right place, cleaner round ledgers.',
        ],
      },
    ],
  },
]
