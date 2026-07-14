from demo_runner.fixture_directory import FIXTURE_MAP
from demo_runner.game_module_directory import MODULE_MAP
from demo_runner.game_setup import load_fixture, apply_agent_state, add_human

from core.bootstrap import create_engine
from core.levels.phase_description import PhaseDescription
from tests.helpers.testing_game_design import TestingGameDesign
from gameplay_management.games.game_prisoners_dilemma import GamePrisonersDilemma

def run_from_frontend(module_id: str, fixture_id: str, sink, api_client, human_name: str = None):
    fixture = FIXTURE_MAP.get(fixture_id)
    if not fixture:
        raise ValueError(f"Unknown fixture: {fixture_id}")

    module = MODULE_MAP.get(module_id)
    if not module:
        raise ValueError(f"Unknown module: {module_id}")
    
    if module.module_class == None:
        phase_desc = _get_test_phase_description(module)

    else:
        phase_desc = PhaseDescription(rounds=[module.module_class], should_summarise_phase=False)

    game_design = TestingGameDesign([phase_desc])

    engine, agent_data, scores, elimination_order = _set_up_fixture(fixture_id, game_design, sink, api_client)
    _initialise_agents(engine, agent_data, scores, elimination_order, human_name=human_name)
    
    _set_up_cfg(module, engine)
    
    if module.module_class == None:
        _set_up_cfg_test(engine)
    
    if module.game:
        engine.phase_runner.run_phase(phase_desc)
    else:
        engine.run_phase_loop()

def _get_test_phase_description(module):
    return PhaseDescription(rounds=[GamePrisonersDilemma], should_summarise_phase=False)

def _set_up_cfg(module, engine):
    cfg = engine.gameplay_config
    for name, value in module.cfgs:
        getattr(cfg, name)(value)

def _set_up_cfg_test(engine):
    cfg = engine.gameplay_config
    cfg.set_pd_pairing_all()
    
    num_players = 3
    while len(engine.agents) > num_players:
        engine.eliminate_player(engine.agents[0])

def _set_up_fixture(fixture_id: str, game_design, sink, api_client):
    fixture_data = load_fixture(f"{fixture_id}.json")
    agent_data = fixture_data["agents"]
    all_names = list(agent_data.keys())

    scores = fixture_data["scores"]
    elimination_order = fixture_data.get("elimination_order", [])
    phase_number = fixture_data.get("phase_number")

    engine = create_engine(sink, game_design=game_design, names=all_names, populate_agents=False, api_client=api_client)

    if phase_number:
        engine.game_board.phase_number = phase_number

    return engine, agent_data, scores, elimination_order


def _initialise_agents(engine, agent_data, scores, elimination_order, human_name=None):
    alive_names = set(scores.keys())

    if human_name:
        add_human(human_name, engine, is_dead=True)

    engine.initialiseGameBoard()
    agents = {a.name: a for a in engine.agents}

    for name, score in scores.items():
        engine.game_board.agent_scores[name] = score
    engine.game_board.game_sink.on_points_update(dict(engine.game_board.agent_scores))

    apply_agent_state(agents, agent_data)

    for name in elimination_order:
        if name in agents:
            engine.eliminate_player(agents[name])

    for agent in list(engine.agents):
        if agent.name not in alive_names:
            engine.eliminate_player(agent)


