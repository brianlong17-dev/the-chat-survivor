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
from core.api_client import create_api_client
from core.levels.game_designs.game_design_beginner import GameDesignBeginner
from core.levels.game_designs.game_design_quickstart import GameDesignQuickStart

if __name__ == "__main__":
    sink = ConsoleGameEventSink()
    game_design = GameDesignQuickStart #RockPaperScissors quickstart
    api_client = create_api_client(sink, token_budget=2_000_000)
    engine = create_engine(sink, game_design, human_player_name = None, number_of_players=5, generic_players=False, allow_rename=False, api_client=api_client)
    engine.run() 
