# Handoff: Chat Survivor — Demos (Teletype)

## Overview

The **Demos** page, restyled into the teletype/paper language already shipped for the lobby and About pages. This is a **visual redesign only** — the page structure, sections, controls, and data flow are unchanged from the current `DemosPage.jsx`. Nothing was added or removed except two small copy/behaviour changes noted under *Deviations*.

Three collapsible sections, one open at a time:

1. **Finales** — pick a finale format, pick a fixture, watch or play it.
2. **Game modules** — same pattern for unintegrated game rounds.
3. **Completed game runs** — replay whole recorded games.

## About the Design Files

`Demos Teletype.dc.html` is a **design reference created in HTML**, not production code. Open it in a browser to see it running; read it to extract exact values; then apply the values to the existing `DemosPage.jsx` / `App.css`. Do not port the file literally.

Reading the source: the template holds structure and refers to styles by name (`{{ someStyle }}`); a `renderVals()` method returns every style object. `<sc-if>` is conditional rendering, `<sc-for list as>` is a loop.

The fixture, module, and runthrough data in the file is a **static snapshot** of what the real page fetches from `/api/fixtures` and `/api/modules`. Keep the live fetches.

## Fidelity

High fidelity on colour, type, spacing, and states. Copy is unchanged from the live page except where noted.

---

## Design tokens

Identical to the lobby handoff (`design_handoff_lobby_teletype/README.md`) — reuse those variables rather than redefining. Summary:

| Token | Light | Dark |
|---|---|---|
| `bg` | `#efe9df` | `#16150f` |
| `ink` | `#1c1a17` | `#eae4d8` |
| `body` | `#5f584d` | `#9a9285` |
| `muted` | `#8d8577` | `#7a7365` |
| `rule` | `#c9bfae` | `#3c392f` |
| `hair` | `#ddd4c5` | `#2b2921` |
| `tint` | `rgba(224,123,84,0.08)` | `rgba(224,123,84,0.12)` |

**Accent** `#e07b54` in both themes. **Space Mono** 400/700 only. No cards, no shadows, **no border-radius anywhere**. Full-bleed ruling overlay (1px hairline every 6px at ~1.8% ink) sits behind the page, `pointer-events: none`.

### Two demos-page-only additions

Both exist because this page is denser than the lobby and terracotta hairlines wash out on light paper.

- **`line` — selected border colour.** `#c25c30` in light mode (a deepened accent), plain `#e07b54` in dark. Used for the border of every selected control. Accent *text* stays `#e07b54`.
- **`fill` — selected background.** `tint` in light mode, transparent in dark. Dark mode needs no fill; light does.

### Column

`max-width: 1040px`, `padding: 0 28px`, centred column, content left-aligned. Wider than the lobby's 860px because the fixture grid needs 3–4 columns; everything else still sits on the left edge.

---

## Page structure

### Top bar

Identical to About/Lobby: `CHAT SURVIVOR` small-caps label left; `game / demos / about` nav plus theme toggle right. `demos` is the active nav item (accent text, 1px accent bottom border, `cursor: default`).

### Hero

- `Demos`, 52px / 700 / `-0.01em`, followed inline by the blinking accent cursor (`tBlink 1.1s step-end infinite`).
- Sub: "Pre-loaded game scenarios from real playthroughs." 14px, `body`, `max-width: 460px`.

### Section headers (replaces `.collapsible-header`)

A full-width button: caret + title + a **1px hairline that runs to the right edge** + a right-aligned count.

- Caret `▸` / `▾`, 11px, `accent` when open, `muted` when closed.
- Title in the small-caps label style but at **12px**, `0.24em`, uppercase, colour `ink` (not muted — this is the one place the label carries a heading).
- Rule: `flex: 1; height: 1px; background: hair`.
- Right meta: `7 FIXTURES` / `3 FULL GAMES`, 10.5px, `0.14em`, uppercase, `muted`.
- Padding `22px 0 14px`. Body animates in with `tFade 0.3s ease-out both`.

Accordion behaviour is unchanged: opening one closes the other.

### Sub-headers (`FINALE FORMAT`, `FIXTURES`, `WATCH / PLAY`)

Same construction one level down: 10.5px / `0.24em` / uppercase / `muted` label, then the hairline, then optional count. **The label needs `white-space: nowrap; flex-shrink: 0`** or it wraps beside the flexible rule.

---

## Format step

Flex row, `gap: 20px`, wrapping.

**Info panel (left).** `width: 340px`, `flex-shrink: 0`, `border: 1px solid line`, `background: fill`, `padding: 18px 20px 20px`.

- Title: 16px / 700 / `accent`.
- **First** paragraph is the lead: 13.5px, `line-height: 1.55`, colour `ink`.
- **Every following** paragraph is a ruled row: `border-top: 1px solid hair`, `padding-top: 10px`, `margin-top: 10px`, 12px, `line-height: 1.7`, colour `body`.

That split is deliberate — the format descriptions are long, and as one prose block they were unreadable. One statement per ruled row scans.

**Format buttons (right).** `flex: 1`, `min-width: 260px`, stacked rows with `gap: 8px`; each row wraps with `gap: 8px`. The existing `moduleRows` grouping is preserved:

```
['knives','mob','circle'] / ['sob','roast'] / ['wisdom'] / ['sacrificer','executioner'] / ['test','discussion']
```

Button: 12px, `padding: 7px 13px`, `white-space: nowrap`, transparent background, `1px solid hair`, `ink` text.
**Selected:** `1px solid line`, `background: fill`, text stays `ink`.

## Fixtures

