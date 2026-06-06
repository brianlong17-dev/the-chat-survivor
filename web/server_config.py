import os
from dotenv import load_dotenv

# Feature flags — set to True to enable before publishing
GAME_ENABLED = True
DEMO_ENABLED = True

load_dotenv(override=True)
DEV_MODE = os.getenv("DEV_MODE", "false").lower() in ("1", "true", "yes")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

MAX_CONCURRENT_GAMES = 5
DAILY_GAME_CAP = 100
DAILY_DEMO_CAP = 300
DAILY_TOKEN_CAP = 30000000

MAX_AUDIO_BYTES = 10 * 1024 * 1024  # 10 MB decoded

MAX_PLAYERS = 12
MAX_NAME_LENGTH = 30
MAX_INPUT_LENGTH = 1500

RATE_LIMITS_DB_PATH = os.getenv("RATE_LIMITS_DB_PATH", "data/rate_limits.db")
