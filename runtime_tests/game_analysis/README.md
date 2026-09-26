# Game Analysis

Experimental evaluation framework — not fully functional, more conceptual at this stage.

The idea: load entire game histories into a database, then embed each message so the
resulting vectors can be analysed for meaning — whether characters are staying distinctive
over the course of a game, or converging toward some generic "optimizer" voice.

## Pipeline

```
logs/gamelogs/*.jsonl --[GameIngestor]--> messages table --[GameMessageEmbedder]--> embeddings table --[DistinctiveVoiceAnalyser]--> voice_scores table
```

All three tables live in `data/embeddings.db`.

- **`game_analyser.py`** — `GameAnalyser`: builds an in-memory `game_log` for one game, either
  from the raw log file (`source="file"`) or from the `messages` table (`source="db"`).
- **`game_ingestor.py`** — `GameIngestor`: reads one game's raw log and writes it to the
  `messages` table. Skips known demo/mock games.
- **`game_message_embedder.py`** — `GameMessageEmbedder`: embeds ingested messages (hashed
  bag-of-words or Gemini embeddings) and writes vectors to the `embeddings` table. Also owns
  `CONTROL_GAME_IDS` — games known to have run a non-standard agent class, flagged so they're
  excluded from the "normal" centroid.
- **`game_analyser_distinctive_voice.py`** — `DistinctiveVoiceAnalyser(GameAnalyser)`: loads
  embeddings and scores each character's drift from a centroid over the course of a game.
- **`running/`** — manual CLI scripts that drive the above (not automated tests).
- **`outputs/`** — generated plots (gitignored).

## Caveats

- `messages` was only backfilled retroactively — some already-embedded games may have gaps.
- Control-game detection is manual (`CONTROL_GAME_IDS`); nothing in the game log itself
  records which agent class produced a game.
- Scoring only works for games with 2–3 finalists; short/aborted games score as `None`.
