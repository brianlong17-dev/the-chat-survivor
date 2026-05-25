# Architecture

This project is in two parts: The agentic players and the game framework.

This is a Claude summary of the project- I will come back to this document later.

1. **Orchestration** — drives the game loop. A `SimulationEngine` runs phases (`PhaseRunner`) according to a `GameDesign` that emits `PhaseDescription` blueprints.
2. **Round execution** — per-round classes (`BaseRound` + mechanics mixins) own the moment-to-moment turn flow via a `TurnManager`. Agents (`Debater`, `GameMaster`, `Human`) produce structured LLM responses through a `DynamicModelFactory`.
3. **State & presentation** — a single `GameBoard` holds all live state (scores, message log, phase/round counters) and fires events into a swappable `GameEventSink`. The same engine drives both a terminal renderer and a web client; only the sink differs.

> A reality-TV-style elimination game where LLM agents compete through discussion rounds, mini-games, and voting eliminations. Agents have evolving state and memory and are eliminated until one winner remains. See [README.md](README.md) for the premise and design motivation; this document covers the mechanisms.

---

## Components

### Orchestration

**`SimulationEngine`** ([core/simulation_engine.py](core/simulation_engine.py)) — top-level holder of all major components, owns the main loop (`run_phase_loop`), handles player setup and elimination, delegates each phase to `PhaseRunner`.

**`PhaseRunner`** ([core/phase_runner.py](core/phase_runner.py)) — executes one phase: applies `config_mutations`, iterates the rounds in order, dispatches to game/vote logic, requests a round summary from the `GameMaster`, imposes brevity jail at round end, and runs parallel phase-memory summarisation when the phase closes.

**`GameDesign`** ([core/levels/game_designs/game_design.py](core/levels/game_designs/game_design.py)) — abstract base for game progression. Concrete subclasses (`GameDesignDefault`, `GameDesignBeginner`) implement `get_phase_description(phase_number, agent_count, cfg)` and decide *which* games, votes, and immunities run in which phase. Encodes progression logic separately from execution.

**`PhaseDescription`** ([core/levels/phase_description.py](core/levels/phase_description.py)) — a Pydantic data object: ordered round classes, optional immunity classes, and a list of `config_mutations` applied at phase start. No execution logic; just a blueprint `PhaseRunner` consumes.

**`LevelDefinition` / `level_registry`** ([core/levels/level_registry.py](core/levels/level_registry.py)) — each playable "level" (beginner, standard, intermediate) is a dataclass — id, name, description, player range, and the `GameDesign` class to use. Used by the launcher / web frontend to pick a game.

### State and context

**`GameBoard`** ([core/gameboard.py](core/gameboard.py)) — central live state. Holds agent scores, phase/round counters, the `ContextBuilder`, and a reference to the `GameLog`. Also the broadcast surface — game logic calls `host_broadcast`, `broadcast_public_action`, etc., which both append to the log and fire sink events. Anything that needs to know "what's happening right now" goes through here.

**`GameLog`** ([core/game_context/game_log.py](core/game_context/game_log.py)) — append-only message store. Owns `current_round` (an open `RoundEntry`) and `completed_round_entries`. Every public broadcast, every private conversation, every system message lands here as a `MessageEntry`. The single source of truth for "what was said."

