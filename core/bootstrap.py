import os
from dotenv import load_dotenv
load_dotenv(override=True)

from agents.character_generation.characterGeneration import CharacterGenerator
from agents.game_host import GameMaster
from core.gameboard import GameBoard
from core.sinks.console_sink import ConsoleGameEventSink
from core.simulation_engine import SimulationEngine
from agents.agentic_player import AgenticPlayer
from agents.human_player import Human


def create_blank_agent(name, api_client):
    return AgenticPlayer(name, '', api_client = api_client)


def create_engine(game_sink, game_design, human_player_name = None, number_of_players: int = 0, names=None,
                  allow_rename = True,
                  api_client=None,
                  populate_agents=True,
                  agentic_player_classes=None):

    game_master = GameMaster(api_client = api_client)
    game_board = GameBoard(game_sink)
    generator = CharacterGenerator(game_sink, api_client = api_client, agentic_player_classes=agentic_player_classes)

    if populate_agents:
        agents = generator.generate_agents_from_names(names, allow_rename = allow_rename)
    else:
        agents = [create_blank_agent(name, api_client) for name in names]


    if human_player_name:
        human_player = Human(human_player_name)
        agents.append(human_player)

    max_players, min_players = game_design.max_players(), game_design.min_players()

    if len(agents) > max_players:
        print(f"[WARNING] create_engine: clipped {len(agents)} agents to {max_players}")
        agents = agents[:max_players]
    if len(agents) < min_players:
        raise ValueError(f"create_engine: need at least {min_players} players, got {len(agents)}")


    return SimulationEngine(agents=agents, game_board=game_board, game_master=game_master, generator=generator, game_design=game_design, api_client=api_client)
