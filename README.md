# The Chat Survivor

A text-based social elimination game played by LLM agents. Every player competes in games for points, plots in private, and tries to survive the vote of their peers.

Play it live at **[thechatsurvivor.com](https://thechatsurvivor.com)**, or clone this repo and run your own characters with your own API key.

<a href="https://thechatsurvivor.com"><img src="docs/screenshots/logan_vs_q_vs_catherine.png" alt="The Chat Survivor — Logan vs Q vs Catherine" /></a>

---



## What it is

A competitive arena for AI game players where the strategy is social and the output is entertaining. We know AI can solve problems and win chess; character gameplay has a different goal — to entertain. For characters to be believable they need coherence: they have to understand the game and evolve with events.

How does a character make choices that are true to themselves? In this game, characters sometimes organically vote themselves out rather than betray a friend. We can also watch them internally plan to betray an ally while maintaining a perfect front.

This is a non-specific goal — AI models aren't trained to betray or to be loyal, or to optimise on a strategy. Creating the future of social and entertaining characters is a different scenario, not necessarily well understood by current training, where models are trying to be helpful and logical above all else.

Games start simple — Prisoner's Dilemma, give-or-steal — and get more complex: mob-mentality games, murder in the dark, sob stories, comedy roasts, and playing to win the votes of defeated players in the finale. Each character is generated at the start of the game, so the variations are endless.

## What the agents actually do

Agents are more than static Q&A bots. Each one has:

- **Evolving state** — persona, strategy, speaking style, and life lessons that update after every turn.
- **Memory compression** — at the end of each phase, agents summarise what happened into detailed and brief memories, preventing context from growing unboundedly across a long game.
- **Visibility-filtered context** — private conversations are only shown to the agents who were part of them.
- **A Game Master** — a separate LLM agent that summarises rounds and can select players by personality parameter (e.g. "most chaotic") for wildcard immunity.

See [ARCHITECTURE.md](ARCHITECTURE.md) for a full breakdown of how the components fit together.

---

## Run it locally

### 1. Clone and install

```bash
git clone https://github.com/<your-username>/the-chat-survivor.git
cd the-chat-survivor
uv sync
```

(If you don't have `uv`, install it: <https://docs.astral.sh/uv/getting-started/installation/>.)

### 2. Set up a Gemini API key

Easiest path: get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey), then create a `.env` file in the repo root:

```env
GEMINI_API_KEY=your-key-here
```

Vertex AI is also supported if you have a GCP project — set `PROJECT` and `LOCATION` instead.

### 3. Pick how you want to run it

**Console mode** — quickest way to see a game happen:

```bash
uv run main.py
```

**Web mode** — same game, with the React frontend:

```bash
# backend
uv run uvicorn web.server:app --reload

# frontend (in a separate terminal)
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Game design

A game runs on a `GameDesign` — a description of the phases, rounds, and round settings. Game designs can mix and match any of the round modules (games, discussions, votes). See `main.py` for an example of how to wire one up and run it from the console.

---

## Tech stack

- Python 3.12+
- [google-genai](https://pypi.org/project/google-genai/) — Gemini models
- [pydantic](https://docs.pydantic.dev/) — data validation and dynamic model generation
- [FastAPI](https://fastapi.tiangolo.com/) — web backend
- [React](https://react.dev/) + [Vite](https://vitejs.dev/) — frontend

---

## Output

The game runs in the terminal with coloured text separating public dialogue, private thoughts, host announcements, and system messages. Agent turns are optionally logged to JSONL files in `logs/` for debugging and analysis — use `read_log.py` to inspect them.
