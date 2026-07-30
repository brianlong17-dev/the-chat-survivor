"""Pure log-inspection logic. No MCP here — this is plain, testable Python.

Character logs are JSONL, one API call per line, named:
    {AgentName}_{YYYYMMDD}_{HHMMSS}_{hash}.jsonl
Each line has keys: call, timestamp, agent, model, system_prompt, user_prompt,
field_prompts, response.
"""
import glob
import json
import os
import re
import difflib
from typing import TypedDict

DEFAULT_LOG_DIR = "logs/characterlogs"
MASTER_LOG_DIR = "logs/master_logs"
GAME_LOG_DIR = "logs/gamelogs"


class PersonaDiff(TypedDict):
    agent: str
    log_file: str
    num_calls: int
    first_call: int | None
    last_call: int | None
    diff: str | None
    note: str | None


def find_latest_log(agent_name: str, log_dir: str) -> str:
    """Return the newest log file for an agent (filenames sort by timestamp)."""
    matches = sorted(glob.glob(os.path.join(log_dir, f"{agent_name}_*.jsonl")))
    if not matches:
        raise FileNotFoundError(
            f"No log files found for agent '{agent_name}' in {log_dir}"
        )
    return matches[-1]


def load_calls(log_path: str) -> list[dict]:
    """Load every call record from a JSONL log file."""
    with open(log_path) as f:
        return [json.loads(line) for line in f if line.strip()]


def diff_system_prompts(
    first_prompt: str,
    last_prompt: str,
    fromfile: str = "first_call_system_prompt",
    tofile: str = "latest_call_system_prompt",
) -> str:
    """Unified diff between two system prompts."""
    return "".join(
        difflib.unified_diff(
            first_prompt.splitlines(keepends=True),
            last_prompt.splitlines(keepends=True),
            fromfile=fromfile,
            tofile=tofile,
            lineterm="",
        )
    )


def get_persona_diff(agent_name: str, log_dir: str = DEFAULT_LOG_DIR) -> PersonaDiff:
    """Find an agent's latest log and diff their first vs. last system_prompt."""
    log_path = find_latest_log(agent_name, log_dir)
    calls = load_calls(log_path)

    if len(calls) < 2:
        return PersonaDiff(
            agent=agent_name,
            log_file=os.path.basename(log_path),
            num_calls=len(calls),
            first_call=None,
            last_call=None,
            diff=None,
            note="Only one call in this log — nothing to diff yet.",
        )

    diff_text = diff_system_prompts(
        calls[0]["system_prompt"], calls[-1]["system_prompt"]
    )
    return PersonaDiff(
        agent=agent_name,
        log_file=os.path.basename(log_path),
        num_calls=len(calls),
        first_call=calls[0]["call"],
        last_call=calls[-1]["call"],
        diff=diff_text or "(no differences — system_prompt identical)",
        note=None,
    )


class SystemPrompts(TypedDict):
    agent: str
    log_file: str
    num_calls: int
    prompts: list[dict]


class SystemPromptDiffs(TypedDict):
    agent: str
    log_file: str
    num_calls: int
    steps: list[dict]


def get_system_prompts_diffs(
    agent_name: str,
    log_dir: str = DEFAULT_LOG_DIR,
    first: int | None = None,
    last: int | None = None,
) -> SystemPromptDiffs:
    """Diff each call's system_prompt against the previous call in the range.

    Where get_persona_diff compares only first vs. last, this walks the whole
    range turn by turn: the first step in the range holds the full baseline
    prompt, and every later step holds a unified diff against the call before
    it — so you can pinpoint the exact turn a life lesson or persona line first
    appeared. `first`/`last` are inclusive call numbers; omit for all calls."""
    result = get_system_prompts(agent_name, log_dir, first, last)
    prompts = result["prompts"]
    steps: list[dict] = []
    for i, p in enumerate(prompts):
        if i == 0:
            steps.append({"call": p["call"], "baseline": p["system_prompt"]})
        else:
            steps.append({
                "call": p["call"],
                "prev_call": prompts[i - 1]["call"],
                "diff": diff_system_prompts(
                    prompts[i - 1]["system_prompt"],
                    p["system_prompt"],
                    fromfile=f"call_{prompts[i - 1]['call']}",
                    tofile=f"call_{p['call']}",
                ) or "(no change from previous call)",
            })
    return SystemPromptDiffs(
        agent=agent_name,
        log_file=result["log_file"],
        num_calls=result["num_calls"],
        steps=steps,
    )


