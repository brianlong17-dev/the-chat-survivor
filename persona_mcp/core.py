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


def diff_system_prompts(first_prompt: str, last_prompt: str) -> str:
    """Unified diff between two system prompts."""
    return "".join(
        difflib.unified_diff(
            first_prompt.splitlines(keepends=True),
            last_prompt.splitlines(keepends=True),
            fromfile="first_call_system_prompt",
            tofile="latest_call_system_prompt",
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
