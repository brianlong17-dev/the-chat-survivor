from collections import Counter
from typing import Sequence
from gameplay_management.base_manager import *
   
class VotingRoundBase(BaseRound):
    dont_miss_string = "A player that receives votes but is not eliminated will receive {points} points per failed vote. "

    def __init__(self, game_board, simulationEngine):
        super().__init__(game_board, simulationEngine) 
    
    ###############
    #   Helper    #
    ###############
    
    @classmethod
    def is_vote(cls):
        return True
    
    
       
    def _facing_the_vote_string(self, players_up_for_elimination: Sequence[str]):
        players_up_for_elimination_string = (
            f"\nThe following players are up for elimination:\n *{self.format_list(players_up_for_elimination)}*"
        )
        return players_up_for_elimination_string
    
    
            
        
    ###############
    #   Logic     #
    ###############
    
    def _handle_vote_response(self, agent, vote_response):
        actual_vote = self.turn_manager._get_target_name_from_response(vote_response)
        self.turn_manager._output_response(agent, vote_response, is_reply=True, pre_message_choice_reveal=self.TARGET_NAME_FIELD)
        self._update_voting_widget(agent.name, actual_vote or "—")
        return actual_vote 
        
