
from gameplay_management.base_manager import BaseRound

class IntroRound(BaseRound):
    
    @classmethod
    def display_name(cls, cfg):
        return "Intro Round"

    @classmethod
    def rules_description(cls, cfg):
        return "This is a wakeup round"
    
    
    @classmethod
    def is_private_round(cls):
        return True
    
    def default_welcome_message(self):
        return ("So, as you know, you're here to play the game. "
        "You're gonna do great. Each phase has a mini game to earn points, "
        "and at the end of each phase, the players at the bottom of the board will face elimination. "
        "Each player has a vote, so you're gonna need friends- and common-enemies. "
        "Even if you have alliances, remember, at the end there can only be one player standing. "
        "Are you ready? Do you have what it takes? ")
        
    def default_questionnaire(self):
        questions = {
            "facts" : "Tell me 4-5 specific, memorable facts about you: one embarrassing incident, one specific fear, one person from your past you're conflicted about, one thing you've never told anyone. These should feel specific enough to be true. ",
            "your_edge": "What do you have that the others don't?" ,
            "trust": "What's the worst thing you've done to someone who trusted you?",
            "values": "What traits do you most value in an ally? In a friend or in a competitor? " ,
            "dislikes": "What traits do you most dislike in a person? What type of behaviour is most unacceptable to you in a teammate? " ,
            "kindness" : "Tell me about an act of kindness shown to you that has always stayed with you. ",
            "cooperation" : "In a game where someone has to be eliminated, how do you manage co-operation? Do you try to build alliance against the most dangerous player, or do you go it alone? Or another strategy entirely? ", 
            "values_strategy" : "You walk into the room. You have thirty seconds before the game begins. You approach one person. Who is it, what do you say to them, and what are you hoping to get out of it?", 
        }
        return questions
        
    def _wake_up_player_i(self, player):
        
        player.initialising = True
        welcome_message = self.cfg.intro_round_welcome_message
        qa = self.cfg.intro_round_QA
        
        if not welcome_message:
            welcome_message = self.default_welcome_message()
            
        if not qa:
            qa = self.default_questionnaire()
            
        users = ["Host", player.name]
        conversation_id = self.game_board.log_new_restricted_conversation(users, "Host", welcome_message)
        result = self.turn_manager.take_turn(player, "Continue the conversation. ",
            model_name="basic_turn",
            public_response_prompt="This is your message of response to the host. ")
        self.game_board.log_message_to_conversation(conversation_id, player.name, result.public_response)
        self._host_back_and_forth(player, qa, conversation_id = conversation_id)
        player.initialising = False
        self.game_board.system_broadcast(f"{player.name} has entered the chat.", private = True)
        return conversation_id
            

    def run_game(self):
        self.game_board._loading_string("Preparing our players")
        conversation_ids = self._run_tasks([[agent] for agent in self._shuffled_agents() if not agent.is_human()], 
                                           self._wake_up_player_i, parallel = True)
        for conv_id in conversation_ids:
            self.game_board.close_private_conversation(conv_id)
        self.game_board._end_loading()
        #shoot one message