from types import SimpleNamespace

from tests.helpers.game_test_helpers import build_vote_game, host_messages


def test_process_vote_rounds_no_valid_votes_random_elimination_instead_of_crash(monkeypatch):
    game, board, _agents, _clients = build_vote_game({"Alice": [], "Bob": []})
    game._collect_votes = lambda _players: ([], [SimpleNamespace(action=""), SimpleNamespace(action=" ")])
    monkeypatch.setattr("gameplay_management.eliminations.voting_round_base.random.choice", lambda players: players[1])

    victim_name, returned_votes = game.process_vote_rounds(["Alice", "Bob"])

    assert victim_name == "Bob"
    assert returned_votes == [SimpleNamespace(action=""), SimpleNamespace(action=" ")]
    messages = host_messages(board)
    assert "🗳️ VOTING TALLY: {tally}".format(tally="") in messages
    assert "No valid votes were cast. The Judge will eliminate someone at random." in messages
