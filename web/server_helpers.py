import asyncio
import base64
import json
import logging
import os
import traceback
import uuid
from datetime import datetime

import httpx
from fastapi import WebSocket

from core.shared_web_game_functionality import sanitize_text
from web.server_config import MAX_AUDIO_BYTES, DEV_MODE, MAX_INPUT_LENGTH, TRANSCRIPTION_ENABLED

TURNSTILE_SECRET = os.getenv("TURNSTILE_SECRET")
if not TURNSTILE_SECRET: # and TURNSTILE_ENABLED --  for now always crash
    raise RuntimeError("TURNSTILE_ENABLED is on but TURNSTILE_SECRET is not set")

_GAME_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "gamelogs")
_game_logger = None


def _get_game_logger() -> logging.Logger:
    """Lazily build the game-start logger so importing this module has no filesystem side effects."""
    global _game_logger
    if _game_logger is None:
        os.makedirs(_GAME_LOG_DIR, exist_ok=True)
        handler = logging.FileHandler(os.path.join(_GAME_LOG_DIR, "master_game_log"))
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger = logging.getLogger("game")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        _game_logger = logger
    return _game_logger


def sanitize_name(name: str) -> str:
    name = " ".join(sanitize_text(name).split())
    return name


def get_client_ip(websocket: WebSocket) -> str | None:
    # CF-Connecting-IP is set by Cloudflare; fall back to the direct peer.
    return websocket.headers.get("CF-Connecting-IP") or (
        websocket.client.host if websocket.client else None
    )


async def verify_turnstile(token: str) -> bool:
    if not token:
        return False
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": TURNSTILE_SECRET, "response": token}
        )
        return resp.json().get("success", False)


async def _notify_game_start(ntfy_url, msg):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(ntfy_url, content=msg, timeout=3)
    except Exception:
        pass


def log_game_start(is_game, id, player_names, human_name, ip_address, token_budget):
    event = "game_start" if is_game else "demo_start"
    _get_game_logger().info(json.dumps({
        "event": event,
        "game_id": str(uuid.uuid4()),
        "level_id" if is_game else "demo_id": id,
        "player_names": player_names,
        "human_name": human_name,
        "ip": ip_address,
        "token_budget": token_budget,
        "time": datetime.utcnow().isoformat(),
    }))
    
    if ntfy_game_start := os.getenv("ntfy_game_start"):
        ntfy_url = f"https://ntfy.sh/{ntfy_game_start}"
        label = "Game" if is_game else "Demo"
        name_label = human_name if human_name else "Viewer"
        msg = f"{ip_address} - {label} started ({id})— {name_label} playing with {', '.join(player_names)}"
        asyncio.create_task(_notify_game_start(ntfy_url, msg))


async def _run_game_thread(thread, api_client, websocket, sink):
    while thread.is_alive():
        try:
            data = await asyncio.wait_for(websocket.receive_text(), timeout=0.5)
            msg = json.loads(data)
            if msg.get("type") == "input_response":
                sink._input_queue.put(str(msg.get("value", ""))[:MAX_INPUT_LENGTH])
            elif msg.get("type") == "next_round":
                sink.set_round_gate_open()
            elif msg.get("type") == "set_flag":
                if msg.get("flag") == "mobile_outputs":
                    sink.mobile_outputs = bool(msg.get("value"))
            elif msg.get("type") == "transcribe" and TRANSCRIPTION_ENABLED:
                asyncio.create_task(handle_transcribe(websocket, api_client, msg))
        except asyncio.TimeoutError:
            pass


def _send_error(websocket, loop, exc):
    """Safe to call from any thread."""
    traceback.print_exc()
    message = f"{exc}\n\n{traceback.format_exc()}" if DEV_MODE else str(exc)
    try:
        asyncio.run_coroutine_threadsafe(
            websocket.send_text(json.dumps({"type": "error", "message": message})),
            loop,
        ).result(timeout=5)
    except Exception:
        pass


async def handle_transcribe(websocket, api_client, msg):
    """Transcribe audio over the websocket without blocking the event loop."""
    try:
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
