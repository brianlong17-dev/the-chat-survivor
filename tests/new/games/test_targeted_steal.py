from gameplay_management.game_targeted.game_targeted_steal import GameTargetedChoiceSteal
from tests.new.helpers import start_game


def test_stealing_from_a_player_with_no_points_takes_nothing():
    game = start_game(players=["Ada", "Bo"], rounds=[GameTargetedChoiceSteal])
    game.chooses("Ada", target_name="Bo")
    game.chooses("Bo", target_name="Ada")

    game.run()

    assert game.turn_by("Ada")["amount"] == 0


def test_a_thief_takes_the_full_amount_from_a_rich_victim():
    game = start_game(players=["Ada", "Bo"], rounds=[GameTargetedChoiceSteal])
    game.has_points("Bo", 10)
    game.chooses("Ada", target_name="Bo")
    game.chooses("Bo", target_name="Ada")

    game.run()

    assert game.turn_by("Ada")["target"] == "Bo"
    assert game.turn_by("Ada")["amount"] == 3


def test_a_thief_cannot_take_more_points_than_the_victim_has():
    game = start_game(players=["Ada", "Bo"], rounds=[GameTargetedChoiceSteal])
    game.has_points("Bo", 2)
    game.chooses("Ada", target_name="Bo")
    game.chooses("Bo", target_name="Ada")

    game.run()

    assert game.turn_by("Ada")["amount"] == 2


def test_a_steal_moves_points_without_creating_any():
    game = start_game(players=["Ada", "Bo", "Cy"], rounds=[GameTargetedChoiceSteal])
    game.has_points("Ada", 5)
    game.has_points("Bo", 5)
    game.has_points("Cy", 5)
    game.chooses("Ada", target_name="Bo")
    game.chooses("Bo", target_name="Cy")
    game.chooses("Cy", target_name="Ada")

    game.run()

    assert sum(game.scores().values()) == 15
