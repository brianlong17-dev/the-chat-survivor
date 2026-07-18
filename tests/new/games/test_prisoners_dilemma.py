from gameplay_management.games.game_prisoners_dilemma import GamePrisonersDilemma
from tests.new.helpers import start_game


def test_both_players_split_share_the_split_payout():
    game = start_game(players=["Ada", "Bo"], rounds=[GamePrisonersDilemma])
    game.chooses("Ada", action="split")
    game.chooses("Bo", action="split")

    game.run()

    assert game.score("Ada") == game.score("Bo") == 3


def test_both_players_steal_share_the_reduced_payout():
    game = start_game(players=["Ada", "Bo"], rounds=[GamePrisonersDilemma])
    game.chooses("Ada", action="steal")
    game.chooses("Bo", action="steal")

    game.run()

    assert game.score("Ada") == game.score("Bo") == 1


def test_a_stealer_takes_the_steal_payout_and_the_splitter_gets_nothing():
    game = start_game(players=["Ada", "Bo"], rounds=[GamePrisonersDilemma])
    game.chooses("Ada", action="steal")
    game.chooses("Bo", action="split")

    game.run()

    assert game.score("Ada") == 5
    assert game.score("Bo") == 0


def test_the_odd_player_out_receives_automatic_points():
    game = start_game(players=["Ada", "Bo", "Cy"], rounds=[GamePrisonersDilemma])
    game.configure("set_pd_pairing_none")
    game.chooses("Ada", action="steal")
    game.chooses("Bo", action="steal")
    game.chooses("Cy", action="steal")

    game.run()

    assert sorted(game.scores().values()) == [1, 1, 3]


def test_none_pairing_mode_pairs_players_off_without_a_choice():
    game = start_game(players=["Ada", "Bo"], rounds=[GamePrisonersDilemma])
    game.configure("set_pd_pairing_none")
    game.chooses("Ada", action="split")
    game.chooses("Bo", action="split")

    game.run()

    assert game.score("Ada") == game.score("Bo") == 3


def test_all_pairing_mode_matches_every_player_against_every_other_player():
    game = start_game(players=["Ada", "Bo", "Cy", "Dan"], rounds=[GamePrisonersDilemma])
    game.configure("set_pd_pairing_all")
    game.chooses("Ada", action="split")
    game.chooses("Bo", action="split")
    game.chooses("Cy", action="split")
    game.chooses("Dan", action="split")

    game.run()

    assert game.score("Ada") == game.score("Bo") == game.score("Cy") == game.score("Dan") == 9


def test_all_pairing_mode_has_no_leftover_even_with_an_odd_player_count():
    game = start_game(players=["Ada", "Bo", "Cy"], rounds=[GamePrisonersDilemma])
    game.configure("set_pd_pairing_all")
    game.chooses("Ada", action="steal")
    game.chooses("Bo", action="steal")
    game.chooses("Cy", action="steal")

    game.run()

    assert game.score("Ada") == game.score("Bo") == game.score("Cy") == 2


def test_lowest_pairing_mode_lets_the_lowest_scorer_choose_their_partner_first():
    game = start_game(players=["Ada", "Bo", "Cy", "Dan"], rounds=[GamePrisonersDilemma])
    game.configure("set_pd_pairing_lowest")
    game.has_points("Ada", 0)
    game.has_points("Bo", 1)
    game.has_points("Cy", 2)
    game.has_points("Dan", 3)
    game.chooses("Ada", in_round=GamePrisonersDilemma, target_name="Bo")
    game.chooses("Cy", in_round=GamePrisonersDilemma, target_name="Dan")
    game.chooses("Ada", action="split")
    game.chooses("Bo", action="split")
    game.chooses("Cy", action="split")
    game.chooses("Dan", action="split")

    game.run()

    assert game.score("Ada") == 3
    assert game.score("Bo") == 4
    assert game.score("Cy") == 5
    assert game.score("Dan") == 6


def test_random_pairing_mode_lets_the_chooser_pick_any_remaining_partner():
    game = start_game(players=["Ada", "Bo", "Cy"], rounds=[GamePrisonersDilemma])
    game.configure("set_pd_pairing_random")
    game.chooses("Ada", in_round=GamePrisonersDilemma, target_name="Bo")
    game.chooses("Bo", in_round=GamePrisonersDilemma, target_name="Cy")
    game.chooses("Cy", in_round=GamePrisonersDilemma, target_name="Ada")
    game.chooses("Ada", action="steal")
    game.chooses("Bo", action="steal")
    game.chooses("Cy", action="steal")

    game.run()

    assert sum(game.scores().values()) == 5
