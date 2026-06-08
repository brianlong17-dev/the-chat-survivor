import asyncio
import json
import threading
import traceback

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from core.bootstrap import create_engine
from core.api_client import create_api_client
from core.sinks.websocket_sink import WebSocketSink
from runtime_tests.demo_runner import DEMO_REGISTRY
from core.levels.level_registry import get_level_by_id
from web import rate_limits
from web.server_config import (ALLOWED_ORIGINS, DEMO_ENABLED, DEV_MODE, GAME_ENABLED,
    MAX_INPUT_LENGTH, MAX_NAME_LENGTH, MAX_PLAYERS, DEMO_TOKEN_BUDGET, TRANSCRIPTION_ENABLED
)
from core.sanitize import sanitize_name
from web.server_helpers import handle_transcribe

app = FastAPI()


@app.get("/api/status")
async def status():
    return rate_limits.snapshot()


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Flags endpoint
# ---------------------------------------------------------------------------

@app.get("/api/flags")
async def get_flags():
    return {"game_enabled": GAME_ENABLED, "demo_enabled": DEMO_ENABLED, "transcription_enabled": TRANSCRIPTION_ENABLED}

# ---------------------------------------------------------------------------
# Characters endpoint
# ---------------------------------------------------------------------------

@app.get("/api/characters")
async def get_characters():
    from agents.character_generation.character_lister import CharacterLister
    lister = CharacterLister()
    return {
        "tabs": {
            "Classics": lister.goats,
            "Generics": lister.generics,
            "Schemers": lister.schemers,
            "Regulars": lister.regulars,
            "Little Women" : lister.marches,
            "Hot Heads": lister.agros,
            "Logicos": lister.logicos,
            "All": list(dict.fromkeys(lister.full_characters)),  # dedupe
        }
    }

# ---------------------------------------------------------------------------
# Levels endpoint
# ---------------------------------------------------------------------------

@app.get("/api/levels")
async def get_levels():
    from core.levels import AVAILABLE_LEVELS
    return {
        "levels": [
            {
                "id": level.id,
                "name": level.name,
                "description": level.description,
                "min_players": level.min_players,
                "max_players": level.max_players,
                "locked": level.locked,
            }
            for level in AVAILABLE_LEVELS
        ]
    }

# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------
async def _can_run_game(websocket: WebSocket):
    if not GAME_ENABLED:
        await websocket.send_text(json.dumps({"type": "error", "message": "Game is not available yet."}))
        return False

    if not await rate_limits.check_token_cap(websocket):
        return False
    
    if not await rate_limits.daily_and_concurrency_check(websocket, "game"):
        return False
    return True

@app.websocket("/ws/game")
async def game_ws(websocket: WebSocket):
    await websocket.accept()

    if not await _can_run_game(websocket):
        await websocket.close()
        return

    loop = asyncio.get_event_loop()
    sink = None
    api_client = None

    try:
        # Wait for the "start" message from the client
        data = await websocket.receive_text()
        msg = json.loads(data)
        if msg.get("type") != "start":
            await websocket.send_text(json.dumps({"type": "error", "message": "Expected start message"}))
            return
        level_id = msg.get("levelId")
        level = get_level_by_id(level_id)
        if not level:
            await websocket.send_text(json.dumps({"type": "error", "message": "Invalid level."}))
            return
        
        game_design = level.game_design 
        sink = WebSocketSink(websocket, loop)

        
        human_player_name = str(msg["human_name"])[:MAX_NAME_LENGTH] if msg.get("human_name") else None
        max_players = min(level.max_players, MAX_PLAYERS) - (1 if human_player_name else 0)
        player_names = [str(n)[:MAX_NAME_LENGTH] for n in msg.get("names", [])[:max_players]]

        player_names = [sanitize_name(name) for name in player_names]
        human_player_name = sanitize_name(human_player_name)
        
        api_client = create_api_client(sink, token_budget=level.token_budget)

        def run_game():
            try:
                engine = create_engine(sink, names=player_names, game_design=game_design, api_client=api_client)
                engine.run(human_player_name=human_player_name)
            except Exception as e:
                _send_error(websocket, loop, e)

        thread = threading.Thread(target=run_game, daemon=True)
        thread.start()
        await _run_game_thread(thread, api_client, websocket, sink)

    except WebSocketDisconnect:
        if sink: sink.on_disconnect()
    finally:
        rate_limits.release_slot(api_client)



# ---------------------------------------------------------------------------
# Demos endpoint
# ---------------------------------------------------------------------------

async def _can_run_demo(websocket: WebSocket, demo_id):
    if not DEMO_ENABLED:
        await websocket.send_text(json.dumps({"type": "error", "message": "Demo is not available yet."}))
        return False

    LOCKED_DEMOS = {} #"game_phase"}
    if demo_id in LOCKED_DEMOS:
        await websocket.send_text(json.dumps({"type": "error", "message": "This demo is not available yet."}))
        return False

    if not await rate_limits.check_token_cap(websocket):
        return False

    if not await rate_limits.daily_and_concurrency_check(websocket, "demo"):
        return False

    return True


@app.websocket("/ws/demo")
async def demo_ws(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    msg = json.loads(data)
    demo_id = msg.get("demo_id")

    if not await _can_run_demo(websocket, demo_id):
        await websocket.close()
        return

    loop = asyncio.get_event_loop()
    sink = None
    api_client = None
    try:
        human_name = str(msg["human_name"])[:MAX_NAME_LENGTH] if msg.get("human_name") else None
        human_name = sanitize_name(human_name)
        
        fixture_choice = str(msg["fixture_choice"])[:MAX_NAME_LENGTH] if msg.get("fixture_choice") else None
        runner = DEMO_REGISTRY.get(demo_id)
        if not runner: #this wont happen in practice
            await websocket.send_text(json.dumps({"type": "error", "message": f"Unknown demo: {demo_id}"}))
            return

        sink = WebSocketSink(websocket, loop)
        api_client = create_api_client(sink, token_budget = DEMO_TOKEN_BUDGET) 

        def run_demo():
            try:
                runner(sink, api_client, human_name=human_name, fixture_choice=fixture_choice, )
            except Exception as e:
                _send_error(websocket, loop, e)

        thread = threading.Thread(target=run_demo, daemon=True)
        thread.start()
        await _run_game_thread(thread, api_client, websocket, sink)

    except WebSocketDisconnect:
        if sink: sink.on_disconnect()
    finally:
        rate_limits.release_slot(api_client)


async def _run_game_thread(thread, api_client, websocket, sink):
    while thread.is_alive():
        try:
            data = await asyncio.wait_for(websocket.receive_text(), timeout=0.5)
            msg = json.loads(data)
            if msg.get("type") == "input_response":
                sink._input_queue.put(str(msg.get("value", ""))[:MAX_INPUT_LENGTH])
            elif msg.get("type") == "next_round":
                sink.set_round_gate_open()
            elif msg.get("type") == "transcribe" and TRANSCRIPTION_ENABLED:
                asyncio.create_task(handle_transcribe(websocket, api_client, msg))
        except asyncio.TimeoutError:
            pass

def _send_error(websocket, loop, exc):
    """Send an exception to the connected client. Safe to call from any thread."""
    traceback.print_exc()
    message = f"{exc}\n\n{traceback.format_exc()}" if DEV_MODE else str(exc)
    try:
        asyncio.run_coroutine_threadsafe(
            websocket.send_text(json.dumps({"type": "error", "message": message})),
            loop,
        ).result(timeout=5)
    except Exception:
        pass