def get_system_prompts(
    agent_name: str,
    log_dir: str = DEFAULT_LOG_DIR,
    first: int | None = None,
    last: int | None = None,
) -> SystemPrompts:
    """Return the full system_prompt for each call in an agent's latest log.

    Unlike get_persona_diff (first-vs-last diff), this pulls every prompt
    verbatim so you can inspect any single turn. `first`/`last` bound the call
    range (inclusive, by the call number in the log); omit them for all calls."""
    log_path = find_latest_log(agent_name, log_dir)
    calls = load_calls(log_path)
    prompts = [
        {"call": c["call"], "system_prompt": c["system_prompt"]}
        for c in calls
        if (first is None or c["call"] >= first)
        and (last is None or c["call"] <= last)
    ]
    return SystemPrompts(
        agent=agent_name,
        log_file=os.path.basename(log_path),
        num_calls=len(calls),
        prompts=prompts,
    )


_MOOD_RE = re.compile(r"(?:Mood|Inner Feeling|Emotional State)\s*(.+)")


class MoodTimeline(TypedDict):
    agent: str
    log_file: str
    num_calls: int
    moods: list[dict]


def get_mood_timeline(agent_name: str, log_dir: str = DEFAULT_LOG_DIR) -> MoodTimeline:
    """Extract the 'Mood at last turn' line from each call in an agent's latest log.

    Mood is a lagging read (the mood coming out of the prior turn). Calls with no
    mood line (e.g. the opening turn) are reported as None."""
    log_path = find_latest_log(agent_name, log_dir)
    calls = load_calls(log_path)
    moods = []
    for c in calls:
        m = _MOOD_RE.search(c["system_prompt"])
        moods.append({"call": c["call"], "mood": m.group(1).strip() if m else None})
    return MoodTimeline(
        agent=agent_name,
        log_file=os.path.basename(log_path),
        num_calls=len(calls),
        moods=moods,
    )

def get_master_game_log(limit: int = 50, log_dir: str = MASTER_LOG_DIR) -> dict:
    """Return the most recent entries from the master game event log.

    Each entry is a raw event (e.g. game_start) with fields like game_id,
    level_id, player_names, token_budget, and time. Use this for a ground-truth
    view of recent game activity, not a summarized one."""
    log_path = os.path.join(log_dir, "master_game_log")
    events = load_calls(log_path)
    return {
        "log_file": os.path.basename(log_path),
        "total_events": len(events),
        "recent": events[-limit:],
    }


def character_usage_counts(top_n: int = 15, log_dir: str = MASTER_LOG_DIR) -> dict:
    """Return how many games each character has appeared in, across the whole
    master game log — ranked most to least used.

    Use this for "most/least used character" questions. This scans every
    game_start event in the log, not just the recent ones."""
    log_path = os.path.join(log_dir, "master_game_log")
    events = load_calls(log_path)
    counts: dict[str, int] = {}
    for e in events:
        if e.get("event") != "game_start":
            continue
        for name in e.get("player_names") or []:
            counts[name] = counts.get(name, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return {
        "log_file": os.path.basename(log_path),
        "total_distinct_characters": len(counts),
        "top": [{"character": name, "games": n} for name, n in ranked[:top_n]],
    }


def get_api_summary_log(limit: int = 50, log_dir: str = MASTER_LOG_DIR) -> dict:
    """Return the most recent per-game API usage summaries.

    Each entry covers one finished game: total_calls, total_input_tokens,
    total_output_tokens, total_thinking_tokens, and api_total_tokens. Use this
    for per-game cost breakdowns rather than a daily rollup."""
    log_path = os.path.join(log_dir, "api_summary_log")
    entries = load_calls(log_path)
    return {
        "log_file": os.path.basename(log_path),
        "total_entries": len(entries),
        "recent": entries[-limit:],
    }


def get_daily_token_log(days: int = 30, log_dir: str = MASTER_LOG_DIR) -> dict:
    """Return the most recent daily token-usage rollups.

    Each entry covers one calendar date: games, demos, and total tokens spent
    that day. Use this to spot daily spend trends, not per-game detail."""
    log_path = os.path.join(log_dir, "daily_token_log")
    entries = load_calls(log_path)
    return {
        "log_file": os.path.basename(log_path),
        "total_entries": len(entries),
        "recent": entries[-days:],
    }


def get_latest_log_text(agent_name: str, log_dir: str = DEFAULT_LOG_DIR) -> str:
    """Return a readable dump of an agent's latest log: one section per call
    with the model, user prompt, and response. Intended as browsable content,
    not a machine-parsed result."""
    log_path = find_latest_log(agent_name, log_dir)
    calls = load_calls(log_path)
    lines = [f"# {agent_name} — {os.path.basename(log_path)} ({len(calls)} calls)", ""]
    for c in calls:
        lines.append(f"## call {c['call']}  [{c.get('model', '?')}]  {c.get('timestamp', '')}")
        lines.append(f"user_prompt:\n{c.get('user_prompt', '')}")
        lines.append(f"response:\n{c.get('response', '')}")
        lines.append("")
    return "\n".join(lines)


def list_agents(log_dir: str = DEFAULT_LOG_DIR) -> list[str]:
    """List distinct agent names that have logs in log_dir."""
    names = set()
    for path in glob.glob(os.path.join(log_dir, "*.jsonl")):
        base = os.path.basename(path)
        names.add(base.rsplit("_", 3)[0])
    return sorted(n for n in names if n)


def list_game_logs(limit: int = 20, log_dir: str = GAME_LOG_DIR) -> list[dict]:
    """List the most recent full game-event logs (one file per played game or
    demo), newest first. Each file is the raw event tape the frontend received
    over the websocket. Use `log_file` from here with `get_game_log_text`."""
    files = sorted(glob.glob(os.path.join(log_dir, "game_*.jsonl")))
    return [
        {"log_file": os.path.basename(f), "size_bytes": os.path.getsize(f)}
        for f in reversed(files[-limit:])
    ]


def _resolve_game_log(log_file: str, log_dir: str) -> str:
    if log_file:
        safe = os.path.basename(log_file)
        path = os.path.join(log_dir, safe)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"No game log '{log_file}' in {log_dir}")
        return path
    files = sorted(glob.glob(os.path.join(log_dir, "game_*.jsonl")))
    if not files:
        raise FileNotFoundError(f"No game logs found in {log_dir}")
    return files[-1]


