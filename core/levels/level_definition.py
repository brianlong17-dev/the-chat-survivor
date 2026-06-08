from __future__ import annotations
from dataclasses import dataclass
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from core.levels.game_designs.game_design import GameDesign


@dataclass
class LevelDefinition:
    id: str
    name: str
    description: str
    token_budget: int
    game_design: Type[GameDesign]
    locked: bool = True

    @property
    def min_players(self) -> int:
        return self.game_design.min_players()

    @property
    def max_players(self) -> int:
        return self.game_design.max_players()
    
