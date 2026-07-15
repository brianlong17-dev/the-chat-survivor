# Architecture

A reality-TV-style elimination game where LLM agents compete through discussion rounds, mini-games, and jury voting. Agents carry evolving state — persona, speaking style, strategy, life lessons, and per-opponent impressions — and compress their own memory as the game runs long, so context stays affordable over dozens of rounds. The same engine drives a terminal renderer and a live web client; only the output sink changes. See [README.md](README.md) for the premise and design motivation; this document covers the mechanisms.

The project is really two things stacked together:

- **An agent design.** A small amount of code (the [agents/](agents/) package) defines a player whose whole personality and memory live as strings on the instance, and who rewrites those strings every turn through the structured-output schema. Most of the rest of the codebase exists in service of making that agent behave well and stay watchable over a long game.
- **A game framework.** The orchestration, round library, state model, and dual-surface presentation layer that put a cast of these agents through a full elimination game and stream it to a viewer.

Three architectural layers cut across both:

1. **Orchestration** — a `SimulationEngine` runs phases (`PhaseRunner`) according to a `GameDesign` that emits `PhaseDescription` blueprints.
2. **Round execution** — one `BaseRound` subclass per round/game type owns the moment-to-moment turn flow through a shared `TurnManager`. Agents (`AgenticPlayer`, `GameMaster`, `Human`) produce structured responses assembled per turn by `AgentResponseModelFactory`.
3. **State & presentation** — a single `GameBoard` holds live state and fires every change into a swappable `GameEventSink`. Terminal vs. web is decided at the sink layer, never in game logic.

---

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
| | [gameplay_management/](gameplay_management/) subpackages | discussion / games / game_perform / game_targeted / game_cycle / eliminations / immunities |
| Agents | [agents/abstract_agentic_player.py](agents/abstract_agentic_player.py) | `AbstractAgenticPlayer` — the pluggable agent contract |
| | [agents/agentic_player.py](agents/agentic_player.py) | `AgenticPlayer` — the current player implementation |
| | [agents/agentic_player_v1/](agents/agentic_player_v1/) | `AgenticPlayerV1` — an alternate implementation of the same contract |
| | [agents/game_host.py](agents/game_host.py) | `GameMaster` ("Host") — summariser / selector / narrator |
| | [agents/human_player.py](agents/human_player.py) | `Human` — sink-driven interactive player |
| | [agents/system_prompt.py](agents/system_prompt.py) | `SystemPrompt` — renders an agent's identity prompt |
| | [agents/player_response_models.py](agents/player_response_models.py) | `AgentResponseModelFactory` — per-turn schema assembly |
| | [agents/character_generation/](agents/character_generation/) | `CharacterGenerator` — threaded persona generation |
| Infrastructure | [core/api_client/](core/api_client/) | Gemini wrapper, model tiers, token budget, usage records |
| | [core/sinks/](core/sinks/) | `GameEventSink` + console / websocket implementations |
| | [web/](web/) | FastAPI app: REST + game / demo / replay WebSockets |
| | [demo_runner/](demo_runner/) | Fixture-driven demos and saved-tape replay |
| | [frontend/](frontend/) | React/Vite SPA consuming the event stream |

---

## The agent

The player is the centre of the project. Everything an `AgenticPlayer` "is" lives as plain attributes on the instance, seeded at character generation and then rewritten by the agent itself as the game unfolds:

- **Persona** — a core `initial_persona` (immutable anchor), plus `additional_persona_coloring` and a `persona_unique_detail` the agent can add to over time.
- **Speaking style** — a core `initial_speaking_style` plus an evolving `speaking_style_update`, kept separate so the voice can drift and then be pulled back toward the original.
- **Strategy** — `game_strategy` (long-game plan) and `character_strategy` (the edge their persona gives them).
- **Life lessons** — a `deque(maxlen=8)` of learnings that shape future decisions.
- **Impressions** — a `character_dictionary` of per-opponent notes, one entry per other live player.
- **Memory** — `phase_summaries_detailed` / `phase_summaries_brief`, written by the agent at each phase boundary.

None of these are set once and snapshotted. They are the **evolution fields** of the turn schema (see below), so the agent's self-description changes in lockstep with the game rather than at intervals.

### The pluggable agent contract

