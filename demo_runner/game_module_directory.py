from dataclasses import dataclass, field
from typing import List, Tuple, Type

from gameplay_management.base_manager import BaseRound
from gameplay_management.eliminations.reunion_round import FinaleReunionRound
from gameplay_management.games.game_pd_finale import GamePrisonersDilemmaFinale
from gameplay_management.game_cycle.game_knives import GameKnives
from gameplay_management.game_cycle.game_circle import GameCircle
from gameplay_management.game_cycle.game_mob import GameMob
from gameplay_management.eliminations.voting_bottom_two import VoteBottomTwo
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
from gameplay_management.discussion_rounds.discussion_round_directed_short import DiscussionRoundDirectedShort
from gameplay_management.discussion_rounds.discussion_round_directed import DiscussionRoundDirected


@dataclass
class ModuleEntry:
    id: str
    title: str
    module_class: Type[BaseRound]
    description: str = ""
    finale: bool = False
    game: bool = False
    hidden: bool = False
    cfgs: List[Tuple[str, object]] = field(default_factory=list)


reunion_desc = """This is the classic finale- eliminated players to crown a winner.

It raises the stakes on the game- every character has their own rivalries and alliances.

Eliminated players remain as background viewers, creating summarisation memories of each phase.

Instead of keeping these in context, we have a pre-interview where they use the memories to surface their opinions.

The agentic host finally appears here- he creates player introductions by using their memories of the game.

In future the host will be a full game agent with its own views and memories."""

