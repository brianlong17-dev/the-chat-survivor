import os
from dotenv import load_dotenv
from core.shared_web_game_functionality import INACTIVITY_TIMEOUT  # noqa: F401 — re-exported for visibility

load_dotenv(override=True)

# Feature flags
GAME_ENABLED = os.environ.get("GAME_ENABLED", "true").lower() == "true"
DEMO_ENABLED = True

TRANSCRIPTION_ENABLED = os.getenv("TRANSCRIPTION_ENABLED", "").lower() == "true"
TURNSTILE_ENABLED = os.getenv("TURNSTILE_ENABLED", "").lower() == "true"
CHECK_IP = os.getenv("CHECK_IP", "").lower() == "true"


DEV_MODE = os.getenv("DEV_MODE", "false").lower() in ("1", "true", "yes")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

MAX_CONCURRENT_GAMES = int(os.environ.get("MAX_CONCURRENT_GAMES", 5))
DAILY_GAME_CAP = int(os.environ.get("DAILY_GAME_CAP", 100))
MAX_TOKENS_PER_GAME = int(os.environ.get("MAX_TOKENS_PER_GAME", 1500000))
DAILY_DEMO_CAP = 300
DAILY_TOKEN_CAP = 30_000_000

MAX_AUDIO_BYTES = 10 * 1024 * 1024  # 10 MB decoded

MAX_PLAYERS = 12
MAX_NAME_LENGTH = 40
MAX_INPUT_LENGTH = 1500
#INACTIVITY_TIMEOUT - imported

RATE_LIMITS_DB_PATH = os.getenv("RATE_LIMITS_DB_PATH", "data/rate_limits.db")

DEMO_TOKEN_BUDGET = 500_000
