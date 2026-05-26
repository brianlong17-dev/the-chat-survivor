from typing import List, Optional
from core.levels.level_definition import LevelDefinition
from core.levels.game_designs.game_design import GameDesign
from core.levels.game_designs.game_design_beginner import GameDesignBeginner
from core.levels.game_designs.game_design_quickstart import GameDesignQuickStart
from gameplay_management.games.game_rps import GameRockPaperScissors
from gameplay_management.games.game_guess import GameGuess
from gameplay_management.eliminations.voting_elect_leader import VoteElectLeader


AVAILABLE_LEVELS: List[LevelDefinition] = [
    LevelDefinition(
        id="quickstart",
        name="Warm-Up",
        description="Two players, one round of rock-paper-scissors, lowest score goes home.",
        min_players=2,
        max_players=2,
        game_design=GameDesignQuickStart,
        locked=False
    ),
    LevelDefinition(
        id="beginner",
        name="First Elimination",
        description="A quick introductory game with rock-paper-scissors and one vote.",
        min_players=6,
        max_players=6,
        game_design=GameDesignBeginner,
        locked=False
    ),
    LevelDefinition(
        id="standard",
        name="The Challenge",
        description="Guess the number, discuss strategy, and vote. A classic format.",
        min_players=5,
        max_players=8,
        game_design=GameDesignBeginner,
        locked=False
    ),
    LevelDefinition(
        id="intermediate",
        name="The Arena",
        description="More discussion rounds and strategic voting. For seasoned players.",
        min_players=6,
        max_players=8,
        game_design=GameDesignBeginner,
        locked=True
    ),
]


def get_level_by_id(level_id: str) -> Optional[LevelDefinition]:
    """Retrieve a level definition by its ID."""
    for level in AVAILABLE_LEVELS:
        if level.id == level_id:
            return level
    return None

def game_design_for_id(level_id: str):
    level = get_level_by_id(level_id)
    return level.game_design 

        

def get_available_levels() -> List[LevelDefinition]:
    """Get all available levels."""
    return AVAILABLE_LEVELS


def unlock_level(level_id: str) -> bool:
    """Unlock a level by ID. Returns True if successful."""
    level = get_level_by_id(level_id)
    if level:
        level.locked = False
        return True
    return False
