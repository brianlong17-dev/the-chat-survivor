"""
Demo runner functions — callable versions of the runtime test scripts.
Each function accepts a sink (any GameEventSink) and an optional human_name.
"""
import sys
import os

from gameplay_management.game_targeted.game_targeted_steal import GameTargetedChoiceSteal
from gameplay_management.game_perform.game_perform_sob_story import GamePerformSobStory
from gameplay_management.game_perform.game_perform_comedy_roast import GamePerformComedyRoast
from gameplay_management.games.game_pd_finale import GamePrisonersDilemmaFinale
from gameplay_management.eliminations.voting_lowest_points import VoteLowestPoints
from tests.helpers.testing_game_design import TestingGameDesign

from gameplay_management.game_targeted.game_targeted_give_or_take import GameTargetedChoiceGiveOrTake

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gameplay_management.discussion_rounds.discussion_round import DiscussionRound
from gameplay_management.discussion_rounds.discussion_round_directed_short import DiscussionRoundDirectedShort

from gameplay_management.games.game_prisoners_dilemma import GamePrisonersDilemma
from runtime_tests.game_setup import (
    load_fixture, apply_agent_state,
    add_human, setup_game_from_fixture,
)



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
    "quirrell_morty_pre_finale": {
        "fixture_filename": "quirrell_morty_pre_finale.json",
        "finalist_scores": {"Professor Quirrell": 19, "Morty Smith": 17},
        "elimination_order": ["Lady Macbeth", "Amy March", "Logan Roy", "Gollum", "Lumpy Space Princess", "Elle Woods"],
        "phase_number": 8,
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
    "quirrell_morty_pre_finale": {
        "fixture_filename": "quirrell_morty_pre_finale.json",
        "finalist_scores": {"Professor Quirrell": 19, "Morty Smith": 17},
        "phase_number": 8,
    },
    "danny_diana_pre_finale": {
        "fixture_filename": "danny_diana_pre_finale.json",
        "finalist_scores": {"Danny Healy-Rae": 22, "Lady Diana": 17},
        "phase_number": 7,
    },
}


def run_demo_reunion(sink, api_client, human_name: str = None, fixture_choice: str = None):
    
    from core.bootstrap import create_engine
    from tests.helpers.testing_game_design import TestingGameDesign
    from core.levels.phase_description import PhaseDescription
    from gameplay_management.eliminations.reunion_round import FinaleReunionRound

    choice = fixture_choice or "game_3"
    cfg = REUNION_FIXTURES.get(choice) or REUNION_FIXTURES["game_3"]
    fixture_filename=cfg["fixture_filename"]
    finalist_scores=cfg["finalist_scores"]
    elimination_order=cfg["elimination_order"]
    human_name=human_name
    phase_number=cfg["phase_number"]

    agent_state = load_fixture(fixture_filename)
    all_names = list(agent_state.keys())

    engine = create_engine(sink, game_design=TestingGameDesign(), names=all_names, populate_agents=False, api_client=api_client)
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

    phase = PhaseDescription(rounds=[FinaleReunionRound], should_summarise_phase=False)
    engine.phase_runner.run_phase(phase)


def run_demo_pd_finale(sink, api_client, human_name: str = None, fixture_choice: str = None):
    """Prisoner's Dilemma Finale: two finalists, split-or-steal endgame."""
    from core.bootstrap import create_engine
    from core.levels.phase_description import PhaseDescription

    choice = fixture_choice or "finn_lsp"
    cfg = PD_FINALE_FIXTURES.get(choice) or PD_FINALE_FIXTURES["finn_lsp"]

    finalist_names = set(cfg["finalist_scores"].keys())
    agent_state = load_fixture(cfg["fixture_filename"])
    all_names = list(agent_state.keys())
    
    game_design = TestingGameDesign([PhaseDescription(rounds=[GamePrisonersDilemmaFinale], should_summarise_phase=False)])

    engine = create_engine(sink, game_design=game_design, names=all_names, 
                           populate_agents=False, api_client=api_client)

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
    
    engine.gameplay_config.pd_pairing_method = engine.gameplay_config.pd_pairing_choice_all
    
   

    #phase = PhaseDescription(rounds=[GamePrisonersDilemmaFinale])
    #engine._dev_test_phase = phase
    engine.run_phase_loop()
    #engine.phase_runner.run_phase(phase)


def run_demo_game(sink, api_client, human_name: str = None, fixture_choice: str = None):
    """Game Phase: 11 real players, mid-game round dev testing."""
    from core.levels.phase_description import PhaseDescription
    from gameplay_management.eliminations.voting_bottom_two import VoteBottomTwo
    from gameplay_management.eliminations.voting_winner_chooses import VoteWinnerChooses
    from gameplay_management.games.game_guess import GameGuess
    from gameplay_management.game_cycle.game_knives import GameKnives
    from gameplay_management.game_cycle.game_circle import GameCircle
    from gameplay_management.game_cycle.game_mob import GameMob
    from gameplay_management.games.game_wisdom import GameWisdom
    from gameplay_management.eliminations.voting_elect_leader2 import VoteElectLeader2

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
        api_client,
        fixture_filename="game_agent_state.json",
        scores=scores,
        phase_number=3,
        human_name=human_name,
        human_is_dead=True,
        eliminate_after=8,
    )

    cfg = engine.gameplay_config
    #cfg.pd_pairing_method = cfg.pd_pairing_choice_lowest
    #cfg.pd_pairing_method = cfg.pd_pairing_choice_none
    #cfg.pd_pairing_method = cfg.pd_pairing_choice_all
    cfg.optional_responses_in_use = True
    cfg.pd_pairing_method = cfg.pd_pairing_choice_all
    cfg.vote_bottom_two_expand_ties = True

    #phase = PhaseDescription(rounds=[GameTargetedChoiceGiveOrTake], should_summarise_phase=False)
    #phase = PhaseDescription(rounds=[GameWisdom], should_summarise_phase=False)
    #phase = PhaseDescription(rounds=[GameKnives, VoteWinnerChooses], should_summarise_phase=False)
    phase = PhaseDescription(rounds=[VoteElectLeader2], should_summarise_phase=False)
    #phase = PhaseDescription(rounds=[GameKnives, VoteBottomTwo], should_summarise_phase=False)
    # phase = PhaseDescription(rounds=[GameCircle, VoteBottomTwo], should_summarise_phase=False)
    #phase = PhaseDescription(rounds=[GamePerformComedyRoast, VoteLowestPoints, GamePerformComedyRoast], should_summarise_phase=False)

    engine.phase_runner.run_phase(phase)
    engine.api_client.print_and_write_summary()


DEMO_REGISTRY = {
    "reunion": run_demo_reunion,
    "pd_finale": run_demo_pd_finale,
    "game_phase": run_demo_game,
}
