from __future__ import annotations
from typing import TYPE_CHECKING

from core.game_config import GameConfig
from core.phase_runner import PhaseRunner
import uuid
from datetime import datetime, timezone

if TYPE_CHECKING:
    from agents.character_generation.characterGeneration import CharacterGenerator
    from core.levels.game_designs.game_design import GameDesign
    from agents.game_host.game_host import GameMaster
    from core.gameboard import GameBoard
    from agents.abstract_agentic_player import AbstractAgenticPlayer
    
 
    
class SimulationEngine:
    def __init__(self, agents: list[AbstractAgenticPlayer], game_board: GameBoard, game_master: GameMaster, generator: CharacterGenerator,
                 game_design: GameDesign, api_client):

        self.game_master = game_master
        self.game_design = game_design
        self.api_client = api_client

        self.game_board = game_board
        self.generator = generator
        self.gameplay_config = GameConfig()
        self.game_design.initialise_game_config(self.gameplay_config)
        self.phase_runner = PhaseRunner(self)
        
        
        self.agents = agents
        self._select_debug_targets()
        self.dead_agents = []
        
        self.game_id = self._generate_game_id()
        self.api_client.game_id = self.game_id
        
    
    @property
    def human_agent(self):
        return next((agent for agent in self.agents if agent.is_human()), None)

    @property
    def non_human_agents(self):
        return [agent for agent in self.agents if not agent.is_human()]

    def _generate_game_id(self):
        return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
            
    def initialiseGameBoard(self):
        self.game_board.initialize_agents(self.agents)
        self.game_board.phase_runner = self.phase_runner
        
    def eliminate_player(self, agent):
        agent.game_over = True
        self.agents.remove(agent)
        self.dead_agents.append(agent)
        self.game_board.remove_agent_state(agent.name)
        
    def _select_debug_targets(self):
        if not self.api_client._mock_output:
            for agent in self.agents:
                agent.debug_log = True
                    

    def run(self):
        self.initialiseGameBoard()
        self.run_phase_loop()
    
    def run_demo_phase(self, phase):
        self.phase_runner.run_phase(phase)
        self.api_client.print_and_write_summary()
        
    def run_phase_loop(self):
        while len(self.agents) > 1 and not self.game_board.game_over:
            phase = self.game_design.get_phase_description(self.game_board.phase_number + 1, len(self.agents), self.gameplay_config)
            self.phase_runner.run_phase(phase)
        #------------Fin------------#
        self.game_board.game_sink.on_game_over([agent.name for agent in self.agents])
        self.api_client.print_and_write_summary()
        self._post_game_interview()
        
    def _post_game_interview(self):
        pass
           
