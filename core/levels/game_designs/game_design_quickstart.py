from core.levels.game_designs.game_design import *
from gameplay_management.discussion_rounds.discussion_settings import DiscussionLoop, DiscussionRoundSettings
from gameplay_management.discussion_rounds.introduction_round_empty import IntroRoundEmpty


class GameDesignQuickStart(GameDesign):
    """Minimal Level 1: two players, one rock-paper-scissors game, lowest score eliminated."""

    @classmethod
    def min_players(cls) -> int:
        return 2

    @classmethod
    def max_players(cls) -> int:
        return 2

    @classmethod
    def intro_tutorial_messages(cls, human_name=None, opponent_names=None): #
        if not human_name:
            human_name = "Human"
            cant_see_string = "the players won't see them"
            first = "First a quick introduction between the players, then they'll face off"
        else:
            opponent_name = opponent_names[0]
            cant_see_string = f"{opponent_name} won't see them"
            first = f"First a quick introductory chat with {opponent_name}, then you'll face off"

        return [
            f"Hello {human_name}! Welcome to the tutorial game. ",
            f"These Golden tutorial messages are just for you — {cant_see_string}. \nSpeaking of the game: you'll see three round types today — Discussion, Game, and Elimination. ",
            #"The mini-game today will be Rock Paper Scissors. Ready?",
        ]
        
    @classmethod
    def human_only_game_intro(cls):
        return ("Hello human! This is a demonstration game. \n"
        "It shows the basic format- discussion, game, elimination.")
    
    @classmethod
    def pre_eviction_message(cls):
        return "A JOURNEY COMES TO AN END. THE RESULTS ARE FINAL. {victim_name}, IT'S TIME TO SAY... *GOODBYE.*  ☠ ☠ ☠ "
    
    @classmethod
    def post_eviction_system_message(cls):
        return "{victim_name} has been removed from the chat."
    

    @classmethod
    def get_phase_description(cls, phase_number, agent_number, cfg: GameConfig):
        if agent_number == 2:
            cfg.tutorial_mode = True
            cfg.next_level_id = "beginner"
            cfg.set_discussion_settings(DiscussionRoundSettings(loops=[
                DiscussionLoop(
                    turn_prompt="Say hello! If you don't know them, introduce yourself- if you already know them, you can greet them. ",
                    host_message ="Welcome to our players! Why doesn't everyone introduce themselves? Or have you two already met? ",
                    additional_thought_prompt="Do you recognise the other player - {opponent_names} - do you already know them?",
                    
                ),
                DiscussionLoop(
                    turn_prompt="Reply and continue the conversation. DO NOT REPEAT ANYTHING FROM YOUR PREVIOUS TURN. ",
                    human_turn_tutorial_message="This game is all about manipulation and influence. The upcoming round is Rock, Paper, Scissors... can you use your next turn to influence {opponent_name}'s decision? "
                ),
                DiscussionLoop(
                    turn_prompt="Reply and continue the conversation. DO NOT REPEAT ANYTHING FROM YOUR PREVIOUS TURN. ",
                    cut_human_turn=True,
                ),
            ]))
            
            rounds = [IntroRoundEmpty, DiscussionRound, GameRockPaperScissors, VoteLowestPoints]
            return PhaseDescription(rounds=rounds, should_summarise_phase=False)

