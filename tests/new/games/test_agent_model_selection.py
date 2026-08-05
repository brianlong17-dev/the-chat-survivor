from gameplay_management.games.game_rps import GameRockPaperScissors
from tests.new.helpers import start_game


def test_a_player_with_a_configured_model_uses_it_for_their_turn():
    game = start_game(players=["Ada", "Bo"], rounds=[GameRockPaperScissors])
    game.uses_model("Ada", "gemini-2.5-flash-lite")
    game.chooses("Ada", action="rock")
    game.chooses("Bo", action="scissors")

    game.run()

    assert game.model_requested_by("Ada") == "gemini-2.5-flash-lite"


def test_a_player_without_a_configured_model_requests_none():
    game = start_game(players=["Ada", "Bo"], rounds=[GameRockPaperScissors])
    game.chooses("Ada", action="rock")
    game.chooses("Bo", action="scissors")

    game.run()

    assert game.model_requested_by("Bo") is None
