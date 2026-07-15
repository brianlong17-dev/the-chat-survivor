from typing import Optional, Sequence
import random
from gameplay_management.eliminations.voting_round_base import VotingRoundBase


class VoteLowestPoints(VotingRoundBase):
    @classmethod
    def display_name(cls, cfg):
        return "Farewell, to thee of points so lowest"

    @classmethod
    def rules_description(cls, cfg):
        return "Player with the lowest points is removed from the game"
    
    def rules_description_detailed(self):
        #in future, potential tie breaker can be in config
        return (f"The player with the lowest score will now be removed from the game. "
                f"In the event of a tie, a player will be chosen at random.\n\n")

    def run_vote(self, immunity_players: Optional[Sequence[str]]):
        self.run_voting_lowest_points_removed(immunity_players)
        
    def _winner_speech(self, winner):
        final_q = (f"Congrats to {winner.name}! How does it feel to be a winner? ")
        self._host_broadcast(final_q)
        self.turn_manager.respond_to(winner,
            f"React to host message: {final_q}",
            public_response_prompt="Only answer the questions- afterwards give a final speech to the fans. ",
            is_reply=True,
            broadcast=True)
       
        
    def run_voting_lowest_points_removed(self, immunity_players: Optional[Sequence[str]] = None, with_pass_option: bool = False):
        immunity_players = self._validate_immunity(immunity_players)
        players_up_for_elimination = self._players_up_for_elimination(immunity_players)
        lowest_players = self.get_strategic_players(players_up_for_elimination, top_player = False, multiple = True)
        is_finale = len(self.agents) == 2
        
        #TODO potentially, there can be a unified host string, alarms, plus rules.
        if is_finale:
            host_string = "The time has come- our game has come to its conclusion. "
        else:
            host_string = "The time has come to say goodbye to one of our players. "
        host_string += VoteLowestPoints.rules_description_detailed(self)
        
        self.game_board.host_broadcast(host_string)
        
        if len(lowest_players) == 1:
            evictee = lowest_players[0]
            removal_string = (f"The player with the lowest score, and who will therefore be removed from the competition, is... {evictee.name}.")
        else:
            evictee = random.choice(lowest_players)
            removal_string = (f"We have a tie for the lowest scoring player between {self.format_list(self._names(lowest_players))}. "
            f"At random, we have decided that the player who will be sent home is... *{evictee.name.upper()}*. ")
        self.game_board.host_broadcast(removal_string)
        self.eliminate_player_by_name(evictee.name)
        if is_finale:
            self._winner_speech(self.agents[0])
   
