# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "instructor",
#     "google-genai",
#     "python-dotenv",
#     "pydantic",
# ]
# ///
from core.bootstrap import *
from core.levels.game_designs.game_design_default import GameDesignDefault

if __name__ == "__main__":
    sink = ConsoleGameEventSink()
    engine = create_engine(sink, GameDesignDefault, number_of_players = 8, generic_players=False, allow_rename = False)
    engine.run() #human_player_name = "Brian")
