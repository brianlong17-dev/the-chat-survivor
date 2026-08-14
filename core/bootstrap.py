import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv(override=True)

from agents.character_generation.characterGeneration import CharacterGenerator
from agents.game_host.game_host import GameMaster
from core.gameboard import GameBoard
from core.sinks.console_sink import ConsoleGameEventSink
from core.simulation_engine import SimulationEngine
from agents.agentic_player_v2.agentic_player import AgenticPlayer
from agents.human_player import Human

@dataclass
class GenerateAgentsDescription:
    names: list[str]
    models: dict[str, str] | None = None
    allow_rename: bool = True


    
def create_engine(game_sink, game_design, human_player_name = None, names=None,
        allow_rename = True, api_client=None, populate_agents=True, agentic_player_classes=None,
        agent_models=None, generate_agents_in_game=False):

    game_master = GameMaster(api_client = api_client)
    game_board = GameBoard(game_sink)
    generator = CharacterGenerator(game_sink, api_client = api_client, agentic_player_classes=agentic_player_classes)


    agents, generate_agents_description = _build_agents(game_design, generator, names, human_player_name,
                            allow_rename, api_client, populate_agents, agent_models, generate_agents_in_game)

    return SimulationEngine(agents=agents, game_board=game_board, game_master=game_master, generator=generator,
                            game_design=game_design, api_client=api_client,
                            generate_agents_description=generate_agents_description)


def _build_agents(game_design, generator, names, human_player_name, allow_rename, api_client,
                   populate_agents, agent_models, generate_agents_in_game):

    if populate_agents and not generate_agents_in_game:
        agents = generator.generate_agents_from_names(names, agent_models = agent_models, allow_rename = allow_rename,)
    else:
        #Demo case - agents populated from fixture data
        agents = [create_blank_agent(name, api_client) for name in names]

    if human_player_name:
        human_player = Human(human_player_name)
        agents.append(human_player)

    agents = _clip_agents(game_design, agents)

    if generate_agents_in_game:
        generate_agents_description = GenerateAgentsDescription(names=[a.name for a in agents],
                models=agent_models, allow_rename=allow_rename)
    else:
        generate_agents_description = None

    return agents, generate_agents_description


def create_blank_agent(name, api_client):
    return AgenticPlayer(name, '', api_client = api_client)

def _clip_agents(game_design, agents):

    max_players, min_players = game_design.max_players(), game_design.min_players()


    if len(agents) > max_players:
        print(f"[WARNING] create_engine: clipped {len(agents)} agents to {max_players}")
        agents = agents[:max_players]
    if len(agents) < min_players:
        raise ValueError(f"create_engine: need at least {min_players} players, got {len(agents)}")
    
    return agents