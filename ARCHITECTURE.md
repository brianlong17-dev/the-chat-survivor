# Architecture

A social strategy game where LLM agents compete through discussion rounds, mini-games, and jury voting. Agents are initialised with a persona and speaking style, and evolve in response to the game- strategy, life lessons, and a relationship to each player. They compress their own game view into memory as the game runs long, so context stays affordable over dozens of rounds. See [README.md](README.md) for the premise and design motivation; this document covers the mechanisms.

The project is two things stacked together:

- **An agent design.** The [agents/](agents/) package defines a player whose personality and memory live as strings on the instance, and who rewrites those strings every turn through the structured-output schema.
- **A game framework.** The orchestration, round library, state model, and presentation layer that put a cast of these agents through a full elimination game and stream it to a viewer.

Three concerns cut across both — orchestration, round execution, and state/presentation — and the presentation layer is fully swappable: the terminal and the web client run the same engine, differing only at the output sink.

## Component map

| Layer | Path | Role |
|-------|------|------|
| Orchestration | [core/simulation_engine.py](core/simulation_engine.py) | Top-level loop, player setup, elimination |
| | [core/phase_runner.py](core/phase_runner.py) | Runs one phase: intro, rounds, summary, brevity jail |
| | [core/bootstrap.py](core/bootstrap.py) | Factory: wires agents, board, engine |
| | [core/levels/game_designs/](core/levels/game_designs/) | `GameDesign` base + concrete designs (progression logic) |
| | [core/levels/phase_description.py](core/levels/phase_description.py) | `PhaseDescription` — a phase blueprint |
| | [core/levels/level_registry.py](core/levels/level_registry.py) | `LevelDefinition`s the launcher / web frontend pick from |
| State & context | [core/gameboard.py](core/gameboard.py) | Central live state + broadcast surface |
| | [core/game_context/game_log.py](core/game_context/game_log.py) | Append-only message store, round summarisation |
| | [core/game_context/models.py](core/game_context/models.py) | `RoundBlock` / `MessageBlock` / `MessageEntry` |
| | [core/game_context/context_builder.py](core/game_context/context_builder.py) | Per-agent context, visibility filter, recency anchor |
| | [core/game_context/user_content.py](core/game_context/user_content.py) · [dashboard.py](core/game_context/dashboard.py) · [summaries_builder.py](core/game_context/summaries_builder.py) | The three pieces of a per-turn user message |
| Round execution | [gameplay_management/base_manager.py](gameplay_management/base_manager.py) | `BaseRound` abstract base + shared round helpers |
| | [gameplay_management/turn_manager.py](gameplay_management/turn_manager.py) | `TurnManager` — universal turn entry point |
| | [gameplay_management/](gameplay_management/) subpackages | discussion / games / game_perform / game_targeted / game_cycle / eliminations |
| Agents | [agents/abstract_agentic_player.py](agents/abstract_agentic_player.py) | `AbstractAgenticPlayer` — the pluggable agent contract |
| | [agents/agentic_player_v2/agentic_player.py](agents/agentic_player_v2/agentic_player.py) | `AgenticPlayer` — the current player implementation |
| | [agents/game_host/game_host.py](agents/game_host/game_host.py) | `GameMaster` ("Host") — summariser / selector / narrator |
| | [agents/human_player.py](agents/human_player.py) | `Human` — sink-driven interactive player |
| | [agents/agentic_player_v2/system_prompt.py](agents/agentic_player_v2/system_prompt.py) | `SystemPrompt` — renders an agent's identity prompt |
| | [agents/player_response_models.py](agents/player_response_models.py) | `AgentResponseModelFactory` — per-turn schema assembly |
| | [agents/character_generation/](agents/character_generation/) | `CharacterGenerator` — threaded persona generation |
| Infrastructure | [core/api_client/](core/api_client/) | Gemini wrapper, model tiers, token budget, usage records |
| | [core/sinks/](core/sinks/) | `GameEventSink` + console / websocket implementations |
| | [web/](web/) | FastAPI app: REST + game / demo / replay WebSockets |
| | [demo_runner/](demo_runner/) | Fixture-driven demos and saved-tape replay |
| | [frontend/](frontend/) | React/Vite SPA consuming the event stream |

---

# Part 1 — The agent

