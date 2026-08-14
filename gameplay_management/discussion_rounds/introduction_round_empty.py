from gameplay_management.discussion_rounds.introduction_round import IntroRound

class IntroRoundEmpty(IntroRound):
    
    @classmethod
    def display_name(cls, cfg):
        return "Hello"
        
    def run_game(self):
        for player in self.non_human_agents:
            self.game_board.system_broadcast(f"{player.name} has entered the chat.", private = True)