# Knives — Script (V1 / V2)

All player-facing copy from `game_knives_2.py`. **V1** is the original, **V2** is the Bleak-Sword baseline (sober, declarative — restraint now, ornament later). Placeholders in `{braces}` are filled in at runtime.

**Voice principles for V2:**
- Public copy is ceremonial — it belongs to the world.
- Private copy is grounded — it reminds the player they're still in the *competition*.
- Short, declarative sentences. The Lights, The Knife, The Circle — definite articles do the work.
- No exclamation marks. No game-show patter.


## 1. Metadata

**Display name** — unchanged: `Knives`

**Rules description** (menu / context only — not in-game)

**V1:**
> Every player starts with a knife. The lights go off — each player secretly stabs someone or passes (keeping their knife for later). The lights come back on: the player with the most knives in their back dies. Ties mean all tied players die. Dead players' knives are randomly redistributed among survivors. Players who passed accumulate knives for future rounds. If every remaining player dies simultaneously, they all win and earn bonus points (1 point in round 1, 2 in round 2, etc.). Last 3 standing earn points.

*(V2 not yet drafted — note: the last sentence ("Last 3 standing earn points") contradicts the actual scoring. Editorial flag.)*


## 2. Game start

### Private disclaimer (sent to every player before the game)

**V1:**
> This is a parlor game- you can play it up but the knives aren't real- the only backstabbing is strategic. The only thing at stake- points, and your place in the competition.

**V2:**
> A parlor game. The knives are theatre. The points are not. Neither is your place in this competition. Play it cold.

### Welcome broadcast (public)

**V1:**
> Welcome to KNIVES! You each have one knife. When the lights go out, you can stab someone... or pass and keep your knife for later. When the lights come up, the player with the most knives in their back dies. Ties? Both die. But if you survive a stabbing, you keep those knives in your back as weapons for the next round. If everyone dies at once — game over. {points_string}  Remember — the lights are out. No one knows what you did. Let's go!

**V2:**
> A circle. A knife each.
> The lights die. Choose, or pass.
> The lights return. The most-stabbed falls. Ties fall together.
> Survive a stabbing — the blades are yours next round.
> Fall together, win together.
> {points_string}
> Lights out.

### Points-mode line (slots into the welcome)

| Mode | V1 | V2 |
|------|----|----|
| Runner-up | "The player with most stabbings who survives gets a point for each knife." | "The most-wounded survivor takes a point for each blade." |
| Survival  | "You receive a point for every round you survive." | "A point for every round you remain." |


## 3. Round opener

### Knives-count header (followed by stacks of 🗡 per player)

**V1:** `The knives for each player:`
**V2:** `Each of you holds —`

### Round announcement

**V1:** `Round {round_number}. Ready? Lights out...!`
**V2:** `Round {round_number}. Lights out.`


## 4. Stab decision (LLM prompt)

### User-content prompt (the player's turn instruction)

**V1:**
> The lights are off. You have {knife_string}. For each knife, choose someone to stab or pass to keep it. You can stab the same person multiple times. You could stab yourself. The other players in the circle are: {other_names}.

**V2:**
> The lights are out. You hold {knife_string}. For each — name a target, or pass and keep it. You may stab the same player twice. You may stab yourself. The circle: {other_names}.

### Per-knife field description

**V1:** `Knife {i}: choose a player to stab, or 'Pass' to keep this knife for later.`
**V2:** `Knife {i}: name a target, or pass.`

### Public response prompt — chatty mode

**V1:**
> You can say something or stay silent. The lights are off — no one can see your decision. You can lie, boast, stay quiet... it's up to you.

**V2:**
> Speak, or don't. The lights are out. No one sees what you do — only what you say.

### Public response prompt — silent mode

**V1:** `This wont be broadcast and can be left empty.`
**V2:** `Optional. Not broadcast.`

### Internal thought nudge

**V1:**
> Who is the biggest threat? Should you spread your knives or focus on one target? Is it worth passing to save knives for later?