[`AbstractAgenticPlayer`](agents/abstract_agentic_player.py) defines the contract every player implementation must satisfy — a constructor signature, `take_turn_standard`, `summarise_phase`, `phase_summaries_string`, and the three field-set hooks (`chain_of_thought_fields`, `logic_fields`, `evolution_fields`). `take_turn_standard` itself is implemented once on the abstract base: it renders the user content, calls the model, and hands the response to the subclass's `_process_standard_turn_response`.

Two implementations satisfy that contract today — the current [`AgenticPlayer`](agents/agentic_player.py) and an earlier [`AgenticPlayerV1`](agents/agentic_player_v1/agent_player_v1.py) (which keeps a `position_assessment` / `round_specific_strategy` / `persona_additions` model). `CharacterGenerator` can be handed a list of agent classes and assigns one at random per character, so a single game can mix implementations. The point is architectural: **the agent is developed as a swappable unit behind a stable interface**, and the rest of the framework never depends on which one it's talking to.

### The turn model: three field families

Every turn's response schema is built from three hooks on the agent, in a deliberate order (assembled by [`AgentResponseModelFactory.create_model_`](agents/player_response_models.py)):

1. **Chain-of-thought fields** (before the answer) — grounding and reasoning: `who_are_you`, a `hallucination_catcher` ("did another player lie or hallucinate last round?"), a `bandwagon` check, and inner/outer `feeling` / `outer_mood`. These steer the response without being spoken.
2. **`private_thoughts` + `private_thoughts_brief`**, then the game's **action fields** (a `Literal["split","steal"]`, a name choice, a 1–10 score…), then the **`public_response`**.
3. **Evolution fields** (after the answer) — the self-updates: `game_strategy`, `life_lessons`, `additional_persona_coloring`, `character_strategy`, `speaking_style_update`, and the per-opponent `impression_*` fields.

After the call, [`process_evolution_fields`](agents/agentic_player.py) writes each populated field back onto the instance (queue-typed fields like `life_lessons` append and de-duplicate; string fields overwrite), and [`process_character_impressions`](agents/agentic_player.py) syncs the impression dictionary against the current roster. `private_thoughts_brief` is retained as the agent's `most_recent_internal_thought` and threaded back into their next context.

This is **schema-as-prompt**: the Pydantic field descriptions *are* the per-turn instruction set. The agent's choice space and its introspection prompts ride together in one structured object, and the LLM never sees freeform JSON — Gemini's native `response_schema` enforces the shape. Adding a game type is a function that returns extra action fields, not a new prompt template.

### Memory that compresses through the agent

At each phase boundary the agent runs a **summary turn** (`summarise_phase`) on the higher-quality model, writing a detailed and a brief summary of the phase from its own perspective. The summary turn doubles as a **clean-up pass**: the same evolution fields switch into compression mode (`currently_summarising` is set), so the agent rewrites its `speaking_style_update` back toward the original voice (stripping tics and catchphrases it has fallen into) and folds accumulated persona colour into its `persona_unique_detail`. When `life_lessons` reaches five, an extra `compressed_life_lessons` field (exactly three items) is injected and the deque is replaced with the distilled set. Memory is compressed *by the agent*, and those compression decisions are themselves part of how the character evolves.

---

## State and context

### `GameBoard`

[`GameBoard`](core/gameboard.py) is the central live state and the single broadcast surface. It owns agent scores, phase/round counters, the `ContextBuilder`, and the `GameLog`. Game logic never touches the sink or the log directly — it calls `host_broadcast`, `broadcast_public_action_agent`, `system_broadcast`, `append_agent_points`, etc., and the board both appends to the log and fires the matching sink event. Scores are floored at zero; `RESERVED_NAMES` (`SYSTEM`, `SYS_ADMIN`, `HOST`) are protected from collisions and excluded from player-only logic.

### `GameLog` and the message model

[`GameLog`](core/game_context/game_log.py) is an append-only store — nothing is ever deleted. Its data model is three levels deep, which is what makes private conversations and per-round compression fall out of one structure ([models.py](core/game_context/models.py)):

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

`visibility_restriction` on the `MessageBlock` is the **single** mechanism behind every private-message behaviour — public broadcasts, two-player negotiations, private host chats, and `SYS_ADMIN`-only system notes are all the same field. One decision point, no parallel ACL system.

The log also holds an optional **current-round summarisation** (`push_current_round_summarisation`): long "cycle" games can replace the older part of the in-progress round with a Host-authored summary while keeping recent messages verbatim.

