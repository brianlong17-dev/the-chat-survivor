# Character & Prompt Changelog

Tracks edits to character-generation prompts and agent response-model field descriptions over time. Organized by file, then by method/field. Each field keeps a running history: **Initial** is the earliest known version, then each later revision is added as its own dated entry below it (newest last). When a field changes again, append a new dated entry rather than overwriting the last one.

---

## `agents/character_generation/characterGeneration.py`

### Field: `CharacterProfile.persona`
- **Initial:** `"A detailed, first-person personality description, core beliefs, and strategic outlook if thrown into a game figure. What sensitive nuance behind this person?"`
- **2026-08-04:** `"A detailed, first-person personality: their core beliefs, what they want, what they love and what they can't stand, their contradictions and blind spots. A vivid character with a real emotional core - a full personality they'll respond to the game through, rather than a strategy. What is the sensitive nuance behind this person?"` — pushes toward a full emotional character rather than a strategy summary.

### Field: `CharacterProfile.speaking_style`
- **Initial:** `"Their speaking style, how they talk, to preserve the character from context bleed. Do not write specific phrases."`
- **2026-08-04:** `"(First person) Their speaking style, how they talk, writen in their unique register- to preserve the character from context bleed. Do not write specific phrases."` — clarifies voice should be written in the character's own register.

### Field: `CharacterProfile.vocal_register`
- **2026-08-04 (new field):** `"What register do they speak in? Use this to write them, since it's a self description."` — added to give the model an explicit self-described register to write speaking_style from.

### Field: `CharacterProfile.additional_depth`
- **Initial:** archetype-branched single countervailing depth (Baddie → relatable/wounded side; Hero → cheeky imperfection; Sweet → shrewd/dry side; Otherwise → compassion/depth).
- **2026-08-04:** same archetype branches, but each now lists multiple non-wound options (private appetite, grudge, vanity, hypocrisy, stubbornness, mischief, self-interest) alongside the wound option, with explicit note "Not necessarily sad." — broadens the "extra line" beyond wound/soft-heart tropes.

### Method: `CharacterGenerator.generate_agent` — system/user prompt
- **Initial:** system = `"You are generating a starting profile for a character starting in a competitive gameshow. They should be as competitive as their character allows. The name is typically of someone from popular culture, that it should be based on."`; user = `"Create a rich, first-person persona and a physical form description for the historical figure or character: {name}. Make them colorful."`
- **2026-08-04:** system reframed to "chaotic, social gameshow," emphasizing a full colorful personality with real emotional core outside the game, "how do they move through a group where survival is key, perhaps in spite of themself"; user drops the physical-form description ask, keeps "rich, first-person persona and description... colorful and vibrant."

---

## `agents/agentic_player_v2/agentic_player.py`

### Field: `life_lessons`
- **Initial:** `"OPTIONAL: What new strategic lessons have you learned? Write from your persona."`
- **2026-08-04:** `"OPTIONAL: From your unique persona perspective- Is there a life lesson you want to carry forward? (Write in initial speaking style.)"` — reframes from "strategic lessons" to a persona-driven life lesson.

---

## `agents/player_response_models.py`

### Field: impression field (first player, `AgentResponseModelFactory`)
- **Initial:** `"OPTIONAL: Since last turn, your updated impression of the following players- (don't lose any existing key memories, but update with any new noticings). {i+1}: {name}"`
- **2026-08-04:** `"Player Impressions - Selectively update players where your impression has evolved: {i+1}: {name}"` — simplifies wording, drops explicit "don't lose existing memories" caveat in favor of "selectively update."

---

## `runtime_tests/test_character_generation.py`
Test-harness only (no prompt content to track). 2026-08-04: switched to `generate_agent` (v2) from `generate_debater`, updated printed fields to `initial_persona`/`initial_speaking_style`, adjusted the sample name list used for manual runs.
