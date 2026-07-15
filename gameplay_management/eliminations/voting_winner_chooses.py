from typing import Optional, Sequence

from gameplay_management.eliminations.voting_round_base import VotingRoundBase


class VoteWinnerChooses(VotingRoundBase):
    @classmethod
    def display_name(cls, cfg):
        return "The Leader Executes"

    @classmethod
    def rules_description(cls, cfg):
        return "The player leading the scores will choose who leaves the game IMMEDIATELY."

    def run_vote(self, immunity_players: Optional[Sequence[str]]):
        self.run_voting_winner_chooses(immunity_players)
    
    def _host_intro(self, chooser, up_for_elimination):
        return (
            f"The time has come... to choose. The player with the highest score, {chooser.name}, "
            "will now pick who will be elminated from the competition. The players at risk of being sent home are "
            f"\n*{self.format_list(up_for_elimination)}*.\n"
        )
    
        
    def run_voting_winner_chooses(self, immunity_players: Optional[Sequence[str]] = None, with_pass_option: bool = False):
        
        leading_player= self.get_strategic_players(self.simulationEngine.agents, top_player = True)[0]
        immunity_players = self._validate_immunity(immunity_players)
        up_for_elimination = [
            name for name in self.game_board.agent_names()
            if name != leading_player.name and name not in immunity_players
        ]

        self.game_board.host_broadcast(self._host_intro(leading_player, up_for_elimination))
        
        context_msg =  ("As the leading player you get to choose the player who will now leave the competition")
        choice_prompt = "Choose the player you want to remove from the competition. "
        additional_thought_nudge =  "Who do you want to send home? In terms of allies, competition, what is your best choice?"
        public_response_prompt = "What do you say as you reveal your choice?"
        
        response = self.turn_manager._targeted_turn(leading_player, up_for_elimination, choice_prompt, context_msg,
                                                    public_response_prompt, additional_thought_nudge=additional_thought_nudge)
        
        self.turn_manager._output_response(leading_player, response,
                    pre_message_choice_reveal=self.TARGET_NAME_FIELD, is_reply=True)
        self.eliminate_player_by_name(self.turn_manager._get_target_name_from_response(response))
