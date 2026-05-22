"""
Runtime test for GamePrisonersDilemmaFinale.
Two dummy agents tied at 10 points — exercises the tie branch.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.bootstrap import create_engine, ConsoleGameEventSink
from core.api_client import api_client
from core.levels.phase_recipe import PhaseRecipe
from runtime_tests.hardcoded_cast import build_hardcoded_debaters
from gameplay_management.games.game_pd_finale import GamePrisonersDilemmaFinale


if __name__ == "__main__":
    sink = ConsoleGameEventSink()
    api_client._mock_output = True

    names = ["Finn", "Jake"]
    agents = build_hardcoded_debaters(names)
    engine = create_engine(sink, agents=agents, allow_rename=False)
    engine.initialiseGameBoard()

    for name in names:
        engine.game_board.agent_scores[name] = 10

    engine.game_board.new_phase()
    engine.game_board.newRound()
    phase = PhaseRecipe(rounds=[GamePrisonersDilemmaFinale])
    engine.phase_runner.run_phase(phase)
    api_client.print_summary()
