"""
Runtime test for GamePrisonersDilemmaFinale.
Two dummy agents tied at 10 points — exercises the tie branch.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.bootstrap import create_engine, ConsoleGameEventSink
from core.api_client import create_api_client
from tests.helpers.testing_game_design import TestingGameDesign
from core.levels.phase_description import PhaseDescription
from gameplay_management.games.game_pd_finale import GamePrisonersDilemmaFinale


if __name__ == "__main__":
    sink = ConsoleGameEventSink()
    api_client = create_api_client(sink, token_budget=2_000_000)
    names = ["Finn", "Jake"]
    engine = create_engine(sink, game_design=TestingGameDesign(), names=names, populate_agents=False, allow_rename=False, api_client=api_client)
    engine.api_client._mock_output = True
    engine.initialiseGameBoard()

    for name in names:
        engine.game_board.agent_scores[name] = 10

    engine.game_board.new_phase()
    engine.game_board.newRound()
    phase = PhaseDescription(rounds=[GamePrisonersDilemmaFinale])
    engine.phase_runner.run_phase(phase)
    engine.api_client.print_and_write_summary()
