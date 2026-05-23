from typing import get_args

from gameplay_management.game_targeted.game_targeted_give import GameTargetedChoiceGive
from tests.helpers.game_test_helpers import (
    build_targeted_choice_game,
    host_messages,
    ledger_text,
    turn_payload,
)


def test_give_awards_points_to_target_each_turn():
    game, board, _agents, clients = build_targeted_choice_game(
        GameTargetedChoiceGive,
        {
            "Alice": [
                turn_payload(target_name="Bob", public_response="Alice gives to Bob"),
                turn_payload(public_response="Alice reacts to Bob giving"),
            ],
            "Bob": [
                turn_payload(public_response="Bob reacts to Alice giving"),
                turn_payload(target_name="Alice", public_response="Bob gives to Alice"),
            ],
        },
    )

    game.run_game()

    assert board.agent_scores == {"Alice": 3, "Bob": 3}
    messages = host_messages(board)
    assert "Yay! Alice chooses Bob! They receive 3 points." in messages
    assert "Yay! Bob chooses Alice! They receive 3 points." in messages
    ledger = ledger_text(board)
    assert "Alice gave points to Bob" in ledger
    assert "Bob gave points to Alice" in ledger
    clients["Alice"].assert_exhausted()
    clients["Bob"].assert_exhausted()


def test_give_invokes_target_for_reaction():
    game, _board, _agents, clients = build_targeted_choice_game(
        GameTargetedChoiceGive,
        {
            "Alice": [
                turn_payload(target_name="Bob"),
                turn_payload(public_response="Alice reacts to Bob giving"),
            ],
            "Bob": [
                turn_payload(public_response="Bob reacts to Alice giving"),
                turn_payload(target_name="Alice"),
            ],
        },
    )

    game.run_game()

    # Each agent: 1 action + 1 reaction = 2 calls
    assert len(clients["Alice"].calls) == 2
    assert len(clients["Bob"].calls) == 2
    clients["Alice"].assert_exhausted()
    clients["Bob"].assert_exhausted()


def test_give_model_choices_exclude_current_player():
    game, _board, _agents, clients = build_targeted_choice_game(
        GameTargetedChoiceGive,
        {
            "Alice": [
                turn_payload(target_name="Bob"),
                turn_payload(public_response="Alice reacts"),
            ],
            "Bob": [
                turn_payload(public_response="Bob reacts"),
                turn_payload(target_name="Cara"),
            ],
            "Cara": [
                turn_payload(public_response="Cara reacts"),
                turn_payload(target_name="Alice"),
            ],
        },
    )

    game.run_game()

    decision_calls = [
        call
        for client in clients.values()
        for call in client.calls
        if "target_name" in getattr(call["response_model"], "model_fields", {})
    ]
    assert len(decision_calls) == 3

    observed_choices = [
        set(get_args(call["response_model"].model_fields["target_name"].annotation))
        for call in decision_calls
    ]
    assert {"Bob", "Cara"} in observed_choices
    assert {"Alice", "Cara"} in observed_choices
    assert {"Alice", "Bob"} in observed_choices
