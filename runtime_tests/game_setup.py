"""
Shared setup helpers for demo runners and runtime tests.
"""
import json
import os

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")


def load_fixture(filename: str) -> dict:
    with open(os.path.join(FIXTURES_DIR, filename)) as f:
        return json.load(f)


def apply_agent_state(agents: dict, agent_state: dict):
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


def create_agents_from_names(names):
    from core.bootstrap import create_agent
    return [create_agent(name) for name in names]


def add_human(human_name, engine, is_dead=False):
    from agents.human_player import Human
    human = Human(human_name)
    agent_to_replace = next((a for a in engine.agents if a.name == human_name), None)
    if agent_to_replace:
        idx = engine.agents.index(agent_to_replace)
        engine.agents[idx] = human
    else:
        if is_dead:
            human.game_over = True
            engine.dead_agents.append(human)
        else:
            engine.agents.append(human)
            engine.game_board.add_agent_state(human.name)


def setup_game_from_fixture(
    sink,
    fixture_filename: str,
    scores: dict,
    phase_number: int = None,
    human_name: str = None,
    human_is_dead: bool = False,
    eliminate_after: int = None,
):
    """
    Load a fixture, wire up agents, set scores, and return a ready-to-run engine.
    eliminate_after: if set, eliminates all agents beyond this index after setup.
    """
    from core.bootstrap import create_engine

    agent_state = load_fixture(fixture_filename)
    all_names = list(agent_state.keys())
    agents = create_agents_from_names(all_names)

    engine = create_engine(sink, agents=agents, allow_rename=False)

    if phase_number is not None:
        engine.game_board.phase_number = phase_number

    if human_name:
        add_human(human_name, engine, is_dead=human_is_dead)

    engine.initialiseGameBoard()
    agents_by_name = {a.name: a for a in engine.agents}

    for name, score in scores.items():
        engine.game_board.agent_scores[name] = score

    if human_name and human_name not in scores:
        engine.game_board.agent_scores[human_name] = 0

    apply_agent_state(agents_by_name, agent_state)

    if eliminate_after is not None:
        for agent in engine.agents[eliminate_after:]:
            engine.eliminate_player(agent)

    return engine, agents_by_name