CSS grid, `repeat(auto-fill, minmax(262px, 1fr))`, `gap: 10px`. The 262px minimum is load-bearing — narrower and long names ("Professor Quirrell", "Lumpy Space Princess") clip. **Do not add `text-overflow: ellipsis`;** let names wrap.

Card (a `<button>`): flex row, `align-items: stretch`, `1px solid hair`, square.

- Names column: `padding: 11px 13px`, flex column, `gap: 4px`. Player A 12.5px / 700 / `ink`; player B 12.5px / 400 / `body`. `line-height: 1.35`.
- Score stub: right side, `border-left: 1px solid hair`, `padding: 11px 12px`, two lines right-aligned, 11px, `muted`, `font-variant-numeric: tabular-nums`. Hidden entirely when the fixture has no scores.
- **Selected:** border and the stub divider become `line`, background `fill`. Text colour does not change.
- `break_before` fixtures set `grid-column-start: 1` to force a new row (the existing `.fixture-grid-break` behaviour).

## Watch / Play panel

`1px solid hair`, `padding: 20px 22px`, flex column, `gap: 12px`. Background is a **very faint underlay** — `rgba(ink, 0.04)` in light, `rgba(paper, 0.04)` in dark. This is the only tinted surface on the page; keep it at or below 4% or it starts reading as a card.

- **Matchup line:** player names 21px / 700 / `ink`; `VS` in the small-caps label style at 11px; format suffix `— {format}` 12.5px `body` with `white-space: nowrap`.
- **Fixture description:** 12.5px, `body`, `max-width: 560px`, hidden when absent.
- **Cast chips**, flex wrap, `gap: 7px`:
  - *Live contestants (clickable seats)* — **light mode:** hard block border, `2px solid rgba(28,26,23,0.5)`, `padding: 3px 8px`, 11px / **700** / `ink`. **Dark mode:** plain `1px solid hair`, 400 weight, `body` text, `padding: 4px 9px`. The heavier treatment is light-mode only; dark paper doesn't need it.
  - *Your seat (selected)* — border and text become `line`, background `fill`.
  - *Eliminated players* — same chip at `opacity: 0.5`, `muted` text, not interactive, preceded by a 1px vertical `hair` divider (`align-self: stretch`, `margin: 0 5px`).
- **Seat hint** — 11.5px. Shown **only in play mode**: `pick a seat above` in `accent` until a seat is chosen, then `you play {name}` in `muted`. There is no "watching" line; watch mode shows nothing.
- **Footer row** — `border-top: 1px solid hair`, `padding-top: 12px`, flex, `gap: 14px`:
  - *Watch / Play switch*: two buttons inside one `1px solid hair` box, divided by a 1px left border, `padding: 7px 16px`, 11.5px, `0.06em`. Active segment: `accent` text on `tint`; inactive: `muted` on transparent.
  - *Run demo →*: `1px solid accent`, `accent` text, transparent background, `padding: 8px 18px`, 12.5px. **Disabled** (play mode with no seat picked): label changes to lowercase `pick a seat`, border `hair`, text `muted`, `cursor: default`. No error text — the label carries it.

## Completed game runs

Grid, `repeat(auto-fill, minmax(300px, 1fr))`, `gap: 12px`. Card: `1px solid hair`, `padding: 16px 18px`, flex column `gap: 8px` — name 14px/700 `ink`, description 12px/1.6 `body` (`flex: 1` so buttons align across cards), then two buttons: `Watch` (accent ghost) and `Copy link` (hair border, `muted`). `Copy link` swaps to `Copied` for 1.5s, unchanged from today.

## Footer

Hairline top rule. GitHub · Substack links left (12.5px, `body`, `rule` bottom border); "Demos run from fixed transcripts — no setup required." 11px `muted` right.

---

## Interaction notes

- Selecting a **fixture** resets mode to `watch` and clears the chosen seat (matches current `handleSelect`).
- Clicking a live cast chip sets mode to `play` and that seat in one action.
- Per-section selection state (`module`, `fixture`, `mode`, `seat`) is kept independently for Finales and Game modules, as today. Keep the existing `localStorage` persistence of module/fixture choices — the prototype omits it.
- Turnstile is not represented in the prototype. Slot the widget into the footer row before the Run demo button, and keep it gating `canStart`.
- Hover states: none beyond `cursor: pointer`. Consider adding a `tint`-only hover to fixture cards and format buttons in production. No lifts, no shadows.

## Responsive

Desktop-first, no breakpoints in the prototype. For production: the fixture and runs grids already reflow; below ~700px the format step should stack (info panel above the buttons, panel `width: 100%`); the hero drops to ~36px; the Watch/Play footer row wraps already.

## Deviations from the current page

1. **"watching — nobody is you" removed.** Watch mode shows no hint line at all.
2. **Format descriptions are split** into a lead line plus ruled rows (see *Format step*). No copy was rewritten, only the paragraph breaks are now structural.
3. The **`— Reunion Finale` suffix** and all small-caps sub-labels are `nowrap`; they wrapped mid-phrase otherwise.

## Open questions

1. Most game modules have no description — the info panel is nearly empty for them. Write one line each, or hide the panel when there's nothing to show?
2. `Test` and `Discussion Round Directed` look like development fixtures. Ship them?
3. Fixture cards show scores with no label. Does the user know what those numbers are?

## Files

| File | What it is |
|---|---|
| `Demos Teletype.dc.html` | The design. Open in a browser; toggle light/dark top-right. |
| `support.js` | Runtime needed to open the file. Not part of the design; do not port. |

Both must sit in the same folder. Cross-reference `design_handoff_lobby_teletype/README.md` for the full token and type documentation.
