from gameplay_management.game_targeted.game_targeted_sacrifice import GameTargetedChoiceSacrifice
from tests.new.helpers import start_game


def test_passing_costs_nothing():
    game = start_game(players=["Ada", "Bo"], rounds=[GameTargetedChoiceSacrifice])
    game.has_points("Ada", 5)
    game.has_points("Bo", 5)
    game.chooses("Ada", target_name="Pass", points_to_spend=0)
    game.chooses("Bo", target_name="Pass", points_to_spend=0)

    game.run()

    assert game.scores() == {"Ada": 5, "Bo": 5}


def test_spending_points_deals_equal_damage_to_the_target():
    game = start_game(players=["Ada", "Bo"], rounds=[GameTargetedChoiceSacrifice])
    game.has_points("Ada", 5)
    game.has_points("Bo", 5)
    game.chooses("Ada", target_name="Bo", points_to_spend=3)
    game.chooses("Bo", target_name="Pass", points_to_spend=0)

    game.run()

    assert game.turn_by("Ada")["actor_amount"] == -3
    assert game.turn_by("Ada")["target_amount"] == -3


def test_a_player_with_no_points_cannot_attack():
    game = start_game(players=["Ada", "Bo"], rounds=[GameTargetedChoiceSacrifice])
    game.has_points("Bo", 5)
    game.chooses("Bo", target_name="Ada", points_to_spend=5)

    game.run()

    assert game.turn_by("Ada")["action"] == "pass"
    assert game.score("Ada") == 0


def test_attacking_a_player_with_no_points_wastes_the_spend():
    game = start_game(players=["Ada", "Bo"], rounds=[GameTargetedChoiceSacrifice])
    game.has_points("Ada", 5)
    game.chooses("Ada", target_name="Bo", points_to_spend=3)
    game.chooses("Bo", target_name="Pass", points_to_spend=0)

    game.run()

    assert game.turn_by("Ada")["actor_amount"] == 0
    assert game.turn_by("Ada")["target_amount"] == 0
    assert game.score("Ada") == 5
    assert game.score("Bo") == 0


def test_damage_cannot_exceed_the_targets_remaining_points():
    game = start_game(players=["Ada", "Bo"], rounds=[GameTargetedChoiceSacrifice])
    game.has_points("Ada", 10)
    game.has_points("Bo", 2)
    game.chooses("Ada", target_name="Bo", points_to_spend=8)
    game.chooses("Bo", target_name="Pass", points_to_spend=0)

    game.run()

    assert game.turn_by("Ada")["actor_amount"] == -8
    assert game.turn_by("Ada")["target_amount"] == -2
    assert game.score("Bo") == 0