### Building each agent's view

Three collaborators answer three different questions, and stay independently swappable:

- [`SystemPrompt`](agents/system_prompt.py) — *who is this agent?* Persona, speaking style, life lessons, character impressions, current strategy, plus the brevity-jail and mask-drop nudges when active.
- [`ContextBuilder`](core/game_context/context_builder.py) — *what does this agent see?* Scores with a status line ("you are N behind the leader"), the current-round transcript filtered by visibility, and previous rounds — recent ones in full, older ones collapsed to their ledger. It also injects the **recency anchor** (below).
- [`UserContent`](core/game_context/user_content.py) with [`Dashboard`](core/game_context/dashboard.py) and [`SummariesStringBuilder`](core/game_context/summaries_builder.py) — *what is this agent being asked to do now?* Assembles the dashboard, phase summaries, round history, and turn instruction into the final user message.

---

## Round execution

### `BaseRound`

Every round type is a [`BaseRound`](gameplay_management/base_manager.py) subclass, one per file in a topical subpackage. `PhaseRunner` instantiates the class fresh per round and calls `run_game()` or `run_vote()`. Long round files (`game_mob.py`, `game_pd_finale.py`, `reunion_round.py`) are intentionally script-shaped — each method is a beat in the round's story, with the run method at the bottom as the orchestrator.

`BaseRound` carries the cross-cutting helpers every round reuses: player lookup and shuffling, score-ranked player selection (`get_strategic_players`), host broadcasting, parallel task execution (`_run_tasks`), private host conversations (`_host_back_and_forth`, `_initialise_private_host_conversation`), the mask-drop elimination sequence (`eliminate_player_by_name`), and the sidebar **voting widget** helpers. Shared mechanics still come from mixins — `GameMechanicsMixin`, `VoteMechanicsMixin`, `ImmunityMechanicsMixin`.

### `TurnManager`

[`TurnManager`](gameplay_management/turn_manager.py), owned by each `BaseRound`, is the universal turn entry point. `take_turn(...)` builds the response model, calls the agent, and (optionally) broadcasts. On top of that it provides:

- **Targeted / directed turns** — inject a name-choice `Literal` constrained to live players, so agents can address or act on a specific opponent.
- **Choice reveals** — `pre_/post_message_choice_reveal` surfaces a hidden action (e.g. `*STEAL*`) into the public feed around the spoken line.
- **The optional-response buffer** (`take_turn_optional`) — on optional turns an agent accrues a fractional speaking credit (0.6 by default, configurable per game) whether it speaks or not; speaking costs a full unit. This makes silence a real strategic choice and stops every agent from chiming in on every beat.

### The round library

| Subpackage | Rounds |
|------------|--------|
| [discussion_rounds/](gameplay_management/discussion_rounds/) | Discussion (free / directed / short), interview, introduction — driven by data-shaped `DiscussionRoundSettings` (per-loop host messages and prompts) |
| [games/](gameplay_management/games/) | Prisoner's Dilemma (+ finale variant), Rock-Paper-Scissors, Guess-the-Number, Wisdom |
| [game_perform/](gameplay_management/game_perform/) | Perform-and-be-scored: peers rate a sob story / comedy roast 1–10, the average becomes points |
| [game_targeted/](gameplay_management/game_targeted/) | Agent-to-agent point transfers: give, steal, sacrifice, give-or-take |
| [game_cycle/](gameplay_management/game_cycle/) | Long-running multi-cycle games: The Circle, Knives, Mob — with optional per-cycle context compression |
| [eliminations/](gameplay_management/eliminations/) | Votes: bottom-two, each-player, elect-leader, lowest-points, winner-chooses, and the finale `FinaleReunionRound` |
| [immunities/](gameplay_management/immunities/) | Highest-points and wildcard immunity, resolved before a vote |

A representative example: **Prisoner's Dilemma** ([game_prisoners_dilemma.py](gameplay_management/games/game_prisoners_dilemma.py)) supports four pairing methods (random, lowest-picks-first, everyone-vs-everyone, or self-chosen partners), runs each pair's split/steal choice in parallel through a `ThreadPoolExecutor`, reveals the choices into the feed, awards points, drives a live sidebar widget, and appends a numbers-free line to the round ledger. The **finale reunion** ([reunion_round.py](gameplay_management/eliminations/reunion_round.py)) is the largest: eliminated players "wake up", are interviewed privately by the Host, confront the finalists in a Q&A the Host stages from those private conversations, then cast a jury vote (with a runner-up tiebreak) to crown the winner.

