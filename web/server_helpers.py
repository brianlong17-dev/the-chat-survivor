import asyncio
import base64
import json
import traceback

from web.server_config import MAX_AUDIO_BYTES


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
