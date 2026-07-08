"""
Generate an agent-state fixture JSON from a set of per-agent JSONL log files.

Usage:
    python -m demo_runner.fixture_generation.generate_fixture \\
        --files logs/Finn_20260521_103238.jsonl logs/Lumpy*.jsonl \\
        --output demo_runner/fixtures/my_fixture.json \\
        [--include-empty BMO "Ice King" ...] \\
        [--demo-snippet]
"""
import argparse
import json
import os
import re
import sys


EMPTY_AGENT = {
    "initial_persona": "",
    "additional_persona_coloring": "",
    "persona_unique_detail": "",
    "initial_speaking_style": "",
    "speaking_style_update": "",
    "strategy": "",
    "character_strategy": "",
    "position_assessment": "",
    "life_lessons": [],
    "character_dictionary": {},
    "summaries_brief": {},
    "summaries_detailed": {},
}


def _slice(text: str, start_marker: str, end_markers: list) -> str:
    i = text.find(start_marker)
    if i == -1:
        return ""
    i += len(start_marker)
    end = len(text)
    for m in end_markers:
        j = text.find(m, i)
        if j != -1:
            end = min(end, j)
    return text[i:end].strip()


def parse_system_prompt(system_prompt: str) -> dict:
    """Extract agent state from a rendered system prompt (see core/game_context/system_content.py)."""
    initial_persona = _slice(system_prompt, "Core Persona: ", ["\nAdditional Persona Coloring:", "\nUnique persona detail:", "\n\nCore Speaking Style:"])
    additional_persona_coloring = _slice(system_prompt, "\nAdditional Persona Coloring: ", ["\nUnique persona detail:", "\n\nCore Speaking Style:"])
    persona_unique_detail = _slice(system_prompt, "\nUnique persona detail: ", ["\n\nCore Speaking Style:"])
    initial_speaking_style = _slice(system_prompt, "Core Speaking Style: ", ["\nSpeaking Style Additional Consideration:", "\n\n=== ", "\n=== "])
    speaking_style_update = _slice(system_prompt, "\nSpeaking Style Additional Consideration: ", ["\n\n=== ", "\n=== "])
    strategy = _slice(system_prompt, "Current Strategy: ", ["\nCharacter Strategy:", "\nPosition Assessment:"])
    character_strategy = _slice(system_prompt, "\nCharacter Strategy: ", ["\nPosition Assessment:"])
    position_assessment = _slice(
        system_prompt,
        "Position Assessment: ",
        ["\n\nCurrent round strategy:", "\n\n=== ", "\n=== ", "\n\n"],
    )

    lessons_block = _slice(
        system_prompt,
        "Use these past learnings to guide your current behavior:\n",
        ["\n\n=== ", "\n\n"],
    )
    life_lessons = []
    if lessons_block and "None yet" not in lessons_block:
        for line in lessons_block.splitlines():
            line = line.strip()
            if line.startswith("- "):
                life_lessons.append(line[2:].strip())
    life_lessons = life_lessons[-8:]

    impressions_block = _slice(system_prompt, "=== CHARACTER IMPRESSIONS ===\n", ["\n\n=== ", "\n=== "])
    character_dictionary = {}
    if impressions_block and "No impressions yet" not in impressions_block:
        for line in impressions_block.splitlines():
            line = line.strip()
            if line.startswith("- ") and ": " in line:
                name, impression = line[2:].split(": ", 1)
                character_dictionary[f"impression_{name.strip()}"] = impression.strip()

    return {
        "initial_persona": initial_persona,
        "additional_persona_coloring": additional_persona_coloring,
        "persona_unique_detail": persona_unique_detail,
        "initial_speaking_style": initial_speaking_style,
        "speaking_style_update": speaking_style_update,
        "strategy": strategy,
        "character_strategy": character_strategy,
        "position_assessment": position_assessment,
        "life_lessons": life_lessons,
        "character_dictionary": character_dictionary,
    }