---

## Agents in detail

**`AgenticPlayer`** ([agents/agentic_player.py](agents/agentic_player.py)) — the main player described above.

**`GameMaster`** ([agents/game_host.py](agents/game_host.py)) — a special agent with display name "Host". It compresses each finished round into a rolling `deque(maxlen=50)` of summaries, selects players parametrically (`choose_agent_based_on_parameter` for wildcard immunity, `select_players` for question-driven group picks), compresses long cycle-game text, and generates host narration via `create_host_script` (with optional chain-of-thought fields for tricky segments like finale intros).

**`Human`** ([agents/human_player.py](agents/human_player.py)) — subclasses `AgenticPlayer` and overrides `get_response` to collect input through the sink instead of the LLM. It reads the same per-turn Pydantic schema and prompts field-by-field (multiple-choice fields become pickers), validates the result, and re-prompts on error. Input is sanitised to stop humans spoofing system messages, and the evolution/summary passes are no-ops. Because I/O goes through the sink, one `Human` class works identically in the terminal (`ConsoleGameEventSink` reads stdin) and the browser (`WebSocketSink` round-trips to the client).

**`CharacterGenerator`** ([agents/character_generation/characterGeneration.py](agents/character_generation/characterGeneration.py)) — generates a cast in parallel (`ThreadPoolExecutor`) from a name list, prompting the higher model for a rich first-person `CharacterProfile` (persona, speaking style, a countervailing depth so no character is one-note, non-verbal / simplicity flags) and instantiating a randomly chosen agent class per character.

---

## Orchestration

**`SimulationEngine`** ([core/simulation_engine.py](core/simulation_engine.py)) holds the agents, board, `GameMaster`, generator, game config, and phase runner. `run()` initialises the board and loops (`run_phase_loop`): while more than one player remains, it asks the `GameDesign` for the next `PhaseDescription` and hands it to the `PhaseRunner`. It also owns elimination — flipping `game_over`, moving the agent to `dead_agents`, and clearing its scoreboard state.

**`PhaseRunner`** ([core/phase_runner.py](core/phase_runner.py)) runs one phase: applies the phase's `config_mutations`, opens the phase, then for each round opens a `RoundBlock`, introduces the phase/game on the first round, dispatches to `run_game()` / `run_vote()` (resolving immunities first for votes), requests a Host round summary, and imposes **brevity jail**. When the phase closes, it summarises phase memory for every agent in parallel. Between rounds it can hold on a **round gate** so a web viewer advances at their own pace.

**`GameDesign`** ([core/levels/game_designs/game_design.py](core/levels/game_designs/game_design.py)) is the abstract base for progression. Concrete designs (beginner 6-player, beginner-8, bumper 11-player, comedy roast, parlor, quickstart tutorial) implement `get_phase_description(phase_number, agent_count, cfg)` and decide *which* rounds, votes, and immunities run in *which* phase — progression logic kept entirely separate from execution. A `make_phase` helper assembles the common "discussion → game → discussion → vote" shape.

**`PhaseDescription`** ([core/levels/phase_description.py](core/levels/phase_description.py)) is a pure blueprint: ordered round classes, optional immunity classes, `config_mutations`, and a `should_summarise_phase` flag. No execution logic.

**Levels** ([level_registry.py](core/levels/level_registry.py)) — each playable level is a [`LevelDefinition`](core/levels/level_definition.py) dataclass (id, name, description, `token_budget`, `game_design`, `locked`), consumed by the launcher and the web frontend. Player range is derived from the game design.

**`GameConfig`** ([core/game_config.py](core/game_config.py)) is a plain data holder for ~100 tunable rules (PD payouts, RPS points, targeted-game amounts, vote rewards, immunity flags, cycle-game compression settings, discussion settings). Behaviour and strings stay in the round classes; only values live here.

---

## Infrastructure

### API client

[`APIClient`](core/api_client/api_client.py) is a thin wrapper over `google.genai` with three model tiers — a default (`gemini-3.1-flash-lite`), a cheaper `lower` tier, and a `higher` tier (`gemini-2.5-flash`) for character generation and phase summaries. Structured outputs go through Gemini's native `response_schema`; the client retries rate limits, transient 5xx errors, and malformed JSON with exponential backoff. It also exposes `transcribe` for spoken human input. A separate thread-safe [`APIRecordManager`](core/api_client/api_record_manager.py) records every call (caller, model, token counts, duration) to a JSONL log and prints a per-caller usage summary at game end.

