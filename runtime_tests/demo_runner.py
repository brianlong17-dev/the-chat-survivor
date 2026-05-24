"""
Demo runner functions — callable versions of the runtime test scripts.
Each function accepts a sink (any GameEventSink) and an optional human_name.
"""
import sys
import os

from gameplay_management.game_targeted.game_targeted_steal import GameTargetedChoiceSteal
from gameplay_management.games.game_pd_finale import GamePrisonersDilemmaFinale
from tests.helpers.scripted_phase_factory import ScriptedPhaseFactory

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gameplay_management.discussion_rounds.discussion_round import DiscussionRound
from gameplay_management.discussion_rounds.discussion_round_directed_short import DiscussionRoundDirectedShort

from gameplay_management.games.game_prisoners_dilemma import GamePrisonersDilemma
from runtime_tests.game_setup import (
    load_fixture, apply_agent_state, create_agents_from_names,
    add_human, setup_game_from_fixture,
)



def _run_reunion(sink, fixture_filename: str, finalist_scores: dict, elimination_order: list, human_name: str = None, phase_number=None):
    from core.bootstrap import create_engine
    from core.levels.phase_recipe import PhaseRecipe
    from gameplay_management.eliminations.reunion_round import FinaleReunionRound

    agent_state = load_fixture(fixture_filename)
    all_names = list(agent_state.keys())
    agents = create_agents_from_names(all_names)

    engine = create_engine(sink, agents=agents, allow_rename=False)
    if phase_number:
        engine.game_board.phase_number = 11

    if human_name:
        add_human(human_name, engine, is_dead=True)

    engine.initialiseGameBoard()
    agents = {a.name: a for a in engine.agents}

    for name, score in finalist_scores.items():
        engine.game_board.agent_scores[name] = score
        
    apply_agent_state(agents, agent_state)
    for name in elimination_order:
        agent = agents[name]
        engine.eliminate_player(agent)

    

    phase = PhaseRecipe(rounds=[FinaleReunionRound])
    engine.phase_runner.run_phase(phase)


REUNION_FIXTURES = {
    "game_3": {
        "fixture_filename": "reunion_agent_state_3.json",
        "finalist_scores": {"Avatar Aang": 39, "Morty Smith": 39},
        "elimination_order": [
            "HAL 9000", "Michael Jackson", "Amy March", "Benoit Blanc",
            "Buffy Summers", "Gollum", "Lady Macbeth", "Jo March", "Lady Diana",
        ],
        "phase_number": 11,
    },
    "game_2": {
        "fixture_filename": "reunion_agent_state_2.json",
        "finalist_scores": {"Amy March": 41, "Lady Diana": 48},
        "elimination_order": [
            "Morty Smith", "Lady Macbeth", "HAL 9000", "Jo March",
            "Michael Jackson", "Avatar Aang", "Gollum", "Buffy Summers", "Benoit Blanc",
        ],
        "phase_number": None,
    },
    "finn_lsp": {
        "fixture_filename": "game_agent_state_finn_LSP.json",
        "finalist_scores": {"Finn": 17, "Lumpy Space Princess": 17},
        "elimination_order": ["BMO", "Princess Bubblegum", "Ice King", "Jake the Dog"],
        "phase_number": 4,
    },
    "adventure_time_pre_finale": {
        "fixture_filename": "adventure_time_pre_finale.json",
        "finalist_scores": {"Jake the Dog": 16, "Finn": 13},
        "elimination_order": ["BMO", "Lumpy Space Princess", "Ice King", "Princess Bubblegum"],
        "phase_number": 5,
    },
    "brian_jake_pre_finale": {
        "fixture_filename": "brian_jake_pre_finale.json",
        "finalist_scores": {"Finn the Human": 17, "Brian": 15},
        "elimination_order": ["Lumpy Space Princess", "BMO", "Princess Bubblegum", "Jake the Dog"],
        "phase_number": 5,
    },
    "aang_pb_pre_finale": {
        "fixture_filename": "aang_pb_pre_finale.json",
        "finalist_scores": {"Avatar Aang": 11, "Princess Bubblegum": 18},
        "elimination_order": ["BMO", "Jake the Dog", "Finn the Human", "Lumpy Space Princess"],
        "phase_number": 4,
    },
}


