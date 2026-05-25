from core.game_config import GameConfig
from core.levels.game_designs.game_design import GameDesign
from core.levels.phase_description import PhaseDescription
from gameplay_management.discussion_rounds.discussion_round import DiscussionRound
from gameplay_management.discussion_rounds.discussion_round_directed import DiscussionRoundDirected
from gameplay_management.discussion_rounds.interview_round import InterviewRound
from gameplay_management.eliminations.reunion_round import FinaleReunionRound
from gameplay_management.eliminations.voting_bottom_two import VoteBottomTwo
from gameplay_management.eliminations.voting_each_player import VoteEachPlayer
from gameplay_management.eliminations.voting_elect_leader import VoteElectLeader
from gameplay_management.game_cycle.game_circle import GameCircle
from gameplay_management.game_cycle.game_mob import GameMob
from gameplay_management.game_targeted.game_targeted_give import GameTargetedChoiceGive
from gameplay_management.game_targeted.game_targeted_steal import GameTargetedChoiceSteal
from gameplay_management.games.game_perform import GamePerformSobStory
from gameplay_management.games.game_prisoners_dilemma import GamePrisonersDilemma
from gameplay_management.games.game_rps import GameRockPaperScissors
from gameplay_management.immunities.highest_points_immunity import HighestPointsImmunity
from gameplay_management.immunities.wildcard_immunity import WildcardImmunity


class GameDesignDefault(GameDesign):

    @classmethod
    def get_phase_description(cls, phase_number, agent_number, cfg: GameConfig, voting=None, incl_games=True, speed=1):
        return cls.get_phase_compelling(phase_number, agent_number, cfg, voting, incl_games, speed)

    @classmethod
    def _phases(cls):
        return [
            None,  # phase 0 unused

            #rich foes IntroRound, DiscussionRound,
            PhaseDescription(rounds=[DiscussionRoundDirected, InterviewRound, DiscussionRoundDirected,  GameRockPaperScissors, VoteElectLeader]),
            PhaseDescription(rounds=[GameTargetedChoiceGive, VoteBottomTwo]),
            PhaseDescription(rounds=[GameTargetedChoiceSteal, VoteBottomTwo]),
            PhaseDescription(rounds=[GameCircle, DiscussionRound, VoteBottomTwo]),
            PhaseDescription(rounds=[GameMob]),


            #we need someting here to introduce the game
            PhaseDescription(rounds=[GameRockPaperScissors, VoteElectLeader]),
            #PhaseDescription(rounds=[GameGuess, VoteElectLeader],  config_mutations=[("set_guess_range", [3])]),
            PhaseDescription(rounds=[GameCircle, DiscussionRound, VoteBottomTwo]),
            PhaseDescription(rounds=[GameCircle, DiscussionRound, VoteBottomTwo]),
            cls.mid_phase(GameTargetedChoiceGive, VoteEachPlayer, [HighestPointsImmunity, WildcardImmunity]),
            cls.mid_phase(GameTargetedChoiceSteal, VoteBottomTwo, []),
            cls.mid_phase(GamePerformSobStory, VoteBottomTwo, []),
            cls.mid_phase(GamePerformSobStory, VoteBottomTwo, []),
            cls.mid_phase(GamePrisonersDilemma, VoteBottomTwo, [],
                          config_mutations=[("set_pd_pairing_lowest", [])]),

        ]

    @classmethod
    def get_phase_compelling(cls, phase_number, agent_number, cfg: GameConfig, voting=None, incl_games=True, speed=1):
        cfg.vote_bottom_two_expand_ties = True

        if agent_number == 2:
            return  PhaseDescription(rounds=[FinaleReunionRound])
        if agent_number == 3:
            return cls.mid_phase(GamePrisonersDilemma, VoteBottomTwo, [],
                                 config_mutations=[("set_pd_pairing_all", [])])

        phases = cls._phases()
        if phase_number < len(phases):
            return phases[phase_number]
        return phases[-1]
