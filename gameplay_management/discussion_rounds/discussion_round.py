
from gameplay_management.base_manager import BaseRound

class DiscussionRound(BaseRound):
    
    @classmethod
    def display_name(cls, cfg):
        return "Discussion Round"

    @classmethod
    def rules_description(cls, cfg):
        return cfg.discussion_round_topic
        
    
    @classmethod
    def is_discussion(cls):
        return True
    
    def run_game(self, host_intro=None):
        if host_intro:
            self._host_broadcast(host_intro)
        turn_prompt =  self.cfg.discussion_round_topic
        for i in range(self.cfg.discussion_round_loops):
            prompt_helper = "DO NOT REPEAT ANYTHING FROM YOUR PREVIOUS TURN. " if i > 0 else ""
            for player in self.simulationEngine.agents:
                self.turn_manager.take_turn(player, turn_prompt + prompt_helper, broadcast = True)
        
    