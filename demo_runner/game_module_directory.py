from dataclasses import dataclass
from typing import Type

from gameplay_management.base_manager import BaseRound
from gameplay_management.eliminations.reunion_round import FinaleReunionRound
from gameplay_management.games.game_pd_finale import GamePrisonersDilemmaFinale


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
]

MODULE_MAP = {m.id: m for m in MODULES}

