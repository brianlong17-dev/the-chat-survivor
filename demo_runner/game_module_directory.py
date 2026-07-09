from dataclasses import dataclass
from typing import Type

from gameplay_management.base_manager import BaseRound
from gameplay_management.eliminations.reunion_round import FinaleReunionRound
from gameplay_management.games.game_pd_finale import GamePrisonersDilemmaFinale
from gameplay_management.game_cycle.game_knives import GameKnives
from gameplay_management.game_cycle.game_circle import GameCircle
from gameplay_management.game_cycle.game_mob import GameMob
from gameplay_management.eliminations.voting_bottom_two import VoteBottomTwo


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
]

MODULE_MAP = {m.id: m for m in MODULES}

