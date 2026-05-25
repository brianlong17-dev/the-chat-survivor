from core.levels.game_designs.game_design import *
from gameplay_management.discussion_rounds.discussion_round_directed_short import DiscussionRoundDirectedShort
from gameplay_management.game_targeted.game_targeted_give import GameTargetedChoiceGive
from gameplay_management.game_targeted.game_targeted_steal import GameTargetedChoiceSteal
from gameplay_management.games.game_pd_finale import GamePrisonersDilemmaFinale


class GameDesignBeginner(GameDesign):
    
    
    @classmethod
    def intro(cls):
        intro = ("So, as you know, you're here to play the game. "
        "You're gonna do great. Each phase has a mini game to earn points, "
        "and at the end of each phase, the players at the bottom of the board will face elimination. "
        "Each player has a vote, so you're gonna need friends- and common-enemies. "
        "Even if you have alliances, remember, at the end there can only be one player standing. "
        "Are you ready? Do you have what it takes? ")
        return intro

    @classmethod
    def intro_QA(cls):
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
        
    @classmethod
    def phase_intro(cls):
        return None
    
    @classmethod
    def get_phase_description(cls, phase_number, agent_number, cfg: GameConfig, voting=None, incl_games = True, speed=1):
        cfg.vote_bottom_two_expand_ties = True
        
        if agent_number == 6: #IntroRound, DiscussionRoundDirectedPreVote
            rounds = [IntroRound, DiscussionRoundDirected, GamePrisonersDilemma, DiscussionRoundDirectedShort , VoteBottomTwo]
            cfg.set_directed_discussion_group_allowed(False)
            cfg.set_pd_pairing_random()
            return PhaseDescription(rounds=rounds) 
        
        if agent_number == 5:
            rounds = [GameTargetedChoiceGive, DiscussionRoundDirectedShort, VoteBottomTwo]
            cfg.set_directed_discussion_group_allowed(True)
            return PhaseDescription(rounds=rounds)
        
        if agent_number == 4:
            rounds = [GameTargetedChoiceSteal, DiscussionRoundDirectedShort, VoteBottomTwo]
            return PhaseDescription(rounds=rounds)
            
        if agent_number == 3:
            rounds = [GamePrisonersDilemma, DiscussionRoundDirectedShort, VoteBottomTwo]
            cfg.set_pd_pairing_all()
            cfg.set_directed_discussion_group_allowed(True)
            return PhaseDescription(rounds=rounds)
        
        
        if agent_number == 2:
            rounds = [GamePrisonersDilemmaFinale]
            cfg.set_pd_pairing_all()
            return PhaseDescription(rounds=rounds)
        

