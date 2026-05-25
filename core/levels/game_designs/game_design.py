from core.game_config import GameConfig
from core.levels.phase_description import PhaseDescription
from gameplay_management.discussion_rounds.discussion_round import DiscussionRound
from gameplay_management.discussion_rounds.discussion_round_directed import DiscussionRoundDirected
from gameplay_management.eliminations.voting_elect_leader import VoteElectLeader
from gameplay_management.discussion_rounds.introduction_round import IntroRound
from gameplay_management.discussion_rounds.interview_round import InterviewRound
from gameplay_management.games.game_prisoners_dilemma import GamePrisonersDilemma
from gameplay_management.games.game_rps import GameRockPaperScissors
from gameplay_management.games.game_guess import GameGuess
from gameplay_management.games.game_perform import GamePerformSobStory
from gameplay_management.game_targeted.game_targeted_give import GameTargetedChoiceGive
from gameplay_management.game_targeted.game_targeted_steal import GameTargetedChoiceSteal
from gameplay_management.game_targeted.game_targeted_sacrifice import GameTargetedChoiceSacrifice
from gameplay_management.eliminations.voting_bottom_two import VoteBottomTwo
from gameplay_management.eliminations.voting_each_player import VoteEachPlayer
from gameplay_management.eliminations.voting_lowest_points import VoteLowestPoints
from gameplay_management.immunities.highest_points_immunity import HighestPointsImmunity
from gameplay_management.immunities.wildcard_immunity import WildcardImmunity
from gameplay_management.eliminations.reunion_round import FinaleReunionRound
from gameplay_management.game_cycle.game_circle import GameCircle
from gameplay_management.game_cycle.game_knives import GameKnives
from gameplay_management.game_cycle.game_mob import GameMob



class GameDesign:
    
    @classmethod
    def initialise_game_config(cls, config):
        config.intro_round_welcome_message = cls.intro()
        config.intro_round_QA = cls.intro_QA()
        config.phase_one_intro = cls.phase_intro()

    @classmethod
    def intro(cls):
        return None

    @classmethod
    def intro_QA(cls):
        return None

    @classmethod
    def phase_intro(cls):
        return None
    
    
    
    @classmethod
    def make_phase(cls, pre_game_discussion_rounds, game, pre_vote_discussion_rounds,
                   vote, post_vote_discussion_rounds, immunity_types, config_mutations=None):
        rounds = []

        for _ in range(pre_game_discussion_rounds):
            rounds.append(DiscussionRound)
        if game:
            rounds.append(game)

        for _ in range(pre_vote_discussion_rounds):
            rounds.append(DiscussionRound)
        if vote:
            rounds.append(vote)
        for _ in range(post_vote_discussion_rounds):
            rounds.append(DiscussionRound)

        return PhaseDescription(rounds=rounds, immunity_types=immunity_types, config_mutations=config_mutations or [])
        
     
    
    @classmethod 
    def human_only_game_intro(cls):
        return ""
        topicString = (f"Welcome to the arena... You were brought here to discover the best among you. You are all chosen because of your particular characteristics... "
                   "Charisma... uniqueness... nerve... talent. You will play among yourselves to earn points. "
                   "But the person choosing the winner... will be you. "
                   "You will compete to gain points. These points will save help you at the voting round. "
                   "At the voting round, you will choose, who to save... or who to send home. "
                   "We need to find the greatest among you. Your goal? IS TO WIN!"
        )
        return topicString


