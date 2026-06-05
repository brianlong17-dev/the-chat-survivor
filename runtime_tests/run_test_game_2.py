"""
Reusable game test sandbox — Adventure Time cast.
Loads Finn and LSP from end-of-game state, sets up scores, then runs a game.
Swap the game class at the bottom to test different games.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.bootstrap import ConsoleGameEventSink
from core.levels.phase_description import PhaseDescription
from gameplay_management.eliminations.voting_bottom_two import VoteBottomTwo
from gameplay_management.games.game_pd_finale import GamePrisonersDilemmaFinale
from runtime_tests.game_setup import setup_game_from_fixture

if __name__ == "__main__":
    sink = ConsoleGameEventSink()

    scores = {
        "Finn": 17,
        "Lumpy Space Princess": 17,
    }

    # ── 1–5. Load fixture, bootstrap, apply state ──
    engine, agents = setup_game_from_fixture(
        sink,
        fixture_filename="game_agent_state_finn_LSP.json",
        scores=scores,
        phase_number=5,
    )

    # ── 6. Run the game ──
    engine.game_board.new_phase()
    engine.game_board.newRound()
    rounds = 0
    cfg = engine.gameplay_config
    cfg.pd_pairing_method = cfg.pd_pairing_choice_all
    #while len(engine.agents) > 1:
    while rounds < 1:
        rounds += 1
        phase = PhaseDescription(rounds=[GamePrisonersDilemmaFinale])
        engine.phase_runner.run_phase(phase)
    engine.api_client.print_and_write_summary()
