# persona-tools — an MCP server

A small [Model Context Protocol](https://modelcontextprotocol.io) server that
lets an LLM host inspect this project's character logs on its own, instead of a
human pasting log files into a chat.

## What it exposes

Demonstrates both core MCP primitives — **tools** (the model calls them) and a
**resource** (the host reads it by URI).

| Kind | Name | Purpose |
|------|------|---------|
| Tool | `list_logged_agents` | Discover which agent names have logs available. |
| Tool | `persona_drift` | Diff an agent's system prompt from their first API call to their latest — shows how persona/strategy drifted over a game. |
| Tool | `mood_timeline` | Track an agent's `Mood at last turn` across every call — works on a live, in-progress game. |
| Resource | `persona://{agent_name}/latest` | Full latest character log as browsable text — read-only data the host pulls in, not a function the model calls. |

## Design

- **`core.py`** — pure, testable log logic. No MCP imports. Runs as a plain script.
- **`server.py`** — the thin MCP wrapper: `@mcp.tool()` advertises each function; `mcp.run()` serves it over stdio.

The separation is the point: MCP is a *transport* over existing logic, not a
rewrite of it. Tool **docstrings** and **return type annotations** matter —
they are the interface the model reads to decide when to call a tool and how to
parse the result (typed returns yield structured results; a bare `dict` comes
back as JSON text).

## Run standalone

```bash
uv run python -m mcp_service.server
```

## Register with Claude Code

Already wired via `.mcp.json` at the repo root. Equivalent CLI:

```bash
claude mcp add persona-tools --scope project -- uv run python -m mcp_service.server
```

Then in a session, ask e.g. *"how did Aang's persona drift this game?"* and the
model calls `persona_drift` itself.
