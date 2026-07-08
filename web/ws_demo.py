import asyncio
import json
import threading

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.api_client import create_api_client
from core.sinks.websocket_sink import WebSocketSink
from demo_runner.demo_runner import run_from_frontend
from demo_runner.game_module_directory import MODULE_MAP
from web import rate_limits
from web.server_config import DEMO_ENABLED, TURNSTILE_ENABLED, MAX_NAME_LENGTH, DEMO_TOKEN_BUDGET
from web.server_helpers import (
    sanitize_name, verify_turnstile, log_game_start, _run_game_thread, _send_error, get_client_ip
)

router = APIRouter()


async def _can_run_demo(websocket: WebSocket, demo_id, token):
    if not DEMO_ENABLED:
        await websocket.send_text(json.dumps({"type": "error", "message": "Demo is not available yet."}))
        return False

    if TURNSTILE_ENABLED and not await verify_turnstile(token):
        await websocket.send_json({"type": "error", "message": "Verification failed"})
        return False

    LOCKED_DEMOS = {}
    if demo_id in LOCKED_DEMOS:
        await websocket.send_text(json.dumps({"type": "error", "message": "This demo is not available yet."}))
        return False

    if not await rate_limits.check_token_cap(websocket):
        return False

    if not await rate_limits.daily_and_concurrency_check(websocket, "demo", get_client_ip(websocket)):
        return False

    return True


@router.websocket("/ws/demo")
async def demo_ws(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    msg = json.loads(data)
    demo_id = msg.get("demo_id")
    turnstile_token = msg.get("turnstile_token")
    

    if not demo_id in MODULE_MAP:
        await websocket.send_text(json.dumps({"type": "error", "message": f"Unknown demo: {demo_id}"}))
        return

    human_name = msg["human_name"][:MAX_NAME_LENGTH] if msg.get("human_name") else None
    if human_name:
        human_name = sanitize_name(human_name)
    if human_name == "":
        await websocket.send_text(json.dumps({"type": "error", "message": "Invalid name."}))
        return

    if not await _can_run_demo(websocket, demo_id, turnstile_token):
        await websocket.close()
        return

    loop = asyncio.get_event_loop()
    sink = None
    api_client = None

    try:
        sink = WebSocketSink(websocket, loop)
        api_client = create_api_client(sink, token_budget=DEMO_TOKEN_BUDGET)
        fixture_choice = msg["fixture_choice"][:MAX_NAME_LENGTH] if msg.get("fixture_choice") else None

        def run_demo():
            try:
                run_from_frontend(demo_id, fixture_choice, sink, api_client, human_name=human_name)
                
            except Exception as e:
                _send_error(websocket, loop, e)

        thread = threading.Thread(target=run_demo, daemon=True)
        thread.start()

        log_game_start(is_game=False, id=demo_id, player_names=[], human_name=human_name,
                       ip_address=get_client_ip(websocket), token_budget=DEMO_TOKEN_BUDGET)

        await _run_game_thread(thread, api_client, websocket, sink)

    except WebSocketDisconnect:
        if sink: sink.on_disconnect()
    finally:
        rate_limits.release_slot(api_client, get_client_ip(websocket))
