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
from agents.character_generation.character_lister import CharacterLister

if __name__ == "__main__":
    sink = ConsoleGameEventSink()
    game_design = GameDesignQuickStart #RockPaperScissors quickstart
    api_client = create_api_client(sink, token_budget=2_000_000)
    human_player_name = "Brian" #None

    names=CharacterLister().goats[:game_design.min_players() - (1 if human_player_name else 0)]

    engine = create_engine(sink, game_design, human_player_name = human_player_name, names=names, allow_rename=False, api_client=api_client)
    engine.run()
