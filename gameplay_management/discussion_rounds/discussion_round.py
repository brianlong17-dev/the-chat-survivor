
from gameplay_management.discussion_rounds.discussion_base_round import DiscussionBaseRound

class DiscussionRound(DiscussionBaseRound):

    @classmethod
    def display_name(cls, cfg):
        return "Discussion Round"

    @classmethod
    def rules_description(cls, cfg):
        return "Chat and strategise"

    def run_round(self):
        settings = self.cfg.get_discussion_settings()
        for loop in settings.loops:
            if loop.host_message:
                self._host_broadcast(loop.host_message)
            for player in self.simulationEngine.agents:
                formatted_thought_prompt = loop.formatted_additional_thought_prompt(self.format_list(self._opponent_names(player)))

                self.turn_manager.take_turn(
                    player,
                    loop.turn_prompt,
                    public_response_prompt=loop.public_response_prompt,
                    additional_thought_nudge=formatted_thought_prompt,
                    broadcast=True,
                )
        self.cfg.discussion_index += 1

