# Fixture ↔ Agent state mapping

How a fixture JSON entry maps to `Agent` state and to the rendered system prompt
(`agents/system_prompt.py`). Generate parses the prompt back into fixture
keys; game_setup applies fixture keys onto the live agent. When the prompt changes,
both `generate_fixture.py` and `game_setup.py` drift — check here first.

## Fields the prompt renders today

Source of truth: `SystemPrompt.player_system_prompt` in `agents/system_prompt.py`.

### Profile block (`=== YOUR PROFILE ===`)
| Agent attr | Prompt label |
|---|---|
| `initial_persona` | `Core Persona:` |
| `additional_persona_coloring` | `Additional Persona Coloring:` |
| `persona_unique_detail` | `Unique persona detail:` |
| `initial_speaking_style` | `Core Speaking Style:` |
| `speaking_style_update` | `Speaking Style Additional Consideration:` |

### Life lessons (`=== LIFE LESSONS ===`)
| Agent attr | Prompt |
|---|---|
| `life_lessons` | bulleted list under `Use these past learnings to guide your current behavior:` |

### Character impressions (`=== CHARACTER IMPRESSIONS ===`)
| Agent attr | Prompt |
|---|---|
| `character_dictionary` | one line per entry: `- {name}: {impression}`, where `name` is the dict key with the `impression_` prefix stripped |

### Strategy block (`=== YOUR INTERNAL STRATEGY AND ASSESSMENT ===`, omitted when `game_over`)
| Agent attr | Prompt label |
|---|---|
| `game_strategy` | `Current Strategy:` |
| `character_strategy` | `Character Strategy:` |
| `position_assessment` | `Position Assessment:` |
| `round_specific_strategy` | `Current round strategy:` (only if set) |

## Current fixture format

Written by `generate_fixture.py`, read by `game_setup.py`:

| Fixture key | Maps to | Notes |
|---|---|---|
| `initial_persona` | `agent.initial_persona` | parsed from `Core Persona:` label |
| `additional_persona_coloring` | `agent.additional_persona_coloring` | parsed from `Additional Persona Coloring:` |
| `persona_unique_detail` | `agent.persona_unique_detail` | parsed from `Unique persona detail:` |
| `initial_speaking_style` | `agent.initial_speaking_style` | parsed from `Core Speaking Style:` |
| `speaking_style_update` | `agent.speaking_style_update` | parsed from `Speaking Style Additional Consideration:` |
| `strategy` | `agent.game_strategy` | parsed from `Current Strategy:` |
| `character_strategy` | `agent.character_strategy` | parsed from `Character Strategy:` |
| `position_assessment` | `agent.position_assessment` | also reads legacy `math_assessment` key |
| `life_lessons` | `agent.life_lessons` | bulleted list, capped at 8 |
| `character_dictionary` | `agent.character_dictionary` | parsed from impressions block; keys have `impression_` prefix |
| `summaries_brief` | `agent.phase_summaries_brief` | keyed by phase number string |
| `summaries_detailed` | `agent.phase_summaries_detailed` | keyed by phase number string |
