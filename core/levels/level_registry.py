from typing import List, Optional
from core.levels.level_definition import LevelDefinition
from core.levels.game_designs.game_design import GameDesign
from core.levels.game_designs.game_design_beginner import GameDesignBeginner
from core.levels.game_designs.game_design_beginner8 import GameDesignBeginner8
from core.levels.game_designs.game_design_bumper import GameDesignBumper
from core.levels.game_designs.game_design_quickstart import GameDesignQuickStart
from core.levels.game_designs.game_design_comedy_roast import GameDesignComedyRoast
from core.levels.game_designs.game_design_parlor import GameDesignParlor
from gameplay_management.games.game_rps import GameRockPaperScissors
from gameplay_management.games.game_guess import GameGuess
from gameplay_management.eliminations.voting_elect_leader import VoteElectLeader


AVAILABLE_LEVELS: List[LevelDefinition] = [
    LevelDefinition(
        id="quickstart",
        name="Quick-Start Tutorial",
        description="An introduction to the format- Two players, Rock-Paper-Scissors, loser goes home.",
        token_budget=100000,
        game_design=GameDesignQuickStart,
        locked=False
    ),
    LevelDefinition(
        id="beginner",
        name="Six",
        description="A six player, six phase game. A quick 10 minute game, with enough space for emergent strategic behavior. ",
        token_budget=15000000,
        game_design=GameDesignBeginner,
        locked=False
    ),
    LevelDefinition(
        id="8p",
        name="Game One: Eight",
        description="An eight person game. Players elect leaders and protect allies. More space for emergent social strategy in groups dynamics.",
        token_budget=15000000,
        game_design=GameDesignBeginner8,
        locked=False
    ),
    LevelDefinition(
        id="bumper",
        name="Bumper",
        description="An eleven person game. The longest road yet- more players, more alliances, more room for strategy.",
        token_budget=15000000,
        game_design=GameDesignBumper,
        locked=True
    ),
    LevelDefinition(
        id="perform",
        name="Comedy Roast",
        description="Players score each others performances, as they share sob stories and perform comedy roasts. ",
        token_budget=15000000,
        game_design=GameDesignComedyRoast,
        locked=True
    ),
    LevelDefinition(
        id="parlor",
        name="The Parlor Games",
        description="Players play more complex games, like Circle, Mobs and Knives. ",
        token_budget=15000000,
        game_design=GameDesignParlor,
        locked=True
    ),
]


def get_level_by_id(level_id: str) -> Optional[LevelDefinition]:
    """Retrieve a level definition by its ID."""
    for level in AVAILABLE_LEVELS:
        if level.id == level_id:
            return level
    return None


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
