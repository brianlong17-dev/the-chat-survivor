import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import date

from fastapi import WebSocket

from web.server_config import (DAILY_DEMO_CAP, DAILY_GAME_CAP, DAILY_TOKEN_CAP,
    MAX_CONCURRENT_GAMES, RATE_LIMITS_DB_PATH,
)

_db_lock = threading.Lock()

# Concurrency is live-connection state — a crash drops the sockets too, so this
# correctly resets on restart and does not need to be persisted.
_active_games = 0
_active_games_lock = threading.Lock()


def _init_db() -> None:
    db_dir = os.path.dirname(RATE_LIMITS_DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_counts (
                date TEXT PRIMARY KEY,
                games INTEGER NOT NULL DEFAULT 0,
                demos INTEGER NOT NULL DEFAULT 0,
                tokens INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


@contextmanager
def _connect():
    conn = sqlite3.connect(RATE_LIMITS_DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def _ensure_today(conn) -> str:
    today = date.today().isoformat()
    conn.execute(
        "INSERT OR IGNORE INTO daily_counts(date, games, demos, tokens) VALUES (?, 0, 0, 0)",
        (today,),
    )
    return today


def _read_today() -> tuple[str, int, int, int]:
    with _db_lock, _connect() as conn:
        today = _ensure_today(conn)
        conn.commit()
        row = conn.execute(
            "SELECT games, demos, tokens FROM daily_counts WHERE date=?",
            (today,),
        ).fetchone()
        return today, row[0], row[1], row[2]

async def daily_and_concurrency_check(websocket: WebSocket, kind: str) -> bool:
    if not await check_concurrency_and_get_slot(websocket):
        return False
    if not await check_and_increment_daily(websocket, kind):
        release_unused_slot()
        return False
    return True

async def check_and_increment_daily(websocket: WebSocket, kind: str) -> bool:
    column = "games" if kind == "game" else "demos"
    cap = DAILY_GAME_CAP if kind == "game" else DAILY_DEMO_CAP
    with _db_lock, _connect() as conn:
        today = _ensure_today(conn)
        current = conn.execute(
            f"SELECT {column} FROM daily_counts WHERE date=?", (today,)
        ).fetchone()[0]
        if cap > current: 
            conn.execute(
                f"UPDATE daily_counts SET {column} = {column} + 1 WHERE date=?",
                (today,),
            )
            conn.commit()
            return True
    await websocket.send_text(json.dumps({"type": "error", "message": f"Daily {kind} limit reached. Come back tomorrow."}))
    return False


async def check_concurrency_and_get_slot(websocket: WebSocket) -> bool:
    global _active_games
    with _active_games_lock:
        if _active_games < MAX_CONCURRENT_GAMES:
            _active_games += 1
            return True 
    await websocket.send_text(json.dumps({"type": "error", "message": 
        f"Server is at capacity ({MAX_CONCURRENT_GAMES} active games). Try again soon."}))
    return False
                


async def check_token_cap(websocket: WebSocket) -> bool:
    _, _, _, tokens = _read_today()
    if tokens >= DAILY_TOKEN_CAP:
        await websocket.send_text(json.dumps({"type": "error", "message": "Daily token limit reached. Come back tomorrow."}))
        return False
    return True



def record_token_usage(api_client) -> None:
    if api_client is None:
        return
    total = api_client.usage_totals().get("total", 0)
    if total <= 0:
        return
    with _db_lock, _connect() as conn:
        today = _ensure_today(conn)
        conn.execute(
            "UPDATE daily_counts SET tokens = tokens + ? WHERE date=?",
            (total, today),
        )
        conn.commit()


def release_slot(api_client) -> None:
    global _active_games
    record_token_usage(api_client)
    with _active_games_lock:
        _active_games -= 1
        
def release_unused_slot() -> None:
    global _active_games
    with _active_games_lock:
        _active_games -= 1

def snapshot() -> dict:
    today, games, demos, tokens = _read_today()
    return {
        "date": today,
        "games_today": games,
        "game_cap": DAILY_GAME_CAP,
        "games_remaining": max(0, DAILY_GAME_CAP - games),
        "demos_today": demos,
        "demo_cap": DAILY_DEMO_CAP,
        "demos_remaining": max(0, DAILY_DEMO_CAP - demos),
        "tokens_today": tokens,
        "token_cap": DAILY_TOKEN_CAP,
        "tokens_remaining": max(0, DAILY_TOKEN_CAP - tokens),
        "active_games": _active_games,
        "max_concurrent": MAX_CONCURRENT_GAMES,
    }


_init_db()