pd_finale_desc = """The classic split or steal finale.

Two characters whose scores are tied have the opportunity to share the crown.

If not, it's a matter of integrity and manipulation if they can overtake their opponent on scores.

It's an amazing look into long term strategic deception- Uncle Iroh vs Meg March is an absolute highlight."""
MODULES = [
    ModuleEntry(
        id="reunion",
        title="Reunion Finale",
        module_class=FinaleReunionRound,
        description=reunion_desc,
        finale=True,
    ),
    ModuleEntry(
        id="pd_finale",
        title="Prisoner's Dilemma",
        module_class=GamePrisonersDilemmaFinale,
        description=pd_finale_desc,
        finale=True,
    ),
    ModuleEntry(
        id="knives",
        title="Knives",
        module_class=GameKnives,
        description="""This is Murder in the Dark meets Murder on the Orient Express.

Each player has one knife to start with. The lights go out- the most stabbed player is removed- but if you survive, you now control the knives.

I also introduced private messages in this round- you can also send players an anonymous note.

Really this game just needs a strong UI widget, and some refinement- but the idea does work.""",
        game=True,
    ),
    ModuleEntry(
        id="mob",
        title="Mob",
        module_class=GameMob,
        description="""Players form mobs behind a leader and pile onto a target.

This is a cool concept- it separates the leaders from the pacifists.

You step up to target a player- if you get enough people to support you, you steal their points.

It's a cool mechanism, and it really pits leaders against one another. Maybe it will work better with a larger cast, like 10+.

It benefits from fluid group dynamics.

Again, it just needs some refinement and a strong UI widget.""",
        game=True,
    ),
    ModuleEntry(
        id="circle",
        title="The Circle",
        module_class=GameCircle,
        description="""A shooting-circle standoff — survivors split the bonus.

This is the most successful of the parlor games. One player gets a gun, another gets a shield.
Shield has a choice- who else to protect? The gun must choose from the remaining players who to remove from the circle.

This is quick and dramatic, and really raises the stakes and forms grudges.

Because each player can plead it gets long.

In this module I experimented with rolling context compressions.

I also introduced an optional response mechanism. Each optional response you pass increases your buffer by 0.4.

You need 1 to respond, so when you speak up becomes strategic. This mechanism manages noise and manages token use.""",
        game=True,
    ),
    ModuleEntry(
        id="sob_story",
        title="Sob Story",
        module_class=GamePerformSobStory,
        description="""This is really reality TV inspired. I thought, how can they perform in a way that is variable on character? The sob story of course.

If you run multiple rounds they adopt strategic vulnerability.

The problem here is actually the scoring- they tend to rate each other along alliances and scores.

It's definitely a fun section, especially as a player trying to get pity points- not easy!""",
        game=True,
    ),
    ModuleEntry(
        id="comedy_roast",
        title="Comedy Roast",
        module_class=GamePerformComedyRoast,
        description="""This is the counter point to sob story- same format but comedy roasts.

It was really a quick pass at the concept, but they are SO bad at being funny.

A really interesting engineering challenge to work on to try and make this funny.""",
        game=True,
    ),
    ModuleEntry(
        id="wisdom",
        title="Wisdom of the Crowd",
        module_class=GameWisdom,
        description="""Vote on superlatives — match the crowd or win the vote to score points.
This is a mechanism to protect outsiders- questions like who is the biggest threat, outsider, unique voice etc.

It also uses a single turn to generate all the responses. In the end it's too much text for a single round, so I want to editorialise it before it's integrated.""",
        game=True,
    ),
    ModuleEntry(
        id="sacrifice",
        title="Sacrificer",
        module_class=GameTargetedChoiceSacrifice,
        description="""Use your own points to hurt another player.

Is it worth your own points to take points off someone else? In the end it's a bonkers mechanic that doesn't really make sense in practice.""",
        game=True,
    ),
    ModuleEntry(
        id="elect_leader",
        title="Elect the Executioner",
        module_class=VoteElectLeader,
        description="Each player votes to elect the executioner. The leader chosen will have to choose who is going home.",
        game=True,
    ),
    # ── Hidden: works-in-progress, not shown on the demo page ──
    ModuleEntry(
        id="bottom_two",
        title="Bottom Two Vote",
        module_class=VoteBottomTwo,
        description="The two lowest-scoring players face the vote — the group decides who goes home.",
        game=True,
        hidden=True,
    ),
    ModuleEntry(
        id="lowest_points",
        title="Farewell, to thee of points so lowest",
        module_class=VoteLowestPoints,
        description="Player with the lowest points is removed from the game.",
        game=True,
        hidden=True,
    ),
    ModuleEntry(
        id="winner_chooses",
        title="The Leader Executes",
        module_class=VoteWinnerChooses,
        description="The player leading the scores will choose who leaves the game IMMEDIATELY.",
        game=True,
        hidden=True,
    ),
    ModuleEntry(
        id="rps",
        title="Rock Paper Scissors",
        module_class=GameRockPaperScissors,
        description="A really basic demo of a 1v1 game.",
        game=True,
        hidden=True,
    ),
    ModuleEntry(
        id="pd",
        title="Prisoner's Dilemma",
        module_class=GamePrisonersDilemma,
        description="The classic social game.",
        game=True,
        hidden=True,
    ),
    ModuleEntry(
        id="guess",
        title="Guess",
        module_class=GameGuess,
        description="Guess the correct number to win!",
        game=True,
        hidden=True,
    ),
    ModuleEntry(
        id="give_take",
        title="Give and Take",
        module_class=GameTargetedChoiceGiveOrTake,
        description="As it says on the tin really!",
        game=True,
        hidden=True,
    ),
    ModuleEntry(
        id="give",
        title="Giver",
        module_class=GameTargetedChoiceGive,
        description="Choose a player to receive points!",
        game=True,
        hidden=True,
    ),
    ModuleEntry(
        id="steal",
        title="Stealer",
        module_class=GameTargetedChoiceSteal,
        description="Choose a player to steal points from!",
        game=True,
        hidden=True,
    ),
    ModuleEntry(
        id="test",
        title="Test",
        module_class=None,
        description="test",
        game=True,
        hidden=False,
    ),
    ModuleEntry(
        id="discussionDirected",
        title="Discussion Round Directed",
        module_class=DiscussionRoundDirected,
        description="test",
        game=True,
        cfgs=[("set_directed_discussion_group_allowed", True)],
        hidden=False,
    ),
    
]


MODULE_MAP = {m.id: m for m in MODULES}

