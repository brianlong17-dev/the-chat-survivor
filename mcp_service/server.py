"""MCP server exposing character-log inspection tools.

Run standalone (stdio transport):
    uv run python -m mcp_service.server

Register with Claude Code:
    claude mcp add persona-tools -- uv run python -m mcp_service.server

The docstrings below are the interface the model reads to decide when and how
to call each tool — they describe *when to use this*, not just what it does.
"""
from mcp.server.fastmcp import FastMCP

from mcp_service.core import (
    DEFAULT_LOG_DIR,
    MASTER_LOG_DIR,
    MoodTimeline,
    PersonaDiff,
    character_usage_counts,
    get_api_summary_log,
    get_daily_token_log,
    get_latest_log_text,
    get_master_game_log,
    get_mood_timeline,
    get_persona_diff,
    list_agents,
)

mcp = FastMCP("persona-tools")


@mcp.tool()
def persona_drift(agent_name: str, log_dir: str = DEFAULT_LOG_DIR) -> PersonaDiff:
    """Show how an agent's system prompt evolved during a game.

    Use this to see how a character's persona, strategy, or life-lessons drifted
    from their first API call to their most recent one. Returns a unified diff of
    the system prompt plus call counts. Call `list_agents` first if you don't
    know the exact agent name.
    """
    return get_persona_diff(agent_name, log_dir)


@mcp.tool()
def list_logged_agents(log_dir: str = DEFAULT_LOG_DIR) -> list[str]:
    """List every agent name that has a character log available to inspect.

    Use this to discover valid inputs for `persona_drift`.
    """
    return list_agents(log_dir)


@mcp.tool()
def mood_timeline(agent_name: str, log_dir: str = DEFAULT_LOG_DIR) -> MoodTimeline:
    """Track how an agent's mood shifts across their latest game, turn by turn.

    Returns the 'Mood at last turn' read for every call. Use this to watch a
    character's affect evolve during a game (including one still in progress).
    Call `list_logged_agents` first if unsure of the exact name.
    """
    return get_mood_timeline(agent_name, log_dir)


@mcp.tool()
def master_game_log(limit: int = 50, log_dir: str = MASTER_LOG_DIR) -> dict:
    """Return the most recent entries from the master game event log.

    Each entry is a raw event (e.g. game_start) with fields like game_id,
    level_id, player_names, token_budget, and time. Use this for a ground-truth
    view of recent game activity, not a summarized one.
    """
    return get_master_game_log(limit, log_dir)


@mcp.tool()
def most_used_characters(top_n: int = 15, log_dir: str = MASTER_LOG_DIR) -> dict:
    """Return how many games each character has appeared in, across the whole
    master game log — ranked most to least used.

    Use this for "most/least used character" questions. This scans every
    game_start event in the log, not just the recent ones.
    """
    return character_usage_counts(top_n, log_dir)


@mcp.tool()
def api_summary_log(limit: int = 50, log_dir: str = MASTER_LOG_DIR) -> dict:
    """Return the most recent per-game API usage summaries.

    Each entry covers one finished game: total_calls, total_input_tokens,
    total_output_tokens, total_thinking_tokens, and api_total_tokens. Use this
    for per-game cost breakdowns rather than a daily rollup.
    """
    return get_api_summary_log(limit, log_dir)


@mcp.tool()
def daily_token_log(days: int = 30, log_dir: str = MASTER_LOG_DIR) -> dict:
    """Return the most recent daily token-usage rollups.

    Each entry covers one calendar date: games, demos, and total tokens spent
    that day. Use this to spot daily spend trends, not per-game detail.
    """
    return get_daily_token_log(days, log_dir)


@mcp.resource("persona://{agent_name}/latest")
def latest_log(agent_name: str) -> str:
    """The full latest character log for an agent, as browsable text.

    A resource (read-only data the host can pull in), not a tool — the host
    reads it by URI, e.g. persona://Aang/latest, rather than the model calling it.
    """
    return get_latest_log_text(agent_name)


if __name__ == "__main__":
    mcp.run()
