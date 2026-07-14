import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from web import rate_limits
from web.server_config import (ALLOWED_ORIGINS, DEMO_ENABLED, DEV_MODE, GAME_ENABLED,
    TRANSCRIPTION_ENABLED, TURNSTILE_ENABLED)
from web.server_helpers import handle_transcribe
from web.ws_game import router as game_router
from web.ws_demo import router as demo_router
from web.ws_replay import router as replay_router



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
app.include_router(replay_router)


# ---------------------------------------------------------------------------
# Flags endpoint
# ---------------------------------------------------------------------------

@app.get("/api/flags")
async def get_flags():
    return {"game_enabled": GAME_ENABLED, "demo_enabled": DEMO_ENABLED, "transcription_enabled": TRANSCRIPTION_ENABLED, "turnstile_enabled": TURNSTILE_ENABLED, "dev_mode": DEV_MODE}


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
            "Inside Out": lister.inside_out,
            "The Killer": lister.the_killer,
            "Ireland": lister.ireland,
            "All": _all
        }
    }


# ---------------------------------------------------------------------------
# Modules endpoint
# ---------------------------------------------------------------------------

@app.get("/api/modules")
async def get_modules():
    from demo_runner.game_module_directory import MODULES
    return {
        "modules": [
            {
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "finale": m.finale,
                "game": m.game,
            }
            for m in MODULES
            if not m.hidden
        ]
    }


# ---------------------------------------------------------------------------
# Fixtures endpoint
# ---------------------------------------------------------------------------

@app.get("/api/fixtures")
async def get_fixtures():
    from demo_runner.fixture_directory import FIXTURES
    from demo_runner.game_setup import load_fixture
    return {
        "fixtures": [
            {
                "id": f.name,
                "title": f.title,
                "cast": f.cast,
                "alive": f.alive,
                "pd_desc": f.pd_desc,
                "reunion_desc": f.reunion_desc,
                "game_desc": f.game_desc,
                "finale": f.finale,
                "break_before": f.break_before,
                "scores": load_fixture(f"{f.name}.json")["scores"],
            }
            for f in FIXTURES
            if not f.hidden
        ]
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
