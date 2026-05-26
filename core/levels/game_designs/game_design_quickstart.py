from core.levels.game_designs.game_design import *


class GameDesignQuickStart(GameDesign):
    """Minimal Level 1: two players, one rock-paper-scissors game, lowest score eliminated."""
    
    @classmethod 
    def human_only_game_intro(cls):
        return "This is a demonstration game- a round of Rock Paper Scissors, and the loser gets eliminated! "
    
    @classmethod
    def pre_eviction_message(cls):
        return "A JOURNEY COMES TO AN END. THE RESULTS ARE FINAL. {victim_name}, IT'S TIME TO SAY... *GOODBYE.*  ☠ ☠ ☠ "
    
    @classmethod
    def post_eviction_system_message(cls):
        return "{victim_name} has been removed from the chat."

    @classmethod
    def get_phase_description(cls, phase_number, agent_number, cfg: GameConfig, voting=None, incl_games=True, speed=1):
        if agent_number == 2:
            cfg.discussion_round_topic = "Say hello and introduce yourself! "
            cfg.discussion_round_loops = 2
            rounds = [DiscussionRound, GameRockPaperScissors, VoteLowestPoints]
            discussion_round_host_intros = ["Welcome to our players! Why doesn't everyone introduce themselves? "]
            return PhaseDescription(rounds=rounds, discussion_round_host_intros=discussion_round_host_intros)
