from gameplay_management.eliminations.voting_lowest_points import VoteLowestPoints
from gameplay_management.games.game_rps import GameRockPaperScissors
from tests.new.helpers import start_game


def test_rock_beats_scissors():
    game = start_game(players=["Ada", "Bo"], rounds=[GameRockPaperScissors])
    game.chooses("Ada", action="rock")
    game.chooses("Bo", action="scissors")

    game.run()

    assert game.score("Ada") > game.score("Bo")
    assert game.score("Bo") == 0


def test_a_tie_scores_both_players_equally():
    game = start_game(players=["Ada", "Bo"], rounds=[GameRockPaperScissors])
    game.chooses("Ada", action="paper")
    game.chooses("Bo", action="paper")

    game.run()

    assert game.score("Ada") == game.score("Bo")
    assert game.score("Ada") > 0


def test_the_player_who_lost_the_only_game_is_voted_out():
    game = start_game(players=["Ada", "Bo"], rounds=[GameRockPaperScissors, VoteLowestPoints])
    game.chooses("Ada", action="rock")
    game.chooses("Bo", action="scissors")

    game.run()

    assert game.eliminated() == ["Bo"]
    assert game.winner() == "Ada"
