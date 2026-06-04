"""
Smoke tests for GamePrisonersDilemmaFinale. Each scenario exercises a branch
of run_game and asserts only that it doesn't crash.
"""

## PD_VERBOSE=1 uv run pytest tests/test_games/test_pd_finale_smoke.py -s -k tie  


import os
from typing import get_origin, get_args, Literal

import pytest
from pydantic import BaseModel

from core.gameboard import GameBoard
from core.levels.phase_description import PhaseDescription
from gameplay_management.games.game_pd_finale import GamePrisonersDilemmaFinale
from tests.helpers.game_test_helpers import (
    TestGameSink, TestSimulation, attach_test_runtime, make_debater,
)

VERBOSE = os.environ.get("PD_VERBOSE") == "1"


class ScriptedFinaleClient:
    """Fills every field with dummy values. `action` is popped from a queue."""

    _mock_output = False
    default_model = "test-model"
    higher_model = "test-model-high"

    def __init__(self, actions):
        self._actions = list(actions)

    def create(self, response_model, messages, thinking=False, use_higher_model=False):
        return self._fill(response_model)

    def _fill(self, response_model):
        values = {}
        for name, field_info in response_model.model_fields.items():
            ann = field_info.annotation
            if name == "action" and self._actions:
                values[name] = self._actions.pop(0)
            elif get_origin(ann) is Literal:
                values[name] = get_args(ann)[0]
            elif get_origin(ann) is list:
                inner = get_args(ann)[0] if get_args(ann) else str
                if get_origin(inner) is Literal:
                    values[name] = [get_args(inner)[0]]
                else:
                    values[name] = [f"dummy [{name}]"]
            elif isinstance(ann, type) and issubclass(ann, BaseModel):
                values[name] = self._fill(ann)
            else:
                values[name] = f"dummy [{name}]"
        return response_model(**values)


class _Sink(TestGameSink):
    """Swallow any sink method we haven't explicitly stubbed."""
    def __getattr__(self, name):
        return lambda *a, **kw: None


def _make_sink():
    if VERBOSE:
        from core.bootstrap import ConsoleGameEventSink
        return ConsoleGameEventSink()
    return _Sink()


def build_finale_game(scores, actions):
    """scores: {name: int}. actions: {name: [str, ...]} — one action per S/S turn the agent will take."""
    agents = [make_debater(name, ScriptedFinaleClient(actions[name])) for name in scores]
    board = GameBoard(_make_sink())
    board.initialize_agents(agents)
    for name, score in scores.items():
        board.agent_scores[name] = score
    simulation = TestSimulation(agents)
    game = GamePrisonersDilemmaFinale(board, simulation)
    attach_test_runtime(board, simulation, game)
    board.newRound()
    board.phase_runner.current_phase_description = PhaseDescription(rounds=[GamePrisonersDilemmaFinale])
    board.phase_runner.current_round_index = 0
    return game


# scores chosen so that:
#   gap == 0          → run_tie branch
#   0 < gap <= 5      → run_reg_game, is_coronation=False
#   gap > 5           → run_reg_game, is_coronation=True
#
# tie-after-reg: A=15,B=10 with (split, steal) → A=15, B=15 → recurses into
# run_tie(is_second_game=True). The second action covers that second game.
SCENARIOS = [
    # tie branch — gap 0
    ("tie_split_split", {"A": 10, "B": 10}, {"A": ["split"], "B": ["split"]}),
    ("tie_split_steal", {"A": 10, "B": 10}, {"A": ["split"], "B": ["steal"]}),
    ("tie_steal_split", {"A": 10, "B": 10}, {"A": ["steal"], "B": ["split"]}),
    ("tie_steal_steal", {"A": 10, "B": 10}, {"A": ["steal"], "B": ["steal"]}),

    # close reg game — gap 3
    ("reg_close_split_split", {"A": 13, "B": 10}, {"A": ["split"], "B": ["split"]}),
    ("reg_close_split_steal", {"A": 13, "B": 10}, {"A": ["split"], "B": ["steal"]}),
    ("reg_close_steal_split", {"A": 13, "B": 10}, {"A": ["steal"], "B": ["split"]}),
    ("reg_close_steal_steal", {"A": 13, "B": 10}, {"A": ["steal"], "B": ["steal"]}),

    # coronation reg game — gap 10
    ("reg_corona_split_split", {"A": 20, "B": 10}, {"A": ["split"], "B": ["split"]}),
    ("reg_corona_split_steal", {"A": 20, "B": 10}, {"A": ["split"], "B": ["steal"]}),
    ("reg_corona_steal_split", {"A": 20, "B": 10}, {"A": ["steal"], "B": ["split"]}),
    ("reg_corona_steal_steal", {"A": 20, "B": 10}, {"A": ["steal"], "B": ["steal"]}),

    # tie-after-reg → triggers run_tie(is_second_game=True). Second action used there.
    ("reg_then_tie_ss", {"A": 15, "B": 10}, {"A": ["split", "split"], "B": ["steal", "split"]}),
    ("reg_then_tie_xx", {"A": 15, "B": 10}, {"A": ["split", "steal"], "B": ["steal", "steal"]}),
    ("reg_then_tie_xs", {"A": 15, "B": 10}, {"A": ["split", "steal"], "B": ["steal", "split"]}),
]


@pytest.mark.parametrize("name,scores,actions", SCENARIOS, ids=[s[0] for s in SCENARIOS])
def test_finale_no_crash(name, scores, actions):
    game = build_finale_game(scores, actions)
    game.run_game()
