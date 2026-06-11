import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web import rate_limits
from web.server_config import (ALLOWED_ORIGINS, DEMO_ENABLED, GAME_ENABLED,
    TRANSCRIPTION_ENABLED, TURNSTILE_ENABLED)
from web.server_helpers import handle_transcribe
from web.ws_game import router as game_router
from web.ws_demo import router as demo_router



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_router)
app.include_router(demo_router)


# ---------------------------------------------------------------------------
# Flags endpoint
# ---------------------------------------------------------------------------

@app.get("/api/flags")
async def get_flags():
    return {"game_enabled": GAME_ENABLED, "demo_enabled": DEMO_ENABLED, "transcription_enabled": TRANSCRIPTION_ENABLED, "turnstile_enabled": TURNSTILE_ENABLED}


# ---------------------------------------------------------------------------
# Status endpoint
# ---------------------------------------------------------------------------

@app.get("/api/status")
async def status():
    return rate_limits.snapshot()


# ---------------------------------------------------------------------------
# Characters endpoint
# ---------------------------------------------------------------------------

@app.get("/api/characters")
async def get_characters():
    from agents.character_generation.character_lister import CharacterLister
    lister = CharacterLister()
    _all= list(dict.fromkeys(lister.full_characters + lister.agros + lister.regulars + lister.logicos + lister.schemers ))
    return {
        "tabs": {
            "Classics": lister.goats,
            "Adventure Time": lister.adventure_time,
            "Star Wars": lister.star_wars,
            "Succession": lister.succession,
            "Little Women": lister.marches,
            "Avatar": lister.avatar,
            "Meryls": lister.streep,
            "The Killer": lister.the_killer,
            "All": _all
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
