"""
Generate an agent-state fixture JSON from a set of per-agent JSONL log files.

Usage:
    python -m runtime_tests.generate_fixture \\
        --files logs/Finn_20260521_103238.jsonl logs/Lumpy*.jsonl \\
        --output tests/fixtures/my_fixture.json \\
        [--include-empty BMO "Ice King" ...] \\
        [--demo-snippet]
"""
import argparse
import json
import os
import re
import sys


EMPTY_AGENT = {
    "persona": "",
    "speaking_style": "",
    "strategy": "",
    "math_assessment": "",
    "life_lessons": [],
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
    """Extract agent state from a rendered system prompt (see core/game_context/system_prompt.py)."""
    persona = _slice(system_prompt, "Persona: ", ["\nSpeaking Style:"])
    speaking_style = _slice(
        system_prompt, "Speaking Style: ", ["\n\n=== ", "\n=== "]
    )
    strategy = _slice(system_prompt, "Current Strategy: ", ["\nPosition Assessment:"])
    math_assessment = _slice(
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

    return {
        "persona": persona,
        "speaking_style": speaking_style,
        "strategy": strategy,
        "math_assessment": math_assessment,
        "life_lessons": life_lessons,
    }


def reconstruct_agent(lines: list) -> dict:
    lines = sorted(lines, key=lambda l: l["timestamp"])
    # Walk lines in reverse, per-field: first non-empty wins.
    # Eliminated agents lose the strategy/assessment section in their later prompts
    # (core/game_context/system_prompt.py:37), so we need to look further back for those.
    state = {"persona": "", "speaking_style": "", "strategy": "", "math_assessment": "", "life_lessons": []}
    for line in reversed(lines):
        parsed = parse_system_prompt(line["system_prompt"])
        for k, v in parsed.items():
            if not state[k] and v:
                state[k] = v
        if all(state[k] for k in ("persona", "speaking_style", "strategy", "math_assessment")) and state["life_lessons"]:
            break

    summary_lines = [
        l for l in lines if (l.get("response") or {}).get("brief_summary")
    ]
    state["summaries_brief"] = {
        str(i + 1): l["response"]["brief_summary"]
        for i, l in enumerate(summary_lines)
    }
    state["summaries_detailed"] = {
        str(i + 1): l["response"].get("public_response", "")
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
        fixture[name] = reconstruct_agent(lines)
        last_ts_by_agent[name] = max(l["timestamp"] for l in lines)

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
