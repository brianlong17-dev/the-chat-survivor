from gameplay_management.game_targeted.game_targeted_give import GameTargetedChoiceGive
from tests.new.helpers import start_game


def test_the_chosen_player_receives_the_points():
    game = start_game(players=["Ada", "Bo", "Cy"], rounds=[GameTargetedChoiceGive])
    game.chooses("Ada", target_name="Cy")
    game.chooses("Bo", target_name="Cy")
    game.chooses("Cy", target_name="Ada")

    game.run()

    assert game.score("Cy") == 6
    assert game.score("Ada") == 3


def test_a_player_nobody_chooses_receives_nothing():
    game = start_game(players=["Ada", "Bo", "Cy"], rounds=[GameTargetedChoiceGive])
    game.chooses("Ada", target_name="Cy")
    game.chooses("Bo", target_name="Cy")
    game.chooses("Cy", target_name="Ada")

    game.run()

    assert game.score("Bo") == 0


def test_giving_costs_the_giver_nothing():
    game = start_game(players=["Ada", "Bo"], rounds=[GameTargetedChoiceGive])
    game.chooses("Ada", target_name="Bo")
    game.chooses("Bo", target_name="Ada")

    game.run()

    assert game.scores() == {"Ada": 3, "Bo": 3}
