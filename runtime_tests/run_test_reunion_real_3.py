"""
Test script for FinaleReunionRound using real game log data.
Loads agent state from game 3 (Avatar Aang vs Morty Smith finale).
"""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.bootstrap import create_engine, ConsoleGameEventSink, create_blank_agent
from core.api_client import create_api_client
from tests.helpers.testing_game_design import TestingGameDesign
from core.levels.phase_description import PhaseDescription
from gameplay_management.eliminations.reunion_round import FinaleReunionRound

if __name__ == "__main__":
    # ── 1. Load agent state from logs ──
    fixtures_path = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "reunion_agent_state_3.json")
    with open(fixtures_path) as f:
        agent_state = json.load(f)

    # ── 2. Bootstrap with the real character names ──
    all_names = list(agent_state.keys())
    sink = ConsoleGameEventSink()
    api_client = create_api_client(sink, token_budget=2_000_000)
    engine = create_engine(sink, game_design=TestingGameDesign(), names=all_names, populate_agents=False, api_client=api_client)
    engine.initialiseGameBoard()

    # ── 3. Build name->agent lookup ──
    agents = {a.name: a for a in engine.agents}

    # ── 4. Set scores (finalists) ──
    engine.game_board.agent_scores["Avatar Aang"] = 39
    engine.game_board.agent_scores["Morty Smith"] = 39

    # ── 5. Eliminate dead agents in order (earliest eliminated first) ──
    elimination_order = [
        "HAL 9000",
        "Michael Jackson",
        "Amy March",
        "Benoit Blanc",
        "Buffy Summers",
        "Gollum",
        "Lady Macbeth",
        "Jo March",
        "Lady Dianna",
    ]

    for name in elimination_order:
        agent = agents[name]
        engine.eliminate_player(agent)

    # ── 6. Apply saved state to all agents ──
    for name, state in agent_state.items():
        agent = agents[name]
        agent.debug_log = True

        if state["persona"]:
            agent.persona = state["persona"]
        if state["speaking_style"]:
            agent.speaking_style = state["speaking_style"]

        if state["strategy"]:
            agent.game_strategy = state["strategy"]
        if state["math_assessment"]:
            agent.position_assessment = state["math_assessment"]

        agent.life_lessons.clear()
        for lesson in state["life_lessons"]:
            agent.life_lessons.append(lesson)

        for phase_str, text in state["summaries_detailed"].items():
            agent.phase_summaries_detailed[int(phase_str)] = text
        for phase_str, text in state["summaries_brief"].items():
            agent.phase_summaries_brief[int(phase_str)] = text

    # ── 7. Run the reunion ──
    engine.game_board.new_phase()
    engine.game_board.newRound()

    phase = PhaseDescription(rounds=[FinaleReunionRound])
    engine.phase_runner.run_phase(phase)
