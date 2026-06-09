import asyncio
import json
import threading
from dataclasses import dataclass

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.bootstrap import create_engine
from core.api_client import create_api_client
from core.sinks.websocket_sink import WebSocketSink
from core.levels.level_registry import get_level_by_id
from web import rate_limits
from web.server_config import GAME_ENABLED, TURNSTILE_ENABLED, MAX_NAME_LENGTH, MAX_PLAYERS
from web.server_helpers import (
    sanitize_name, verify_turnstile, log_game_start, _run_game_thread, _send_error, get_client_ip
)

router = APIRouter()


class GameRequestError(Exception):
    pass


@dataclass
class GameRequest:
    level: object
    human_name: str | None
    player_names: list


def _parse_game_request(msg) -> GameRequest:
    #just a simple clean up function - extracting the values from the request
    if msg.get("type") != "start":
        raise GameRequestError("Expected start message")

    level_id = msg.get("levelId")
    level = get_level_by_id(level_id)
    if not level:
        raise GameRequestError("Invalid level.")

    human_name = msg.get("human_name")
    human_name = human_name[:MAX_NAME_LENGTH] if human_name else None
    if human_name:
        human_name = sanitize_name(human_name)
    if human_name == "":
        raise GameRequestError("Invalid name.")

    names = msg.get("names", [])
    max_players = min(level.max_players, MAX_PLAYERS) - (1 if human_name else 0)
    player_names = [sanitize_name(n[:MAX_NAME_LENGTH]) for n in names[:max_players]]
    if any(not name for name in player_names):
        raise GameRequestError("Invalid name.")

    return GameRequest(level=level, human_name=human_name, player_names=player_names)


async def _can_run_game(websocket: WebSocket, token):
    if not GAME_ENABLED:
        await websocket.send_text(json.dumps({"type": "error", "message": "Game is not available yet."}))
        return False

    if TURNSTILE_ENABLED and not await verify_turnstile(token):
        await websocket.send_json({"type": "error", "message": "Verification failed"})
        return False

    if not await rate_limits.check_token_cap(websocket):
        return False

    if not await rate_limits.daily_and_concurrency_check(websocket, "game"):
        return False

    return True


@router.websocket("/ws/game")
async def game_ws(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    msg = json.loads(data)

    try:
        req = _parse_game_request(msg)
    except GameRequestError as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        return

    turnstile_token = msg.get("turnstile_token")
    ip_address = get_client_ip(websocket)

    if not await _can_run_game(websocket, turnstile_token):
        await websocket.close()
        return

    loop = asyncio.get_event_loop()
    sink = None
    api_client = None

    try:
        sink = WebSocketSink(websocket, loop)
        api_client = create_api_client(sink, token_budget=req.level.token_budget)

        def run_game():
            try:
                engine = create_engine(sink, names=req.player_names, game_design=req.level.game_design, api_client=api_client)
                engine.run(human_player_name=req.human_name)
            except Exception as e:
                _send_error(websocket, loop, e)

        thread = threading.Thread(target=run_game, daemon=True)
        thread.start()

        log_game_start(is_game=True, id=req.level.id, player_names=req.player_names,
                       human_name=req.human_name, ip_address=ip_address, token_budget=req.level.token_budget)

        await _run_game_thread(thread, api_client, websocket, sink)

    except WebSocketDisconnect:
        if sink: sink.on_disconnect()
    finally:
        rate_limits.release_slot(api_client)