Everything an `AgenticPlayer` "is" lives as plain attributes on the instance, seeded at character generation and then rewritten by the agent itself as the game unfolds:

- **Persona** — a core `initial_persona` (immutable anchor), plus `additional_persona_coloring` and a `persona_unique_detail` the agent can add to over time.
- **Speaking style** — a core `initial_speaking_style` plus an evolving `speaking_style_update`, kept separate so the voice can drift and then be pulled back toward the original.
- **Strategy** — `game_strategy` (long-game plan) and `character_strategy` (the edge their persona gives them).
- **Life lessons** — a capped queue of learnings that shape future decisions.
- **Impressions** — a `character_dictionary` of per-opponent notes, one entry per other live player. As players are eliminated the entries are pruned, so agents keep durable, private, per-rival memory — the substrate for grudges and alliances.
- **Memory** — detailed and brief phase summaries, written by the agent at each phase boundary.

None of these are set once and snapshotted. They are the **evolution fields** of the turn schema (below), so the agent's self-description changes in lockstep with the game.

## The pluggable agent contract

[`AbstractAgenticPlayer`](agents/abstract_agentic_player.py) defines the contract every player implementation must satisfy — a constructor signature, `take_turn_standard`, `summarise_phase`, `phase_summaries_string`, and three field-set hooks (`chain_of_thought_fields`, `logic_fields`, `evolution_fields`). `take_turn_standard` is implemented once on the abstract base: it renders the user content, calls the model, and hands the response to the subclass's `_process_standard_turn_response`. Multiple implementations exist behind the contract and a single game can mix them; the rest of the framework never depends on which one it's talking to.

## The turn model: three field families

Every turn's response schema is built fresh from the agent's three hooks, in a deliberate order (assembled by [`AgentResponseModelFactory`](agents/player_response_models.py)):

1. **Chain-of-thought fields** (before the answer) — grounding and reasoning: `who_are_you`, a `hallucination_catcher` ("did another player lie or hallucinate last round?"), a `bandwagon` check, and inner/outer mood. These steer the response without being spoken.
2. **`private_thoughts` + `private_thoughts_brief`**, then the game's **action fields** (e.g. a `Literal["split","steal"]`), then the **`public_response`**.
3. **Evolution fields** (after the answer) — the self-updates: strategy, life lessons, persona colour, speaking style, and the per-opponent `impression_*` fields.

After the call, `process_evolution_fields` writes each populated field back onto the instance (queue-typed fields append and de-duplicate; string fields overwrite), and `process_character_impressions` syncs the impression dictionary against the current roster. `private_thoughts_brief` is retained as the agent's most recent internal thought and threaded back into their next context.

This is schema-as-prompt: the Pydantic field descriptions *are* the per-turn instruction set. The agent's choice space, its introspection prompts, and its self-updates travel together in one structured object passed to Gemini's native `response_schema` — the model never sees freeform JSON. Adding a game type is a function that returns extra action fields, not a new prompt template.

## Agent turn flow

```
ContextBuilder / SystemPrompt / UserContent
    → what does this agent see, who are they, what are they asked to do

AgentResponseModelFactory.create_model_(agent, action_fields, …)
    → fresh Pydantic schema:
        chain-of-thought fields
        private_thoughts (+ brief)
        action fields  ·  public_response
        evolution fields  ·  impression_<name> fields

APIClient.create(response_schema, messages)
    → Gemini call; structured object returned (budget-checked, usage-recorded)

agent.process_evolution_fields / process_character_impressions
    → strategy, life_lessons, persona, speaking style, impressions updated in place

GameBoard.handle_public_private_output(agent, response, …)
    → public_response appended to GameLog (visible to others)
    → private_thoughts emitted to the sink (viewer only)
    → last_message_id updated so the next turn's recency anchor points here
```

## The other agents

**`GameMaster`** ([agents/game_host/game_host.py](agents/game_host/game_host.py)) — a special agent with display name "Host". It compresses each finished round into a rolling queue of summaries, selects players parametrically (single-agent picks and question-driven group picks), compresses long cycle-game text, and generates host narration.