# Event types that carry no narrative content worth surfacing in a transcript.
_GAME_LOG_NOISE_TYPES = {
    "linebreak", "loading", "loading_done", "delay", "cast", "set_segments",
    "feed_marker", "widget_update", "input_request", "next_round_request",
    "inner_workings", "phase_intro", "phase_rounds", "phase_round_index",
}

# Event types kept when public_only=True: the feed a viewer actually sees,
# plus enough structure (phase/round/host markers) to follow along.
_PUBLIC_EVENT_TYPES = {
    "game_intro", "phase_header", "round_start", "round_summary",
    "public_action", "system_public", "game_over",
}


def _render_game_log_event(e: dict) -> str | None:
    t = e.get("type")
    if t == "game_intro":
        return f"[INTRO] {e.get('message', '')}"
    if t == "phase_header":
        return f"\n=== Phase {e.get('phase_number')} ==="
    if t == "round_start":
        return f"\n--- Round {e.get('round_number')} --- (scores: {e.get('scores', '')})"
    if t == "round_summary":
        return f"[ROUND SUMMARY] {e.get('summary', '')}"
    if t == "public_action":
        speaker = e.get("speaker", "?")
        message = e.get("message", "")
        target = e.get("directed_to_name")
        return f"{speaker} -> {target}: {message}" if target else f"{speaker}: {message}"
    if t == "private_thought":
        return f"  ({e.get('speaker', '?')} thinks: {e.get('message', '')})"
    if t == "private_conversation":
        participants = ", ".join(e.get("participants", []))
        body = "\n".join(
            f"  {m.get('speaker')}: {m.get('message')}" for m in e.get("messages", [])
        )
        return f"[PRIVATE — {participants}]\n{body}"
    if t == "system_public":
        return f"[HOST] {e.get('message', '')}"
    if t == "system_private":
        return f"[HOST-PRIVATE] {e.get('message', '')}"
    if t == "points_update":
        return f"[SCORES] {e.get('scores')}"
    if t == "evicted_update":
        return f"[EVICTED] {', '.join(e.get('evicted_names', []))}"
    if t == "warning":
        return f"[WARNING] {e.get('message', '')}"
    if t == "game_over":
        return f"\n=== GAME OVER — winners: {', '.join(e.get('winners', []))} ==="
    if t in _GAME_LOG_NOISE_TYPES:
        return None
    return f"[{t}] {json.dumps({k: v for k, v in e.items() if k != 'type'}, ensure_ascii=False)}"


def get_game_log_text(
    log_file: str = "",
    log_dir: str = GAME_LOG_DIR,
    public_only: bool = True,
    include_round_summary: bool = False,
) -> str:
    """Return a readable transcript of one full game as it was played on the
    deployed site, in chronological order.

    With public_only=True (the default): just what a viewer saw — host intros,
    round/phase markers, and "speaker: message" for every public line, plus
    the final outcome. This is almost always what you want for "what happened
    in this game". With public_only=False: also includes private thoughts,
    private conversations, evictions, and score payloads for deeper debugging.

    Round summaries (the host's behind-the-scenes recap of each round) are
    left out by default since they restate what the messages already show —
    pass include_round_summary=True to bring them back.

    Leave `log_file` empty for the most recently played game, or pass a
    filename from `list_game_logs`."""
    path = _resolve_game_log(log_file, log_dir)
    events = load_calls(path)
    lines = [f"# {os.path.basename(path)} ({len(events)} events)", ""]
    for e in events:
        t = e.get("type")
        if public_only and t not in _PUBLIC_EVENT_TYPES:
            continue
        if t == "round_summary" and not include_round_summary:
            continue
        rendered = _render_game_log_event(e)
        if rendered is not None:
            lines.append(rendered)
    return "\n".join(lines)
