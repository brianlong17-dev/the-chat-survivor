import json
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

_SAVED_GAMES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "saved_games"
)

# Events that drive live interaction and have no meaning in a fire-through replay.
_SKIP_TYPES = {"input_request", "next_round_request"}


def _resolve_replay_path(replay_file):
    if not replay_file:
        return None
    safe = os.path.basename(replay_file)
    if safe != replay_file or not safe.endswith(".jsonl"):
        return None
    path = os.path.join(_SAVED_GAMES_DIR, safe)
    if not os.path.isfile(path):
        return None
    return path


@router.websocket("/ws/replay")
async def replay_ws(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    msg = json.loads(data)

    path = _resolve_replay_path(msg.get("replay_file"))
    if not path:
        await websocket.send_text(json.dumps({"type": "error", "message": "Unknown replay."}))
        await websocket.close()
        return

    try:
        with open(path, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        # A real tape trails off with a dangling input_request + inactivity system_private
        # after game_over. Drop everything past game_over so the replay lands clean.
        for i, line in enumerate(lines):
            if json.loads(line).get("type") == "game_over":
                lines = lines[: i + 1]
                break

        public_action_count = 0
        for line in lines:
            evt = json.loads(line)
            if evt.get("type") in _SKIP_TYPES:
                continue
            if evt.get("type") == "public_action":
                public_action_count += 1
                # Legacy tapes predate the sink's message_id stamp; backfill the same 0-N
                # scheme at send time. Tapes recorded with a real message_id pass through.
                if "message_id" not in evt:
                    evt["message_id"] = f"0-{public_action_count}"
                    line = json.dumps(evt, ensure_ascii=False)
            await websocket.send_text(line)

    except WebSocketDisconnect:
        return
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
