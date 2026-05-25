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
    min_players: int
    max_players: int
    game_design: Type[GameDesign]
    locked: bool = True
