
from gameplay_management.base_manager import BaseRound

class DiscussionRound(BaseRound):
    
    @classmethod
    def display_name(cls, cfg):
        return "Discussion Round"
    
    @classmethod
    def rules_description(cls, cfg):
        return "Chat and strategise"

    @classmethod
    def is_discussion(cls):
        return True

    def run_game(self):
        settings = self.cfg.get_discussion_settings()
        for loop in settings.loops:
            if loop.host_message:
                self._host_broadcast(loop.host_message)
            for player in self.simulationEngine.agents:
                self.turn_manager.take_turn(
                    player,
                    loop.turn_prompt,
                    additional_thought_nudge=loop.additional_thought_prompt,
                    broadcast=True,
                )
        self.cfg.discussion_index += 1
        
    