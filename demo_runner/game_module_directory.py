from dataclasses import dataclass
from typing import Type

from gameplay_management.base_manager import BaseRound
from gameplay_management.eliminations.reunion_round import FinaleReunionRound
from gameplay_management.games.game_pd_finale import GamePrisonersDilemmaFinale
from gameplay_management.game_cycle.game_knives import GameKnives
from gameplay_management.game_cycle.game_circle import GameCircle
from gameplay_management.game_cycle.game_mob import GameMob
from gameplay_management.eliminations.voting_bottom_two import VoteBottomTwo
from gameplay_management.eliminations.voting_each_player import VoteEachPlayer
from gameplay_management.eliminations.voting_elect_leader import VoteElectLeader
from gameplay_management.eliminations.voting_lowest_points import VoteLowestPoints
from gameplay_management.eliminations.voting_winner_chooses import VoteWinnerChooses
from gameplay_management.games.game_rps import GameRockPaperScissors
from gameplay_management.games.game_prisoners_dilemma import GamePrisonersDilemma
from gameplay_management.games.game_guess import GameGuess
from gameplay_management.games.game_wisdom import GameWisdom
from gameplay_management.game_perform.game_perform_comedy_roast import GamePerformComedyRoast
from gameplay_management.game_perform.game_perform_sob_story import GamePerformSobStory
from gameplay_management.game_targeted.game_targeted_give_or_take import GameTargetedChoiceGiveOrTake
from gameplay_management.game_targeted.game_targeted_give import GameTargetedChoiceGive
from gameplay_management.game_targeted.game_targeted_steal import GameTargetedChoiceSteal
from gameplay_management.game_targeted.game_targeted_sacrifice import GameTargetedChoiceSacrifice


@dataclass
class ModuleEntry:
    id: str
    title: str
    module_class: Type[BaseRound]
    description: str = ""
    finale: bool = False
    game: bool = False


MODULES = [
    ModuleEntry(
        id="reunion",
        title="Reunion Finale",
        module_class=FinaleReunionRound,
        description="The eliminated jury cross-examines the finalists and votes for a winner.",
        finale=True,
    ),
    ModuleEntry(
        id="pd_finale",
        title="Prisoner's Dilemma",
        module_class=GamePrisonersDilemmaFinale,
        description="The two finalists face a split-or-steal endgame.",
        finale=True,
    ),
    ModuleEntry(
        id="knives",
        title="Knives",
        module_class=GameKnives,
        description="Players pass or plant knives each round — alliances and betrayals play out in the open.",
        game=True,
    ),
    ModuleEntry(
        id="circle",
        title="The Circle",
        module_class=GameCircle,
        description="A shooting-circle standoff — survivors split the bonus.",
        game=True,
    ),
    ModuleEntry(
        id="mob",
        title="Mob",
        module_class=GameMob,
        description="Players form mobs behind a leader and pile onto a target.",
        game=True,
    ),
    ModuleEntry(
        id="bottom_two",
        title="Bottom Two Vote",
        module_class=VoteBottomTwo,
        description="The two lowest-scoring players face the vote — the group decides who goes home.",
        game=True,
    ),
    ModuleEntry(
        id="direct_democracy",
        title="Direct Democracy",
        module_class=VoteEachPlayer,
        description="Each player votes to eliminate, the player with the most votes is removed.",
        game=True,
    ),
    ModuleEntry(
        id="elect_leader",
        title="Elect the Executioner",
        module_class=VoteElectLeader,
        description="Each player votes to elect the executioner. The leader chosen will have to choose who is going home.",
        game=True,
    ),
    ModuleEntry(
        id="lowest_points",
        title="Farewell, to thee of points so lowest",
        module_class=VoteLowestPoints,
        description="Player with the lowest points is removed from the game.",
        game=True,
    ),
    ModuleEntry(
        id="winner_chooses",
        title="The Leader Executes",
        module_class=VoteWinnerChooses,
        description="The player leading the scores will choose who leaves the game IMMEDIATELY.",
        game=True,
    ),
    ModuleEntry(
        id="rps",
        title="Rock Paper Scissors",
        module_class=GameRockPaperScissors,
        description="A really basic demo of a 1v1 game. ",
        game=True,
    ),
    ModuleEntry(
        id="pd",
        title="Prisoner's Dilemma",
        module_class=GamePrisonersDilemma,
        description="The classic social game. ",
        game=True,
    ),
    ModuleEntry(
        id="guess",
        title="Guess",
        module_class=GameGuess,
        description="Guess the correct number to win!",
        game=True,
    ),
    ModuleEntry(
        id="wisdom",
        title="Wisdom of the Crowd",
        module_class=GameWisdom,
        description="Vote on superlatives — match the crowd or win the vote to score points.",
        game=True,
    ),
    ModuleEntry(
        id="comedy_roast",
        title="Comedy Roast",
        module_class=GamePerformComedyRoast,
        description="Do your stand-up set — roast yourself, the group, or a single rival. Peers score 1-10.",
        game=True,
    ),
    ModuleEntry(
        id="sob_story",
        title="Sob Story",
        module_class=GamePerformSobStory,
        description="Each player performs, and is scored by their fellow contestants!",
        game=True,
    ),
    ModuleEntry(
        id="give_take",
        title="Give and Take",
        module_class=GameTargetedChoiceGiveOrTake,
        description="As it says on the tin really! ",
        game=True,
    ),
    ModuleEntry(
        id="give",
        title="Giver",
        module_class=GameTargetedChoiceGive,
        description="Choose a player to receive points!",
        game=True,
    ),
    ModuleEntry(
        id="steal",
        title="Stealer",
        module_class=GameTargetedChoiceSteal,
        description="Choose a player to steal points from!",
        game=True,
    ),
    ModuleEntry(
        id="sacrifice",
        title="Sacrificer",
        module_class=GameTargetedChoiceSacrifice,
        description="Use your own points to hurt another player",
        game=True,
    ),
    ModuleEntry(
        id="test",
        title="Test",
        module_class=None,
        description="test",
        game=True,
    ),
]


MODULE_MAP = {m.id: m for m in MODULES}