**Token budgeting is load-bearing, not decorative.** Every game is created with a `token_budget`, hard-capped by the `MAX_TOKENS_PER_GAME` environment variable, and the client raises `BudgetExceeded` the moment recorded usage crosses it. Combined with a mock mode (`_mock_output`) that fabricates schema-shaped responses with no network call, this makes cost bounded and replay/tests free. ([Setup — Vertex AI or Gemini API key — lives in api_client_setup.py](core/api_client/api_client_setup.py).)

### Output sinks

[`GameEventSink`](core/sinks/game_sink.py) is the output contract: game logic only knows this interface, and everything visual is downstream. Beyond speech/thought/score events it carries lifecycle markers, sidebar `widget_update`s, segment titles and feed markers, loading states, and the human-input methods. Implementations:

- [`ConsoleGameEventSink`](core/sinks/console_sink.py) — coloured, animated terminal renderer (via `ConsoleRenderer`).
- [`WebSocketSink`](core/sinks/websocket_sink.py) — serialises each event to JSON and streams it to the browser. Adds a threading-based **round gate** and an input queue (both with inactivity timeouts), a `mobile_outputs` flag that reshapes prompts, and per-game JSONL recording that doubles as the **replay tape**.
- `NoopGameSink` / `CapturingGameSink` — silent and record-everything sinks for tests.

### Web

[web/server.py](web/server.py) is a FastAPI app that mounts three WebSocket routers and a handful of REST endpoints (`/api/flags`, `/api/status`, `/api/characters`, `/api/levels`, `/api/modules`, `/api/fixtures`). Each socket runs a game on its own thread wired to a `WebSocketSink`:

- [`/ws/game`](web/ws_game.py) — a fresh game from a chosen level and cast (optionally with a human).
- [`/ws/demo`](web/ws_demo.py) — a fixture-backed demo module.
- [`/ws/replay`](web/ws_replay.py) — fires a saved tape back through the socket with no LLM calls, stripping live-only events.

Around them sits real production plumbing: Cloudflare Turnstile verification, per-IP daily and concurrency limits plus a token cap backed by a SQLite database ([rate_limits.py](web/rate_limits.py)), input sanitisation and length caps, non-blocking audio transcription, and structured game-start logging. The CLI ([run_terminal.py](core/run_terminal.py)) and every web surface share the exact same engine — only the sink differs.

### Demos, fixtures, and replay

[demo_runner/](demo_runner/) turns a saved snapshot of agent state into a runnable scene. A **fixture** is a JSON capture of a cast mid-game — personas, speaking styles, life lessons, impressions, phase summaries, scores, elimination order — generated from real game logs by [fixture_generation/generate_fixture.py](demo_runner/fixture_generation/generate_fixture.py). [game_setup.py](demo_runner/game_setup.py) loads a fixture, rebuilds the engine with `populate_agents=False`, applies the saved state onto blank agents, and restores scores and eliminations. A **module** ([game_module_directory.py](demo_runner/game_module_directory.py)) then runs a single round or finale against that cast, so a viewer can drop straight into, say, a reunion finale with fully-formed characters — including taking over a finalist as the human, inheriting that finalist's memory. Live games can also be recorded and re-streamed byte-for-byte through `/ws/replay`.

---

## Notable mechanisms

The interesting decisions live in small mechanisms, each there for a specific reason.