**`Human`** ([agents/human_player.py](agents/human_player.py)) — subclasses `AgenticPlayer` and overrides `get_response` to collect input through the sink instead of the LLM. It reads the same per-turn Pydantic schema and prompts field-by-field (multiple-choice fields become pickers), validates, and re-prompts on error. Input is sanitised to stop humans spoofing system messages; the evolution/summary passes are no-ops. Because I/O goes through the sink, the same class works identically in the terminal and the browser — the sink decides how a prompt is rendered and how the answer is gathered.

**`CharacterGenerator`** ([agents/character_generation/](agents/character_generation/)) — generates a cast in parallel from a name list, prompting the higher model tier for a rich first-person profile and instantiating an agent class per character.

## Mask drop

An agent's `game_over` (or an explicit `_mask_drop`) flips `SystemPrompt` into a "the game is over, drop any pretense or false persona" mode. Elimination and the finale use it to get the agent's real voice for final words and victory speeches, distinct from the strategic mask they wore while playing.

---

# Part 2 — The framework

## Orchestration

**`SimulationEngine`** ([core/simulation_engine.py](core/simulation_engine.py)) holds the agents, board, `GameMaster`, generator, game config, and phase runner. `run()` initialises the board and loops: while more than one player remains, it asks the `GameDesign` for the next `PhaseDescription` and hands it to the `PhaseRunner`. It also owns elimination — flipping `game_over`, moving the agent to `dead_agents`, and clearing its scoreboard state.

**`PhaseRunner`** ([core/phase_runner.py](core/phase_runner.py)) runs one phase: applies the phase's `config_mutations`, opens the phase, then for each round opens a `RoundBlock`, dispatches to `run_game()` / `run_vote()`, requests a Host round summary, and imposes brevity jail. When the phase closes, it summarises phase memory for every agent in parallel. Between rounds it can hold on a **round gate** so a web viewer advances at their own pace.

**Brevity jail** — at the end of each round the runner averages message length per agent and flags the wordiest fraction of the cast. The flag makes `SystemPrompt` append a "reactions over statements, shortness can be powerful" nudge to their next turn, then resets and re-elects from scratch. A static "be brief" instruction gets ignored; a *relative* "you're currently the wordiest" one moves behaviour because it's grounded in observable difference.

**`GameDesign`** ([core/levels/game_designs/game_design.py](core/levels/game_designs/game_design.py)) is the abstract base for progression. Concrete designs implement `get_phase_description(phase_number, agent_count, cfg)` and decide *which* rounds and votes run in *which* phase — progression logic kept entirely separate from execution. A `make_phase` helper assembles the common "discussion → game → discussion → vote" shape.

**`PhaseDescription`** ([core/levels/phase_description.py](core/levels/phase_description.py)) is a pure blueprint: ordered round classes, `config_mutations`, and a `should_summarise_phase` flag. No execution logic.

**Levels** ([core/levels/level_registry.py](core/levels/level_registry.py)) — each playable level is a [`LevelDefinition`](core/levels/level_definition.py) dataclass (id, name, description, token budget, game design, locked flag), consumed by the launcher and the web frontend. Player range is derived from the game design.

**`GameConfig`** ([core/game_config.py](core/game_config.py)) is a plain data holder for tunable rules. Behaviour and strings stay in the round classes; only values live here.

### Phase flow

```
game_design.get_phase_description(phase_number, agent_count, cfg)
    → PhaseDescription (round classes + config_mutations)

PhaseRunner.run_phase(phase_description)
    → apply config_mutations
    → gameBoard.new_phase()
    → for each round_class:
        (round gate — wait for viewer on web)
        gameBoard.newRound()                # opens a RoundBlock
        introduce phase / game on first round
        run_vote() OR run_game()
        game_master.summariseRound()        # compresses the round to text
        gameBoard.endRound()                # commits the RoundBlock
        _impose_brevity_jail()              # re-elect the wordiest for next round
    → if should_summarise_phase:
        every agent writes phase memory in parallel
    → reset discussion settings, endPhase()
```

## Round execution

**`BaseRound`** ([gameplay_management/base_manager.py](gameplay_management/base_manager.py)) — every round type is a subclass, one per file in a topical subpackage. `PhaseRunner` instantiates the class fresh per round and calls `run_game()` or `run_vote()`. `BaseRound` carries the cross-cutting helpers rounds reuse (player selection, host broadcasting, parallel task execution, private host conversations, elimination sequences, sidebar widgets); families of rounds share behaviour through intermediate bases — `DiscussionBaseRound`, `VotingRoundBase`, `BaseTargetedGame` — and scoring helpers come from `GameMechanicsMixin`. Round files are intentionally script-shaped: each method is a beat in the round's story, with the run method as the orchestrator.

