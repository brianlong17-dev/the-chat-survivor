from __future__ import annotations
from dataclasses import dataclass
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from core.levels.phase_recipe_factory import PhaseRecipeFactory


@dataclass
class LevelDefinition:
    id: str
    name: str
    description: str
    min_players: int
    max_players: int
    phase_recipe_factory: Type[PhaseRecipeFactory]
    locked: bool = True