### Recency anchor
When it renders the current round, [`ContextBuilder._formatted_public_block`](core/game_context/context_builder.py#L144) finds the agent's own most-recent public message (tracked by a `(block_id, entry_index)` `last_message_id`) and injects a marker right after it — *either* "this was your last turn, react to what's happened since" (if others have spoken since) *or* "it's already been said; your turn now is a fresh action, not a reaction" (if nothing has). Without it, agents parrot themselves or treat their own past words as fresh news. Private conversations are exempt — the frame there is already tight.

### Game ledger as compression substrate
Each `RoundBlock` carries a terse, mechanics-authored `game_ledger` ("Alice stole from Bob."). When older rounds get re-rendered into an agent's context, the full transcript is dropped and the ledger stands in. This is the compression layer for *historical* factual memory — the counterpart to agent-authored phase summaries. Recent rounds keep full text; older rounds in the phase go ledger-only; earlier phases collapse to the agent's own brief summaries. The ledger deliberately omits point counts — agents start doing arithmetic the moment they see numbers, which pulls them off the social/narrative game.

### Brevity jail
At the end of each round, [`PhaseRunner._impose_brevity_jail`](core/phase_runner.py#L97) averages message length per agent and flags the top `player_count // 3` talkers (nobody, for three or fewer players — see [`brevity_jail_count`](core/phase_runner.py#L125)). The flag makes `SystemPrompt` append a "reactions over statements, shortness can be powerful" nudge to their next turn, then resets and re-elects from scratch. A static "be brief" instruction gets ignored; a *relative* "you're currently the wordiest" one moves behaviour because it's grounded in observable difference.

### Life-lesson compression
The `life_lessons` deque is capped at eight, but the real mechanism fires at five: [`_life_lesson_compression_field`](agents/agentic_player.py#L184) injects a `compressed_life_lessons` field (exactly three items) into the next summary turn, and the agent merges its accumulated lessons into three distilled principles that replace the deque. A fixed FIFO loses lessons that mattered; unbounded accumulation grows forever; compression-through-the-agent lets the character decide what's worth keeping — and that decision is itself part of the persona shaping.

### Per-opponent impressions
The turn schema grows one `impression_<name>` field per other live player, and the agent keeps a running note on each. As players are eliminated the fields disappear and the dictionary is pruned to the current roster. This gives agents durable, private, per-rival memory that survives context compression — the substrate for grudges and alliances.

### Optional-response buffer
Discussion and cycle games can make speaking optional and meter it through a buffer that grows a fraction each turn and costs a full unit to spend ([`TurnManager.take_turn_optional`](gameplay_management/turn_manager.py)). Silence becomes a resource an agent saves for high-leverage moments instead of a thing to fill.

### Mask drop
An agent's `game_over` (or an explicit `_mask_drop`) flips `SystemPrompt` into a "the game is over, drop any pretense or false persona" mode. Elimination and the finale use it to get the agent's real voice for final words and victory speeches, distinct from the strategic mask they wore while playing.

### Schema-as-prompt
Every turn assembles a fresh Pydantic model rather than reusing a fixed one, and the field descriptions carry the instructions. The agent's choice space, its introspection prompts, and its self-updates travel together in one structured object passed straight to Gemini's `response_schema`. A new game type is a function returning extra fields — not a new template.

### Sink-driven human input
Because `Human.get_response` collects input through the sink, the same class works in the terminal and the browser. The sink decides how a prompt is rendered and how the answer is gathered — the same indirection that lets the renderer be swapped, reused for input.

---

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

## Phase flow

```
game_design.get_phase_description(phase_number, agent_count, cfg)
    → PhaseDescription (round classes + immunity classes + config_mutations)

PhaseRunner.run_phase(phase_description)
    → apply config_mutations
    → gameBoard.new_phase()
    → for each round_class:
        (round gate — wait for viewer on web)
        gameBoard.newRound()                # opens a RoundBlock
        introduce phase / game on first round
        run_vote(immune players) OR run_game()
        game_master.summariseRound()        # compresses the round to text
        gameBoard.endRound()                # commits the RoundBlock
        _impose_brevity_jail()              # re-elect the wordiest for next round
    → if should_summarise_phase:
        every agent (and, in dev, the dead) writes phase memory in parallel
    → reset discussion settings, endPhase()
```

---

## Memory & context

Memory narrows from raw to distilled as the horizon widens — the core trick that keeps a long game affordable:

- **Raw log** — every message lands in `GameLog` and is never deleted. The current round accumulates in full.
- **Per-round ledger** — a terse, numbers-free record of mechanical facts that stands in for the transcript once a round is no longer recent.
- **Per-agent phase summaries** — at each phase boundary every agent writes a detailed and a brief summary; only the two most recent phases keep their detailed form, earlier ones collapse to brief.
- **Live state** — persona, strategy, speaking style, life lessons, and impressions, rewritten every turn through the evolution fields.

The recency anchor reaches across all of these — it walks the raw log backward to find the agent's last message and marks it in whatever layer the agent is shown. It's the one mechanism that ignores the horizon boundaries, by design, because conversational ownership is the same problem at every scale.