def truncate_to_phase_start(lines: list, phase: int) -> list:
    """Return lines through the FIRST turn after the (phase-1)th summary.

    Summary turns (response.brief_summary present) mark phase ends, since the logs
    don't record phase_number. To reconstruct state as an agent *entered* phase N,
    we keep everything through their (N-1)th summary PLUS the first turn after it.

    That trailing turn is essential: the summary turn's own evolution fields
    (compressed_life_lessons, persona_unique_detail, speaking_style_update, ...) are
    applied AFTER it responds, so they only appear in the *next* turn's system_prompt
    (agents/player.py process_evolution_fields / _process_summary_turn). Cutting at
    the summary turn itself would capture the PRE-compression state (e.g. 8 lessons
    instead of the compressed 3). This yields summaries 1..N-1 and the post-summary
    live state the agent actually entered phase N with.
    """
    lines = sorted(lines, key=lambda l: l["timestamp"])
    summaries_needed = phase - 1
    if summaries_needed <= 0:
        return []
    seen = 0
    for i, l in enumerate(lines):
        if (l.get("response") or {}).get("brief_summary"):
            seen += 1
            if seen == summaries_needed:
                # keep the summary turn AND the first turn after it (if any)
                return lines[: i + 2]
    # Fewer than N-1 summaries exist (agent eliminated before phase N); keep all.
    return lines


def reconstruct_agent(lines: list) -> dict:
    lines = sorted(lines, key=lambda l: l["timestamp"])
    # Walk lines in reverse, per-field: first non-empty wins.
    # Eliminated agents lose the strategy/assessment section in their later prompts
    # (core/game_context/system_content.py:37), so we need to look further back for those.
    state = {"initial_persona": "", "additional_persona_coloring": "", "persona_unique_detail": "",
             "initial_speaking_style": "", "speaking_style_update": "",
             "strategy": "", "character_strategy": "", "position_assessment": "",
             "life_lessons": [], "character_dictionary": {}}
    for line in reversed(lines):
        parsed = parse_system_prompt(line["system_prompt"])
        for k, v in parsed.items():
            if k == "character_dictionary":
                if not state[k] and v:
                    state[k] = v
            elif not state[k] and v:
                state[k] = v
        if all(state[k] for k in ("initial_persona", "initial_speaking_style", "strategy", "position_assessment")) and state["life_lessons"]:
            break

    summary_lines = [
        l for l in lines if (l.get("response") or {}).get("brief_summary")
    ]
    state["summaries_brief"] = {
        str(i + 1): l["response"]["brief_summary"]
        for i, l in enumerate(summary_lines)
    }
    state["summaries_detailed"] = {
        str(i + 1): l["response"].get("personal_detailed_phase_summary", "")
        for i, l in enumerate(summary_lines)
    }
    return state


def load_jsonl(path: str) -> list:
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--files", nargs="+", required=True, help="JSONL log files for one game session")
    ap.add_argument("--output", required=True, help="Path to write the fixture JSON")
    ap.add_argument("--include-empty", nargs="*", default=[], help="Agent names to add as empty-state entries (eliminated/jury)")
    ap.add_argument("--phase", type=int, default=None, help="Reconstruct state as agents ENTERED this phase (keeps summaries 1..phase-1). Omit for final state.")
    ap.add_argument("--demo-snippet", action="store_true", help="Print a suggested demo_runner block to stderr")
    args = ap.parse_args()

    by_agent: dict = {}
    for path in args.files:
        for entry in load_jsonl(path):
            name = entry.get("agent")
            if not name:
                continue
            by_agent.setdefault(name, []).append(entry)

    fixture = {}
    last_ts_by_agent = {}
    for name, lines in by_agent.items():
        last_ts_by_agent[name] = max(l["timestamp"] for l in lines)
        if args.phase is not None:
            lines = truncate_to_phase_start(lines, args.phase)
            if not lines:
                print(f"WARNING: {name} has no turns before phase {args.phase}; skipping", file=sys.stderr)
                continue
        fixture[name] = reconstruct_agent(lines)

    for name in args.include_empty:
        if name not in fixture:
            fixture[name] = dict(EMPTY_AGENT, life_lessons=[], summaries_brief={}, summaries_detailed={})

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(fixture, f, indent=2, ensure_ascii=False)
    print(f"Wrote {args.output} ({len(fixture)} agents)")

    if args.demo_snippet:
        max_phase = max(
            (len(fixture[n]["summaries_brief"]) for n in fixture if fixture[n]["summaries_brief"]),
            default=0,
        )
        elim_order = sorted(last_ts_by_agent, key=last_ts_by_agent.get)
        if len(elim_order) >= 2:
            elim_order = elim_order[:-2]
        snippet = (
            "\n# Suggested demo_runner entry (verify before pasting):\n"
            "{\n"
            f"    \"fixture_filename\": \"{os.path.basename(args.output)}\",\n"
            "    \"finalist_scores\": {},  # FILL IN\n"
            f"    \"elimination_order\": {elim_order!r},\n"
            f"    \"phase_number\": {max_phase + 1 if max_phase else None},\n"
            "}\n"
        )
        print(snippet, file=sys.stderr)


if __name__ == "__main__":
    main()