**V2:**
> Who is the threat? Spread the knives, or focus them? Pass — and keep them for later?


## 5. Stab reveal (private to each player)

### If unhurt

**V1:** `You check your back... no knives.`
**V2:** `You feel for blades. None.`

### If stabbed

**V1:** `Oh no! You've been stabbed {count} time{s}!`
**V2:** `{count} blade{s}. Still standing.`

> *Note: "Still standing" does the grounding work — even when this player is about to be eliminated this round, it reminds them they remain in the **competition**.*


## 6. Lights up — public announcements

### Stabbings reveal (header followed by `{name} — 🔪🔪🔪` per stabbed player)

**V1:** `The lights come up... `
**V2:** `The lights return.`

### Death announcement (public)

**V1:**
> With {knife_string} in their back: It is with great sadness we announce the death of {dead_names}.

**V2:**
> {knife_string}. {dead_names}. They fall.

### Death consolation (private — load-bearing)

**V1:**
> {name} - you haven't been eliminated from the game! You're only finished up in the minigame. Well done!

**V2:**
> {name} — you fell in the dark. You did not fall from the game. Onwards.

> *This is the line keeping players grounded. "In the dark" honors the theatrical death; "from the game" distinguishes elimination-in-the-fiction from elimination-in-the-competition.*


## 7. Round endings

### No stabs at all (round resets)

**V1:** `No stabs in the dark... we continue`
**V2:** `The dark passed quietly. Again.`

### Total wipeout (everyone tied for top stabs, top > 0 — game ends)

**V1:**
> Incredible... {survivor_names} — you all go down together. Each with {knife_string} in their back.

**V2:**
> {names} — {knife_string} each. The circle falls together.

### Sole survivor (game ends with one player standing)

**V1:** `Our last survivor! {name} receives a bonus of {bonus} points!`
**V2:** `One stands. {name}. {bonus} points to the last to stand.`


## 8. Scoring announcements

### Runner-up bonus (runner-up mode)

**V1:** `{count} bonus point{s} for being the most stabbed survivor go to: {names}`
**V2:** `Most-wounded survivor — {names}. {count} blade{s}. {count} point{s}.`

### Survival point (survival mode)

**V1:** `{names} each get a point for surviving.`
**V2:** `{names}. A point each, for standing.`


## 9. Knife redistribution

**V1:** `Redistributing the {knife_string} found on {dead_names}...`
**V2:** `{knife_string}, taken from the fallen. Redivided.`


## 10. Runner-up speech turn (LLM prompt)

Each runner-up gets a speaking turn after their bonus is announced.

### Prompt

**V1:**
> You were stabbed {count} times, but survived. How do you feel? What do you have to say? Do you have any suspects?

**V2:**
> {count} blade{s} found you. You stand. Speak — accuse, or hold your tongue.

### Instruction

**V1:** `Speak to the group. Be coy or brash, or whatever your personality prompts you to do.`
**V2:** `Address the circle, in your own voice.`


## 11. Optional inter-round pitch (LLM prompt)

### Prompt

**V1:** `Before we head to the next round, would you like to say something to the group?`
**V2:** `The lights still hold. Speak, before they die again.`

### Instruction

**V1:** `Speak to the group, or return an empty response to remain silent.`
**V2:** `A few words to the circle, or silence. Either is allowed.`

### Private thoughts prompt

**V1:** `Could you direct the group? Or will you just draw attention?`
**V2:** `Direct the group? Or draw attention to yourself?`


## What's held back for a "spookier" pass

V2 deliberately stays restrained. For a future ornament pass, candidates:

- Capitalized abstractions for the recurring beats — *the Dark*, *the Circle*, *the Blade*.
- A more ceremonial death line — *"They have answered the knives."*
- A weightier curtain-call line for the sole survivor — the climax wants more than the current functional line.
- Round numbering as something other than "Round 1" — *the first dark*, *the second dark*.
- Maybe an opening invocation before the welcome — a single line that sets the dread before the rules begin.