**`RoundEntry` / `MessageEntry`** ([core/game_context/models.py](core/game_context/models.py)) — see [Data Model](#data-model) below. These two structures, together with the visibility model and the per-round `game_ledger`, are how the system stays cheap to read at long horizons.

**`ContextBuilder`** ([core/game_context/context_builder.py](core/game_context/context_builder.py)) — given an agent, assembles the context string they'll see this turn: scores, current-round transcript (filtered by visibility), previous rounds (often compressed to the ledger), and the *recency anchor* injection that marks the agent's own last message. The visibility filter and the recency anchor both live here; both are described under [Notable mechanisms](#notable-mechanisms).

### Round execution

**`BaseRound` (and mixins)** ([gameplay_management/base_manager.py](gameplay_management/base_manager.py)) — abstract base. Every round type (discussion rounds, individual game classes like `GamePrisonersDilemma`, `GameMob`, `GameGuess`; votes like `VoteBottomTwo`, `VoteEachPlayer`; the finale `FinaleReunionRound`) inherits from `BaseRound` and pulls in the relevant mechanics mixins (`GameMechanicsMixin`, `VoteMechanicsMixin`, `ImmunityMechanicsMixin`). `PhaseRunner` instantiates each round class fresh per round and calls `.run_game()` / `.run_vote()`. Long round files (`game_mob.py`, `game_pd_finale.py`, `reunion_round.py`) are intentionally script-shaped — each method is a beat in the round's story, with `run_game()` at the bottom as the orchestrator.

**`TurnManager`** ([gameplay_management/turn_manager.py](gameplay_management/turn_manager.py)) — per-round helper owned by `BaseRound`. Drives one turn: builds the dynamic response model via `DynamicModelFactory`, calls the agent, dispatches broadcasts. Also owns the *optional-response buffer* mechanic — on optional turns, an agent accrues 0.6 of a "speaking credit" per turn whether they speak or not; speaking costs 1. Encourages saving turns for high-leverage moments rather than chiming in every round.

**`DynamicModelFactory`** ([models/player_models.py](models/player_models.py)) — generates a fresh Pydantic response model *per turn*. Every model includes `public_response` and `private_thoughts`; on top of those, the factory adds the agent's cognitive fields (persona update, life lesson, strategy) plus any turn-specific action fields — a `Literal["split", "steal"]` for prisoner's dilemma, a name-choice field for targeted games, an optional `will_you_speak_or_remain_silent` for buffered turns. The structured-output schema is rebuilt per call; the LLM never sees freeform JSON. See [Notable mechanisms](#notable-mechanisms).

### Agents

**`Debater`** ([agents/player.py](agents/player.py)) — main player. Holds evolving state (described in [Memory & context](#memory--context)) and exposes `take_turn_standard()` for normal turns and `summarise_phase()` at phase boundaries.

**`GameMaster`** ([agents/game_host.py](agents/game_host.py)) — special LLM agent with display name "Host". Summarises rounds into compressed text (rolling deque of 50). Also picks players parametrically — `choose_agent_based_on_parameter` for wildcard immunity selection, `select_players` for question-driven group picks — and generates host narration via `create_host_script`.

**`Human`** ([agents/human_player.py](agents/human_player.py)) — subclasses `Debater` and overrides `get_response` to route through `game_sink.get_user_input_*` instead of an LLM call. Human input is sanitised (colons, bracketed system tags, fence lines stripped) to keep humans from spoofing system messages. `summarise_phase` is a no-op for humans. The sink does the actual I/O — `ConsoleGameEventSink` reads stdin, `WebSocketSink` round-trips through the browser — so the same `Human` class works on both surfaces.

### Infrastructure

**`APIClient`** ([core/api_client.py](core/api_client.py)) — thin singleton around `google.genai`. Retries 429s with exponential backoff, records per-call usage stats (caller, tokens, ms), writes a JSONL call log. Structured outputs use Gemini's native `response_schema=` parameter — the `instructor` import in [bootstrap.py:4](core/bootstrap.py#L4) is vestigial.

**`GameEventSink`** ([core/sinks/game_sink.py](core/sinks/game_sink.py)) — output abstraction. Game logic only knows about this interface; everything visual is downstream. Two concrete sinks today:
- `ConsoleGameEventSink` ([core/sinks/console_sink.py](core/sinks/console_sink.py)) — terminal renderer, colored, animated text.
- `WebSocketSink` ([core/sinks/websocket_sink.py](core/sinks/websocket_sink.py)) — serialises events to JSON, streams to a connected web client.

**Web frontend (optional)** — [server.py](server.py) is a FastAPI bridge: REST endpoints for setup (character generation, available levels, feature flags), an audio transcription endpoint for spoken human input, and two WebSocket endpoints (`game_ws`, `demo_ws`) that each spin up a `SimulationEngine` wired to a `WebSocketSink`. The client in [frontend/](frontend/) is a Vite/React app that consumes the stream. The CLI and the web client share the same engine — only the sink changes.

---

## Data Model

### `RoundEntry`
```
phase_number: int
round_number: int
messageEntries: list[MessageEntry]
game_ledger: str            # see below
```

### `MessageEntry`
```
messages: list[{"speaker", "message"}]
id: int                     # monotonic; used for "messages since" queries
visibility_restriction: set[str] | None   # None = public
closed: bool                # for private conversations that can be reopened
```

### Visibility model
`visibility_restriction` is the *single* mechanism that drives every private-message behaviour in the system. `None` means public. A set of names means only those agents see it in their context. `ContextBuilder._formatted_round` reads this when assembling each agent's view and either includes the message verbatim, wraps it in `=== Private Conversation between X & Y ===` markers, or skips it entirely. Private host conversations, two-player negotiations, sys-admin-only system messages — all the same field. One decision point, no parallel ACL system.

### Game ledger
Each `RoundEntry` carries a `game_ledger` string: a terse, mechanics-emitted record of what happened that round ("Alice stole from Bob.", "Bob gave points to Carol."). Game logic appends to it via `GameLog._push_to_game_ledger`. When formatting context for an agent, older rounds collapse to *only* their ledger ([context_builder.py:99-100](core/game_context/context_builder.py#L99-L100)) — the full transcript is dropped. The current round shows the transcript with the ledger appended at the end. This is the compression substrate that lets the game run long without unbounded context growth. The ledger deliberately omits point counts — agents start doing arithmetic when they see numbers, which distorts their behaviour away from the social/narrative game.

---

## Notable mechanisms

The interesting decisions sit inside small mechanisms scattered through `context_builder.py` and the agent state. Each one exists for a specific reason.

### Recency anchor
[`ContextBuilder._recency_anchor`](core/game_context/context_builder.py#L123) walks the message history backward (current round, then previous rounds) looking for the agent's own most-recent *public* message. When formatting context, that message gets a marker injected directly after it: the agent's last internal thought, followed by *either* "this was your last message — react to what's happened since" (if other players have spoken since) *or* "this was your last message — it's already been said, your turn now is a fresh action, not a reaction" (if nothing has happened since).

**Why it exists:** without it, agents repeat themselves, parrot their last statement back, or treat their own past words as fresh news. The anchor tells them *what's mine* and *what's new* in a way that the raw transcript doesn't. Private conversations are intentionally exempt — there the anchor isn't relevant, since the conversational frame is already tight.

### Game ledger as compression substrate
See [Data Model](#game-ledger). The architectural point: this is the compression layer for *historical* context. Phase summaries are agent-authored narrative memory; the ledger is mechanics-authored factual memory. Together they replace transcripts at the right horizon — recent rounds get full text, older rounds in the same phase get ledger-only, and earlier phases collapse further to the agent's own brief summaries.

### Brevity jail
At the end of each round, [`PhaseRunner._impose_brevity_jail`](core/phase_runner.py#L85) computes average message length per agent, picks the top `player_count // 3` talkers, and flips `brevity_jail = True` on them. That flag is read by [`SystemPrompt`](core/game_context/system_prompt.py#L62), which appends a "reactions over statements, occasional shortness can be powerful" prompt to their next system message. The flag resets each round and is re-elected from scratch — so it's self-correcting and traded around as the conversation shifts.

**Why it exists:** without an active corrective, LLMs balloon. Long messages crowd the transcript, hide signal, and make context windows expensive. Static "be brief" prompts get ignored; a *relative* "you're currently the longest-winded" prompt actually moves behaviour because it's grounded in observable difference. The top-third threshold is the tuning knob.

### Life-lesson compression
The `Debater.life_lessons` deque is capped at 8 entries, but the more interesting mechanism is at 5+: [`Debater._life_lesson_compression_field`](agents/player.py#L160-L176) injects a `compressed_life_lessons: list[str]` field (required exactly 3 items) into the *next* summary turn. The agent is forced to merge their accumulated lessons into 3 distilled principles, replacing the deque contents. New lessons can then accumulate again until the cycle repeats.

**Why it exists:** a fixed-window FIFO loses lessons that mattered. A pure deque accumulation grows unbounded. Compression-through-the-agent is a third option — the agent decides what's worth keeping, and the decision itself is part of the persona shaping over time.

### Dynamic per-turn model construction
Every turn assembles a fresh Pydantic model rather than reusing a fixed schema. The model varies by turn type: a normal discussion turn carries persona/strategy/life-lesson fields plus `public_response` and `private_thoughts`; a prisoner's-dilemma turn adds a `Literal["split", "steal"]` choice; a targeted-game turn adds a name-choice constrained to live players; a buffered turn adds `will_you_speak_or_remain_silent` and reframes `public_response` as `Optional[str]`. The structured-output schema is rebuilt per call and passed straight to Gemini's `response_schema`.

**Why it matters architecturally:** schema-as-prompt. The field descriptions on the Pydantic model *are* the per-turn instruction set for the LLM — the agent's choice space and the agent's introspection prompts ride together. Adding a new game type is a function that returns extra fields, not a new prompt template.

### Sink-driven human input
Because `Human.get_response` routes input through the sink (`game_sink.get_user_input_simple`, `get_user_input_multiple_choice`), the same human-player class works in the terminal and the browser. The sink decides how the prompt is rendered and how the response is collected. This is the same indirection that lets the renderer be swapped — it just gets re-used for input.

---

## Agent turn flow

```
ContextBuilder._recency_anchor(agent)
    → finds agent's last public message + whether anyone has spoken since

UserContent.render(agent, game_board, turn_instruction)
    → dashboard (scores, status)
    → phase summaries (older phases, compressed)
    → previous rounds (ledger-only when not recent)
    → current round (with recency-anchor marker)
    → turn instruction

SystemPrompt.render(agent)
    → persona, speaking style, life lessons, strategy, position assessment
    → brevity-jail nudge if flagged
    → optional-response buffer status

DynamicModelFactory.create_model_(agent, turn_type, action_fields, …)
    → fresh Pydantic model with public_response + private_thoughts
      + cognitive fields + game-specific action fields

APIClient.create(response_model, messages)
    → Gemini call with response_schema; structured Pydantic object returned

agent.process_turn_cognitive_fields(turn)
    → persona, game_strategy, life_lessons, speaking_style, position_assessment,
      round_specific_strategy updated in-place from the structured output

GameBoard.handle_public_private_output(agent, response, …)
    → public_response appended to GameLog (visible to others)
    → private_thoughts emitted to sink only (visible to viewer, not other agents)
    → recency anchor for next turn now points at this message
```

The separation between `ContextBuilder`, `SystemPrompt`, and `UserContent` is deliberate — they answer three different questions ("what does this agent *see*?", "who are they?", "what are they being asked to do right now?") and stay independently swappable.

---

## Phase flow

```
game_design.get_phase_description(phase_number, agent_count, cfg)
    → PhaseDescription (ordered round classes + immunity classes + config_mutations)

PhaseRunner.run_phase(phase_description)
    → apply phase_description.config_mutations to gameplay_config
    → gameBoard.new_phase()
    → for each round_class in phase_description.rounds:
        gameBoard.newRound()                # opens a new RoundEntry
        _introduce_phase()  if first round  # host + system broadcasts
        _introduce_game()   if phase 1 r 1  # human-facing game intro
        round_class(game_board, sim_engine).run_vote() / run_game()
        game_master.summariseRound()        # compresses round to text
        gameBoard.endRound()                # commits RoundEntry to history
        _impose_brevity_jail()              # top talkers flagged for next round
    → agents.summarise_phase() in parallel  # each agent writes phase memory
    → gameBoard.endPhase()
```

---

## Memory & context

Three layers, narrowing from raw to distilled as the horizon widens.

**Raw log** — every public broadcast, host message, and private conversation lands in `GameLog` as a `MessageEntry`. This is the ground truth; nothing is ever deleted. The `current_round` is open and accumulating; `completed_round_entries` accumulate behind it.

**Per-round ledger** — alongside the transcript, each round carries a terse `game_ledger` string of mechanics-emitted facts. Numbers excluded. When older rounds get re-rendered into an agent's context, the transcript is dropped and the ledger stands in. This is the dominant compression at the round horizon.

**Per-agent phase summaries** — at the end of each phase, every agent writes their *own* summary of the phase using the higher model: a detailed narrative summary and a brief one, both keyed by phase number on the agent. When rendering older phases into context, only the most recent `detailed_summary_count` (currently 2) keep their detailed form — earlier phases collapse to brief. This is the dominant compression at the phase horizon.

Live state — `persona`, `game_strategy`, `position_assessment`, `life_lessons`, `speaking_style`, `round_specific_strategy` — is updated *every turn* via the structured-output cognitive fields, so the agent's self-description evolves alongside the game rather than being snapshotted at intervals. `life_lessons` is the one piece of live state with its own compression cycle (see [Notable mechanisms](#notable-mechanisms)); the rest are free-form strings the agent rewrites in place.

The recency anchor reaches across all of this: it walks the raw log backward to find the agent's last message and injects a marker into whatever context layer they're being shown. It's the one mechanism that doesn't respect the horizon boundaries — by design, because conversational ownership is the same problem at every horizon.
