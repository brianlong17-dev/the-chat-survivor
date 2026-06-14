import os
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from gameplay_management.immunities.immunity_mechanicsMixin import ImmunityMechanicsMixin



if TYPE_CHECKING:
    from core.simulation_engine import SimulationEngine
    from core.levels.phase_description import PhaseDescription



    
class PhaseRunner:
    def __init__(self, simulation_engine: 'SimulationEngine'):
        self.simulation_engine = simulation_engine
        self.current_phase_description = None
        self.current_round_index = 0
        self._dev_mode = os.getenv("DEV_MODE", "false").lower() == "true"
        

    @property
    def game_board(self):
        return self.simulation_engine.game_board
    
    @property
    def _cfg(self):
        return self.simulation_engine.gameplay_config

    def agent_names(self):
        return [agent.name for agent in self.simulation_engine.agents]
    
    def removed_agent_names(self):
        return [agent.name for agent in self.simulation_engine.dead_agents]

    def run_vote_round_with_immunity_types(self, round_class, immunity_types):
        immune_players = []
        if immunity_types:
            for immunity_type in immunity_types:
                result = immunity_type(self.game_board, self.simulation_engine).run_immunity()
                immune_players.extend(result)
        immune_players = list(dict.fromkeys(immune_players)) #remove any dupes
        round_class(self.game_board, self.simulation_engine).run_vote(immunity_players=immune_players)

    
    def get_phase_progress_string(self):
        return self.current_phase_description.phase_progress_string(self._cfg, self.current_round_index)

    def _introduce_phase(self):
        cfg = self._cfg
        host_intro = self.current_phase_description.phase_intro_string(self.game_board.phase_number,
                                    len(self.agent_names()), cfg)
        system_phase_summary = self.current_phase_description.phase_summary_string(cfg)
        round_names = [r.display_name(cfg) for r in self.current_phase_description.rounds]
        if host_intro:
            self.game_board.host_broadcast(host_intro)
        #self.game_board.system_broadcast(system_phase_summary, private = True, border_bottom=True)
        self.game_board.game_sink.on_phase_rounds(round_names)
        
    def _introduce_game(self):
        host_intro_human_only = self.simulation_engine.game_design.human_only_game_intro()
        if host_intro_human_only:
            self.game_board.game_sink.on_game_intro(host_intro_human_only) 
            self.game_board.game_sink.on_linebreak() 
    
    def _use_round_gate(self):
        return self.game_board.first_message_send and not self._dev_mode
    
    def run_round(self, round, immunity_types):
        if self._use_round_gate():
            self.game_board.game_sink.wait_for_continue_next_round()
        self.current_round_index += 1
        self.game_board.newRound()
        self.game_board.game_sink.on_phase_round_index(self.current_round_index - 1)
        if self.current_round_index == 1:
            self._introduce_phase()
            
        if self.game_board.phase_number == 1 and self.current_round_index == 1:
            self._introduce_game()

        if round.is_vote():
            self.run_vote_round_with_immunity_types(round, immunity_types)
        else:
            round(self.game_board, self.simulation_engine).run_game()
        
        
        #self.game_board.system_broadcast(self.game_board.agent_scores)
        round_summary = self.simulation_engine.game_master.summariseRound(self.game_board)
        
        self.game_board.endRound(round_summary)
        if self._use_round_gate():
            self.game_board.game_sink._request_continue_next_round()

    def _impose_brevity_jail(self):
        for agent in self.simulation_engine.agents:
            agent.brevity_jail = False

        current_round = self.game_board.game_log.current_round
        message_lengths = {}

        for message_block in current_round.conversation_entries:
            for message_entry in message_block.message_entries:
                speaker = message_entry.speaker
                if speaker not in self.game_board.RESERVED_NAMES:
                    if speaker not in message_lengths:
                        message_lengths[speaker] = []
                    message_lengths[speaker].append(len(message_entry.public_output))

        averages = {
            speaker: sum(lengths) / len(lengths)
            for speaker, lengths in message_lengths.items()
        }

        jail_count = self.brevity_jail_count(len(self.simulation_engine.agents))
        top_talkers = sorted(averages, key=averages.get, reverse=True)[:jail_count]

        for agent in self.simulation_engine.agents:
            if agent.name in top_talkers:
                agent.brevity_jail = True
                
    @staticmethod
    def brevity_jail_count(player_count):
        if player_count <= 3:
            return 0
        return player_count // 3

    def run_phase(self, phase_description: 'PhaseDescription'):

        self.current_round_index = 0
        cfg = self._cfg
        cfg.discussion_index = 0
        for method, args in phase_description.config_mutations:
            getattr(cfg, method)(*args)

        self.current_phase_description = phase_description
        self.game_board.new_phase()
        for round in phase_description.rounds:
            self.run_round(round, phase_description.immunity_types)
            self._impose_brevity_jail()
            
        
        if phase_description.should_summarise_phase:
            agents = self.simulation_engine.agents
            if cfg.should_dead_players_summarise:
                agents = agents + self.simulation_engine.dead_agents
            
            with ThreadPoolExecutor(max_workers=min(32, len(agents))) as executor:
                for agent in agents:
                    executor.submit(agent.summarise_phase, self.game_board)
                    
            
        self.game_board.endPhase()
  
    