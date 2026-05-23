from gameplay_management.game_targeted.game_targeted_sacrifice import GameTargetedChoiceSacrifice
from gameplay_management.game_targeted.game_targeted_steal import GameTargetedChoiceSteal
from tests.helpers.game_test_helpers import (
    build_targeted_choice_game,
    host_messages,
    ledger_text,
    turn_payload,
)


# ---------- Steal ----------

def test_steal_full_amount_when_victim_has_enough():
    game, board, _agents, clients = build_targeted_choice_game(
        GameTargetedChoiceSteal,
        {
            "Alice": [
                turn_payload(target_name="Bob", public_response="Alice steals"),
                turn_payload(public_response="Alice reacts to Bob's theft"),
            ],
            "Bob": [
                turn_payload(public_response="Bob reacts to being stolen from"),
                turn_payload(target_name="Alice", public_response="Bob steals"),
            ],
        },
        initial_scores={"Alice": 10, "Bob": 10},
    )

    game.run_game()

    assert board.agent_scores == {"Alice": 10, "Bob": 10}
    msgs = host_messages(board)
    assert any("Alice steals from Bob" in m for m in msgs)
    assert any("Bob steals from Alice" in m for m in msgs)
    ledger = ledger_text(board)
    assert "Alice stole from Bob" in ledger
    assert "Bob stole from Alice" in ledger
    clients["Alice"].assert_exhausted()
    clients["Bob"].assert_exhausted()


def test_steal_partial_when_victim_underwater():
    game, board, _agents, clients = build_targeted_choice_game(
        GameTargetedChoiceSteal,
        {
            "Alice": [
                turn_payload(target_name="Bob", public_response="Alice steals"),
                turn_payload(public_response="Alice reacts to Bob's theft"),
            ],
            "Bob": [
                turn_payload(public_response="Bob reacts"),
                turn_payload(target_name="Alice", public_response="Bob steals"),
            ],
        },
        initial_scores={"Alice": 0, "Bob": 2},
    )

    game.run_game()

    # Alice steals all 2 from Bob; then Bob steals all 2 back from Alice.
    assert board.agent_scores == {"Alice": 0, "Bob": 2}
    msgs = host_messages(board)
    assert any("Alice steals from Bob" in m for m in msgs)
    assert any("Bob steals from Alice" in m for m in msgs)
    clients["Alice"].assert_exhausted()
    clients["Bob"].assert_exhausted()


def test_steal_empty_pockets_no_transfer_no_ledger():
    game, board, _agents, clients = build_targeted_choice_game(
        GameTargetedChoiceSteal,
        {
            "Alice": [
                turn_payload(target_name="Bob", public_response="Alice tries to steal"),
                turn_payload(public_response="Alice reacts to empty pockets"),
                turn_payload(public_response="Alice reacts to being stolen from"),
            ],
            "Bob": [
                turn_payload(target_name="Alice", public_response="Bob steals"),
            ],
        },
        initial_scores={"Alice": 5, "Bob": 0},
    )

    game.run_game()

    # Alice's attempt on Bob (0 points) is a no-op; Bob then steals 3 from Alice.
    assert board.agent_scores == {"Alice": 2, "Bob": 3}
    msgs = host_messages(board)
    assert any("empty pockets" in m for m in msgs)
    ledger = ledger_text(board)
    assert "Alice stole from Bob" not in ledger
    assert "Bob stole from Alice" in ledger
    clients["Alice"].assert_exhausted()
    clients["Bob"].assert_exhausted()


# ---------- Sacrifice ----------

def test_sacrifice_player_with_zero_points_skipped():
    game, board, _agents, clients = build_targeted_choice_game(
        GameTargetedChoiceSacrifice,
        {
            "Alice": [],
            "Bob": [
                turn_payload(target_name="Pass", points_to_spend=0),
                turn_payload(public_response="Bob reacts to pass"),
            ],
        },
        initial_scores={"Alice": 0, "Bob": 5},
    )

    game.run_game()

    assert board.agent_scores == {"Alice": 0, "Bob": 5}
    msgs = host_messages(board)
    assert any("has no points" in m for m in msgs)
    # Alice was skipped entirely, no API calls
    assert clients["Alice"].calls == []
    clients["Alice"].assert_exhausted()
    clients["Bob"].assert_exhausted()


def test_sacrifice_pass_no_damage_no_ledger():
    game, board, _agents, clients = build_targeted_choice_game(
        GameTargetedChoiceSacrifice,
        {
            "Alice": [
                turn_payload(target_name="Pass", points_to_spend=0, public_response="Alice passes"),
                turn_payload(public_response="Alice reacts to her own pass"),
            ],
        },
        initial_scores={"Alice": 5},
    )

    game.run_game()

    assert board.agent_scores == {"Alice": 5}
    msgs = host_messages(board)
    assert any("passes" in m for m in msgs)
    assert "sacrificed" not in ledger_text(board)
    clients["Alice"].assert_exhausted()


def test_sacrifice_successful_attack():
    game, board, _agents, clients = build_targeted_choice_game(
        GameTargetedChoiceSacrifice,
        {
            "Alice": [
                turn_payload(target_name="Bob", points_to_spend=2, public_response="Alice attacks"),
            ],
            "Bob": [
                turn_payload(public_response="Bob reacts to attack"),
                turn_payload(target_name="Pass", points_to_spend=0, public_response="Bob passes"),
                turn_payload(public_response="Bob reacts to his own pass"),
            ],
        },
        initial_scores={"Alice": 3, "Bob": 10},
    )

    game.run_game()

    assert board.agent_scores == {"Alice": 1, "Bob": 8}
    msgs = host_messages(board)
    assert any("BRUTAL" in m for m in msgs)
    assert "Alice sacrificed points to attack Bob" in ledger_text(board)
    clients["Alice"].assert_exhausted()
    clients["Bob"].assert_exhausted()


def test_sacrifice_spend_clamped_to_attacker_score():
    game, board, _agents, clients = build_targeted_choice_game(
        GameTargetedChoiceSacrifice,
        {
            "Alice": [
                turn_payload(target_name="Bob", points_to_spend=999, public_response="Alice overspends"),
            ],
            "Bob": [
                turn_payload(public_response="Bob reacts to attack"),
                turn_payload(target_name="Pass", points_to_spend=0),
                turn_payload(public_response="Bob reacts to his own pass"),
            ],
        },
        initial_scores={"Alice": 3, "Bob": 10},
    )

    game.run_game()

    # Spend clamped to Alice's 3 points; damage min(victim_score, spend) = 3
    assert board.agent_scores == {"Alice": 0, "Bob": 7}
    clients["Alice"].assert_exhausted()
    clients["Bob"].assert_exhausted()


def test_sacrifice_victim_zero_no_op():
    # Bob has 0 points, so he is skipped (no responses needed) and is also a no-op target.
    game, board, _agents, clients = build_targeted_choice_game(
        GameTargetedChoiceSacrifice,
        {
            "Alice": [
                turn_payload(target_name="Bob", points_to_spend=2, public_response="Alice attacks"),
                turn_payload(public_response="Alice reacts to no-op"),
            ],
            "Bob": [],
        },
        initial_scores={"Alice": 5, "Bob": 0},
    )

    game.run_game()

    assert board.agent_scores == {"Alice": 5, "Bob": 0}
    msgs = host_messages(board)
    assert any("has no points, so the attack does nothing" in m for m in msgs)
    assert "sacrificed" not in ledger_text(board)
    clients["Alice"].assert_exhausted()
    clients["Bob"].assert_exhausted()
