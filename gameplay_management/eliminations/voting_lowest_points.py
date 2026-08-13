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

    def run_vote(self):
        self.run_voting_lowest_points_removed()
        
    def _winner_speech(self, winner):
        final_q = (f"Congrats to {winner.name}! How does it feel to be a winner? ")
        self._host_broadcast(final_q)
        self.turn_manager.respond_to(winner,
            f"React to host message: {final_q}",
            public_response_prompt="Only answer the questions- afterwards give a final speech to the fans. ",
            is_reply=True,
            broadcast=True)
       


    
    def run_voting_lowest_points_removed(self, with_pass_option: bool = False):
        lowest_players = self.get_strategic_players(self.agents, top_player = False, multiple = True)
        is_finale = len(self.agents) == 2
        
        if is_finale:
            host_string = "The time has come- our game has reached its conclusion. "
        else:
            host_string = "The time has come to say goodbye to one of our players. "
        host_string += VoteLowestPoints.rules_description_detailed(self)
        
        self.game_board.host_broadcast(host_string)

        if len(lowest_players) == 1:
            evictee = lowest_players[0]
            removal_string = (f"The player with the lowest score, who will now be removed from the competition, is... {evictee.name}.")
        else:
            evictee = random.choice(lowest_players)
            removal_string = (f"We have a tie for the lowest scoring player between {self.format_list(self._names(lowest_players))}. "
            f"At random, we have decided that the player who will be sent home is... *{evictee.name.upper()}*. ")
        
        self.game_board.host_broadcast(removal_string)
        self.eliminate_player_by_name(evictee.name)
        if is_finale:
            winner = self.agents[0]
            self._winner_speech(winner)

            if self.cfg.tutorial_mode:
                human_played = any(agent.is_human() for agent in self.agents + self.dead_agents())
                message = ""
                if human_played:
                    message = "Congrats! You win! \n" if winner.is_human() else "Sad! You lost :( \n"
                message += ("In a real elimination, vulnerable players face a group vote. Survival depends on social dynamics. \n")
                self.game_board.game_sink.output_tutorial_message(message)
                
                other_notes = "One more thing: settings can be found on the top right. 'Auto-run' and 'Animate messages' control the pace of incoming messages."
                self.game_board.game_sink.output_tutorial_message(other_notes)
                
                next_level_message = ("Next level: the 6-player game. Can you be the last player standing? ")
                self.game_board.game_sink.output_tutorial_message(next_level_message, next_level=self.cfg.next_level_id)
   