PD_FINALE_FIXTURES = {
    "game_3": {
        "fixture_filename": "reunion_agent_state_3.json",
        "finalist_scores": {"Avatar Aang": 39, "Morty Smith": 39},
        "phase_number": 11,
    },
    "game_2": {
        "fixture_filename": "reunion_agent_state_2.json",
        "finalist_scores": {"Amy March": 41, "Lady Diana": 48},
        "phase_number": 11,
    },
    "finn_lsp": {
        "fixture_filename": "game_agent_state_finn_LSP.json",
        "finalist_scores": {"Finn": 17, "Lumpy Space Princess": 17},
        "phase_number": 5,
    },
    "adventure_time_pre_finale": {
        "fixture_filename": "adventure_time_pre_finale.json",
        "finalist_scores": {"Jake the Dog": 16, "Finn": 13},
        "phase_number": 5,
    },
    "brian_jake_pre_finale": {
        "fixture_filename": "brian_jake_pre_finale.json",
        "finalist_scores": {"Finn the Human": 17, "Brian": 15},
        "phase_number": 5,
    },
    "aang_pb_pre_finale": {
        "fixture_filename": "aang_pb_pre_finale.json",
        "finalist_scores": {"Avatar Aang": 11, "Princess Bubblegum": 18},
        "phase_number": 5,
    },
}


def run_demo_reunion(sink, human_name: str = None, fixture_choice: str = None):
    """Reunion Finale: jury votes between two finalists, then a PD finale."""
    choice = fixture_choice or "game_3"
    cfg = REUNION_FIXTURES.get(choice) or REUNION_FIXTURES["game_3"]
    _run_reunion(
        sink,
        fixture_filename=cfg["fixture_filename"],
        finalist_scores=cfg["finalist_scores"],
        elimination_order=cfg["elimination_order"],
        human_name=human_name,
        phase_number=cfg["phase_number"],
    )


def run_demo_pd_finale(sink, human_name: str = None, fixture_choice: str = None):
    """Prisoner's Dilemma Finale: two finalists, split-or-steal endgame."""
    from core.bootstrap import create_engine
    from core.levels.phase_recipe import PhaseRecipe

    choice = fixture_choice or "finn_lsp"
    cfg = PD_FINALE_FIXTURES.get(choice) or PD_FINALE_FIXTURES["finn_lsp"]

    finalist_names = set(cfg["finalist_scores"].keys())
    agent_state = load_fixture(cfg["fixture_filename"])
    all_names = list(agent_state.keys())
    agents = create_agents_from_names(all_names)
    engine = create_engine(sink, agents=agents, allow_rename=False)
    if cfg["phase_number"]:
        engine.game_board.phase_number = cfg["phase_number"]
        
    if human_name:
        add_human(human_name, engine, is_dead=True)
        
    engine.initialiseGameBoard()
    agents_by_name = {a.name: a for a in engine.agents}
    for name, score in cfg["finalist_scores"].items():
        engine.game_board.agent_scores[name] = score
    apply_agent_state(agents_by_name, agent_state)
    
    for agent in list(engine.agents):
        if agent.name not in finalist_names:
            engine.eliminate_player(agent)
            
    phase_recipe_factory = ScriptedPhaseFactory([PhaseRecipe(rounds=[GamePrisonersDilemmaFinale])])

    engine.gameplay_config.pd_pairing_method = engine.gameplay_config.pd_pairing_choice_all
    engine.phase_factory = phase_recipe_factory
    #phase = PhaseRecipe(rounds=[GamePrisonersDilemmaFinale])
    #engine._dev_test_phase = phase
    engine.run_phase_loop()
    #engine.phase_runner.run_phase(phase)


def run_demo_game(sink, human_name: str = None, fixture_choice: str = None):
    """Game Phase: 11 real players, mid-game Knives + Vote round."""
    from core.levels.phase_recipe import PhaseRecipe
    from gameplay_management.eliminations.voting_bottom_two import VoteBottomTwo

    scores = {
        "Aang": 12, "Michael Jackson": 10, "HAL 9000": 9,
        "Jo March": 12, "Lady Macbeth": 11, "Lady Diana": 13,
        "Morty Smith": 2, "Amy March": 12, "Benoit Blanc": 11,
        "Gollum": 9, "Buffy Summers": 10,
    }
    if human_name:
        scores[human_name] = 9

    engine, agents = setup_game_from_fixture(
        sink,
        fixture_filename="game_agent_state.json",
        scores=scores,
        phase_number=3,
        human_name=human_name,
        human_is_dead=True,
        eliminate_after=5,
    )

    cfg = engine.gameplay_config
    #cfg.pd_pairing_method = cfg.pd_pairing_choice_lowest
    #cfg.pd_pairing_method = cfg.pd_pairing_choice_none
    #cfg.pd_pairing_method = cfg.pd_pairing_choice_all
    cfg.pd_pairing_method = cfg.pd_pairing_choice_all
    cfg.vote_bottom_two_expand_ties = True
    round_count = 0
    #while len(engine.agents) > 2:
    while round_count < 1:
        round_count += 1
        phase = PhaseRecipe(rounds=[GameTargetedChoiceSteal, DiscussionRoundDirectedShort, VoteBottomTwo])
        engine.phase_runner.run_phase(phase)


DEMO_REGISTRY = {
    "reunion": run_demo_reunion,
    "pd_finale": run_demo_pd_finale,
    "game_phase": run_demo_game,
}
