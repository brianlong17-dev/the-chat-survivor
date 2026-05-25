from core.levels.game_designs.game_design import *
from gameplay_management.discussion_rounds.discussion_round_directed_short import DiscussionRoundDirectedShort
from gameplay_management.game_targeted.game_targeted_give import GameTargetedChoiceGive
from gameplay_management.game_targeted.game_targeted_steal import GameTargetedChoiceSteal
from gameplay_management.games.game_pd_finale import GamePrisonersDilemmaFinale


class GameDesignBeginner(GameDesign):
    
    

    
        
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
        

