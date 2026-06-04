import asyncio
import base64
import json
import os
import threading
import traceback
from datetime import date

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from core.bootstrap import create_engine
from core.api_client_setup import create_api_client
from core.sinks.websocket_sink import WebSocketSink
from runtime_tests.demo_runner import DEMO_REGISTRY
from core.levels.level_registry import game_design_for_id

load_dotenv()

app = FastAPI()

# Feature flags — set to True to enable before publishing
GAME_ENABLED = True
DEMO_ENABLED = True
DEV_MODE = os.getenv("DEV_MODE", "false").lower() in ("1", "true", "yes")

_allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
_active_games = 0
_active_games_lock = threading.Lock()
MAX_CONCURRENT_GAMES = 5

_limit_lock = threading.Lock()
_games_today = 0
_limit_date = date.today()
DAILY_CAP = 20

MAX_AUDIO_BYTES = 10 * 1024 * 1024  # 10 MB decoded

async def _handle_transcribe(websocket, api_client, msg):
    try:
        
        """Transcribe audio over the websocket without blocking the event loop."""
        audio_b64 = msg.get("audio") or ""
        # base64 expands by ~4/3, so cap the encoded length cheaply before decoding
        if len(audio_b64) > (MAX_AUDIO_BYTES // 3) * 4 + 4:
            await websocket.send_text(json.dumps({"type": "transcription", "text": ""}))
            return
        audio_bytes = base64.b64decode(audio_b64)
        if len(audio_bytes) > MAX_AUDIO_BYTES:
            await websocket.send_text(json.dumps({"type": "transcription", "text": ""}))
            return
        hints = msg.get("hints")
        mime_type = msg.get("mimeType") or "audio/webm"
        text = await asyncio.to_thread(api_client.transcribe, audio_bytes, mime_type, hints=hints)
        await websocket.send_text(json.dumps({"type": "transcription", "text": text}))
    except Exception:
        traceback.print_exc()
        try:
            await websocket.send_text(json.dumps({"type": "transcription", "text": ""}))
        except Exception:
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


def check_and_increment_global_limit() -> bool:
    global _games_today, _limit_date
    with _limit_lock:
        today = date.today()
        if today != _limit_date:
            _games_today = 0
            _limit_date = today
        if _games_today >= DAILY_CAP:
            return False
        _games_today += 1
        return True
    
@app.get("/api/status")
async def status():
    return {
        "games_today": _games_today,
        "cap": DAILY_CAP,
        "date": _limit_date.isoformat(),
        "remaining": max(0, DAILY_CAP - _games_today)
    }
    

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Flags endpoint
# ---------------------------------------------------------------------------

@app.get("/api/flags")
async def get_flags():
    return {"game_enabled": GAME_ENABLED, "demo_enabled": DEMO_ENABLED}

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

@app.websocket("/ws/game")
async def game_ws(websocket: WebSocket):
    global _active_games
    await websocket.accept()

    #need to put this a method / file
    if not GAME_ENABLED:
        await websocket.send_text(json.dumps({"type": "error", "message": "Game is not available yet."}))
        await websocket.close()
        return

    loop = asyncio.get_event_loop()

    if not check_and_increment_global_limit():
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Daily game limit reached. Come back tomorrow."
        }))
        await websocket.close()
        return
    
    with _active_games_lock:
        if _active_games >= MAX_CONCURRENT_GAMES:
            await websocket.send_text(json.dumps({"type": "error", "message": f"Server is at capacity ({MAX_CONCURRENT_GAMES} active games). Try again soon."}))
            await websocket.close()
            return
        _active_games += 1
        

    sink = None
    try:
        # Wait for the "start" message from the client
        data = await websocket.receive_text()
        msg = json.loads(data)
        if msg.get("type") != "start":
            await websocket.send_text(json.dumps({"type": "error", "message": "Expected start message"}))
            return

        sink = WebSocketSink(websocket, loop)
        
        player_names = [str(n)[:30] for n in msg.get("names", [])[:12]] #this magic number? put it somewhere
        human_player_name = str(msg["human_name"])[:30] if msg.get("human_name") else None

        level_id = msg.get("levelId")
        game_design = game_design_for_id(level_id)
        api_client = create_api_client(sink)
      
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
        with _active_games_lock:
            _active_games -= 1



# ---------------------------------------------------------------------------
# Demos endpoint
# ---------------------------------------------------------------------------
@app.websocket("/ws/demo")
async def demo_ws(websocket: WebSocket):
    global _active_games
    await websocket.accept()

    if not DEMO_ENABLED:
        await websocket.send_text(json.dumps({"type": "error", "message": "Demo is not available yet."}))
        await websocket.close()
        return

    loop = asyncio.get_event_loop()
    
    
    if not check_and_increment_global_limit():
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Daily game limit reached. Come back tomorrow."
        }))
        await websocket.close()
        return
    
    with _active_games_lock:
        if _active_games >= MAX_CONCURRENT_GAMES:
            await websocket.send_text(json.dumps({"type": "error", "message": f"Server is at capacity ({MAX_CONCURRENT_GAMES} active games). Try again soon."}))
            await websocket.close()
            return
        _active_games += 1
        
    

    sink = None
    try:
        data = await websocket.receive_text()
        msg = json.loads(data)
        demo_id = msg.get("demo_id")
        human_name = str(msg["human_name"])[:30] if msg.get("human_name") else None
        fixture_choice = str(msg["fixture_choice"])[:30] if msg.get("fixture_choice") else None

        LOCKED_DEMOS = {} #"game_phase"}
        if demo_id in LOCKED_DEMOS:
            await websocket.send_text(json.dumps({"type": "error", "message": "This demo is not available yet."}))
            return

        runner = DEMO_REGISTRY.get(demo_id)
        if not runner:
            await websocket.send_text(json.dumps({"type": "error", "message": f"Unknown demo: {demo_id}"}))
            return

        sink = WebSocketSink(websocket, loop)
        api_client = create_api_client(sink)
        
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
        with _active_games_lock:
            _active_games -= 1
            
            
async def _run_game_thread(thread, api_client, websocket, sink):
    while thread.is_alive():
        try:
            data = await asyncio.wait_for(websocket.receive_text(), timeout=0.5)
            msg = json.loads(data)
            if msg.get("type") == "input_response":
                sink._input_queue.put(str(msg.get("value", ""))[:1500])
            elif msg.get("type") == "next_turn":
                sink._step_queue.put(True)
            elif msg.get("type") == "transcribe":
                asyncio.create_task(_handle_transcribe(websocket, api_client, msg))
        except asyncio.TimeoutError:
            pass
            
