
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
    
    def run_game(self):
        turn_prompt =  self.cfg.discussion_round_topic
        for player in self.simulationEngine.agents:
            self.turn_manager.take_turn(player, turn_prompt, broadcast = True)
        
    