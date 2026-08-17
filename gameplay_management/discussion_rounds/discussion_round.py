
from gameplay_management.discussion_rounds.discussion_base_round import DiscussionBaseRound
from gameplay_management.human_turn_form import HumanInputDescription

class DiscussionRound(DiscussionBaseRound):

    @classmethod
    def display_name(cls, cfg):
        return "Discussion Round"

    @classmethod
    def rules_description(cls, cfg):
        return "Chat and strategise"

    def _human_response_description(self):
        return HumanInputDescription(
            titles={"public_response": "Your turn to talk"},
            placeholders={"public_response": "say something"},
            underlines=["everyone hears this"],
        )
        
        
    
    def _tutorial_message(self, message, loop, hold=True):
        if not message or not self.human_player or loop.cut_human_turn:
            return
        self.game_board.game_sink.output_tutorial_message(
            message.format(opponent_name=self.non_human_agents[0].name),
            hold=hold,
        )

    def run_round(self):
        settings = self.cfg.get_discussion_settings()
        for loop in settings.loops:
            self._tutorial_message(loop.loop_start_tutorial_message, loop)

            if loop.host_message:
                self._host_broadcast(loop.host_message)
            for player in self.simulationEngine.agents:
                if player.is_human() and loop.cut_human_turn:
                    continue

                formatted_thought_prompt = loop.formatted_additional_thought_prompt(self.format_list(self._opponent_names(player)))
                
                if player.is_human():
                    self._tutorial_message(loop.human_turn_tutorial_message, loop, hold=False)
                self.turn_manager.take_turn(
                    player,
                    loop.turn_prompt,
                    public_response_prompt=loop.public_response_prompt,
                    additional_thought_nudge=formatted_thought_prompt,
                    broadcast=True,
                    human_input_description_object=loop.human_input_description or self._human_response_description(),
                )
        self.cfg.discussion_index += 1