| Subpackage | Round family |
|------------|--------------|
| [discussion_rounds/](gameplay_management/discussion_rounds/) | Free / directed / short discussion, interviews — driven by data-shaped `DiscussionRoundSettings` |
| [games/](gameplay_management/games/) | Head-to-head and group mini-games (Prisoner's Dilemma, RPS, …) |
| [game_perform/](gameplay_management/game_perform/) | Perform-and-be-scored: peers rate a performance, the average becomes points |
| [game_targeted/](gameplay_management/game_targeted/) | Agent-to-agent point transfers (give / steal / sacrifice) |
| [game_cycle/](gameplay_management/game_cycle/) | Long multi-cycle games with optional per-cycle context compression |
| [eliminations/](gameplay_management/eliminations/) | Vote formats on `VotingRoundBase`, plus the finale reunion and jury vote |

**`TurnManager`** ([gameplay_management/turn_manager.py](gameplay_management/turn_manager.py)), owned by each `BaseRound`, is the universal turn entry point: `take_turn(...)` builds the response model, calls the agent, and (optionally) broadcasts. On top of that it provides **targeted turns** (a name-choice `Literal` constrained to live players, so agents can address or act on a specific opponent), **choice reveals** (surfacing a hidden action like `*STEAL*` into the public feed around the spoken line), and the **optional-response buffer**: on optional turns an agent accrues a fractional speaking credit whether it speaks or not, and speaking costs a full unit. Silence becomes a resource an agent saves rather than a gap every agent fills.

## State and context

**`GameBoard`** ([core/gameboard.py](core/gameboard.py)) is the central live state and the single broadcast surface. It owns agent scores, phase/round counters, the `ContextBuilder`, and the `GameLog`. Game logic never touches the sink or the log directly — it calls the board's broadcast and scoring methods, and the board both appends to the log and fires the matching sink event.

**`GameLog`** ([core/game_context/game_log.py](core/game_context/game_log.py)) is an append-only store — nothing is ever deleted. Its data model is three levels deep ([models.py](core/game_context/models.py)):

```
RoundBlock                       # one round
  phase_number, round_number
  conversation_entries: [MessageBlock]
  game_ledger: str               # terse mechanics-emitted facts

MessageBlock                     # usually one message; a private convo is several
  message_entries: [MessageEntry]
  id: int                        # monotonic; drives "messages since" queries
  visibility_restriction: set[str] | None   # None = public
  closed: bool                   # private conversations can be reopened

MessageEntry                     # the atom
  speaker, public_output
  private_thought_brief          # the speaker's own aside, shown back only to them
```

`visibility_restriction` on the `MessageBlock` is the single mechanism behind every private-message behaviour — public broadcasts, two-player negotiations, private host chats, and system-only notes are all the same field.

Each `RoundBlock` also carries a **game ledger** — a terse, mechanics-authored record of what happened ("Alice stole from Bob."). When older rounds are re-rendered into an agent's context, the transcript is dropped and the ledger stands in. The ledger deliberately omits point counts: agents start doing arithmetic the moment they see numbers, which pulls them off the social/narrative game.

**Building each agent's view** — three collaborators answer three different questions, and stay independently swappable:

- [`SystemPrompt`](agents/agentic_player_v2/system_prompt.py) — *who is this agent?* Persona, speaking style, life lessons, impressions, current strategy, plus the brevity-jail and mask-drop nudges when active.
- [`ContextBuilder`](core/game_context/context_builder.py) — *what does this agent see?* Scores with a status line, the current-round transcript filtered by visibility, and previous rounds — recent ones in full, older ones collapsed to their ledger. It also injects the **recency anchor**: it finds the agent's own most-recent public message and marks it — either "this was your last turn, react to what's happened since" or, if nothing has happened since, "it's already been said; your turn now is a fresh action, not a reaction." Without it, agents parrot themselves or treat their own past words as fresh news. Private conversations are exempt — the frame there is already tight.
- [`UserContent`](core/game_context/user_content.py) with [`Dashboard`](core/game_context/dashboard.py) and [`SummariesStringBuilder`](core/game_context/summaries_builder.py) — *what is this agent being asked to do now?* Assembles the dashboard, phase summaries, round history, and turn instruction into the final user message.

## Infrastructure

**API client** ([core/api_client/](core/api_client/)) — a thin wrapper over `google.genai` with three model tiers: a default, a cheaper tier, and a higher tier for character generation and phase summaries. Structured outputs go through Gemini's native `response_schema`; the client retries rate limits, transient errors, and malformed JSON with backoff. Every game is created with a token budget, hard-capped by environment variable, and the client raises `BudgetExceeded` the moment recorded usage crosses it; a mock mode fabricates schema-shaped responses with no network call, making cost bounded and replay/tests free. A thread-safe [`APIRecordManager`](core/api_client/api_record_manager.py) records every call to a JSONL log and prints a per-caller usage summary at game end.

**Output sinks** ([core/sinks/](core/sinks/)) — the CLI and every web surface share the exact same engine; only the sink differs. [`GameEventSink`](core/sinks/game_sink.py) is the output contract: game logic only knows this interface, and everything visual is downstream. Beyond speech/thought/score events it carries lifecycle markers, sidebar widget updates, segment titles, loading states, and the human-input methods — the same indirection that lets the renderer be swapped is reused for input. Implementations: [`ConsoleGameEventSink`](core/sinks/console_sink.py) (coloured, animated terminal renderer), [`WebSocketSink`](core/sinks/websocket_sink.py) (serialises each event to JSON and streams it to the browser, adding the round gate, an input queue with inactivity timeouts, a mobile-output flag, and per-game JSONL recording that doubles as the replay tape), and silent / capturing sinks for tests.

**Web** ([web/server.py](web/server.py)) — a FastAPI app mounting REST endpoints and three WebSocket routers, each running a game on its own thread wired to a `WebSocketSink`: [`/ws/game`](web/ws_game.py) (a fresh game from a chosen level and cast, optionally with a human), [`/ws/demo`](web/ws_demo.py) (a fixture-backed demo module), and [`/ws/replay`](web/ws_replay.py) (a saved tape fired back through the socket with no LLM calls). Around them: Cloudflare Turnstile verification, per-IP daily and concurrency limits plus a token cap backed by SQLite ([rate_limits.py](web/rate_limits.py)), input sanitisation, non-blocking audio transcription, and structured game-start logging.

**Demos, fixtures, and replay** ([demo_runner/](demo_runner/)) — a **fixture** is a JSON capture of a cast mid-game (personas, styles, lessons, impressions, summaries, scores, elimination order), generated from real game logs. The demo runner rebuilds the engine with blank agents, applies the saved state, and runs a single round or finale against that cast — so a viewer can drop straight into a reunion finale with fully-formed characters, including taking over a finalist as the human and inheriting that finalist's memory. Live games can also be recorded and re-streamed byte-for-byte through `/ws/replay`.

---

# Memory & context

Memory narrows from raw to distilled as the horizon widens — this is what keeps a long game affordable:

- **Raw log** — every message lands in `GameLog` and is never deleted. The current round accumulates in full.
- **Per-round ledger** — the terse, numbers-free record of mechanical facts that stands in for the transcript once a round is no longer recent.
- **Per-agent phase summaries** — at each phase boundary every agent writes a detailed and a brief summary; only the most recent phases keep their detailed form, earlier ones collapse to brief.
- **Live state** — persona, strategy, speaking style, life lessons, and impressions, rewritten every turn through the evolution fields.

The compression is done *by the agent*, not to it. At each phase boundary the agent runs a **summary turn** (`summarise_phase`) on the higher model tier, writing both summaries from its own perspective. The summary turn doubles as a clean-up pass: the evolution fields switch into compression mode, so the agent rewrites its `speaking_style_update` back toward the original voice (stripping tics and catchphrases it has fallen into) and folds accumulated persona colour into its `persona_unique_detail`. When the life-lesson queue nears its cap, a compression field is injected and the agent merges its accumulated lessons into a small distilled set that replaces the queue — a fixed FIFO loses lessons that mattered, unbounded accumulation grows forever, and compression through the agent lets the character decide what's worth keeping. Those compression decisions are themselves part of how the character evolves.