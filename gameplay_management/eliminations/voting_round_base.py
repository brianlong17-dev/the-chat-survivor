from collections import Counter
from typing import List, Optional, Sequence
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
    
    
    def _validate_immunity(self, immunity_players: Optional[Sequence[str]]) -> list[str]:
        #Tosses out immunity if all players are immune? 
        immunity_all_players_reset = (
            "All players have immunity this round! This means... NO ONE HAS IMMUNITY. You are all again at risk of being voted out."
        )
        if immunity_players is None:
            return []
        immunity_players = list(dict.fromkeys(immunity_players))
        if len(self.simulationEngine.agents) == len(immunity_players):
            
            host_message = immunity_all_players_reset
            self.game_board.host_broadcast(host_message)
            immunity_players = []
        return immunity_players
       
    def _facing_the_vote_string(self, players_up_for_elimination: Sequence[str]):
        players_up_for_elimination_string = (
            f"\nThe following players are up for elimination:\n *{self.format_list(players_up_for_elimination)}*"
        )
        return players_up_for_elimination_string
    
    def immunity_string(self, immunity_players: Sequence[str], players_up_for_elimination: Sequence[str]) -> str:
        immunity_string = ""
        immunity_players_prefix = (
        "The following players have immunity, and cannot be voted for to leave in this round of voting:"
        )
        if immunity_players:
            immunity_string = (
                f"{immunity_players_prefix}\n"
                f" {', '.join(immunity_players)}.\n"
            )
        
        return f"{immunity_string}\n"
            

    def _players_up_for_elimination(self, immunity_players: Optional[Sequence[str]]) -> List['AbstractAgenticPlayer']:
        immunity_players = immunity_players or []
        return  [a for a in self.simulationEngine.agents if a.name not in immunity_players]
        
    ###############
    #   Logic     #
    ###############
    
    def _handle_vote_response(self, agent, vote_response):
        actual_vote = self.turn_manager._get_target_name_from_response(vote_response)
        self.turn_manager._output_response(agent, vote_response, is_reply=True, pre_message_choice_reveal=self.TARGET_NAME_FIELD)
        self._update_voting_widget(agent.name, actual_vote or "—")
        return actual_vote 
        
