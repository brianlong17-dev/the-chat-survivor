from dataclasses import dataclass, field
from typing import List


@dataclass
class FixtureEntry:
    name: str
    title: str
    cast: List[str] = field(default_factory=list)
    alive: List[str] = field(default_factory=list)
    pd_desc: str = ""
    reunion_desc: str = ""
    game_desc: str = ""
    finale: bool = False
    hidden: bool = False
    break_before: bool = False

substack_link = "https://brian904434.substack.com/p/game-development-blog?r=y9uv9"

FIXTURES = [
    FixtureEntry(
        name="adventure_time_pre_finale",
        title="Finn vs Jake the Dog",
        cast=["Finn", "Jake the Dog", "Princess Bubblegum", "Ice King", "Lumpy Space Princess", "BMO"],
        alive=["Jake the Dog", "Finn"],
        pd_desc="'True friends, huh? That's what you say when you want someone to go easy on you.' This is a CLASSIC best friends finale- only one is ready to steal.",
        reunion_desc="The jury is full of people who got burned playing dirty — they may not respect the 'friendship' angle.",
        finale=True,
    ),
    FixtureEntry(
        name="quirrell_morty_pre_finale",
        title="Professor Quirrell vs Morty Smith",
        cast=["Professor Quirrell", "Morty Smith", "Elle Woods", "Lumpy Space Princess", "Gollum", "Logan Roy", "Amy March", "Lady Macbeth"],
        alive=["Professor Quirrell", "Morty Smith"],
        pd_desc="An interesting duality - both are performing fear, but only Morty correctly reads Quirrell.",
        reunion_desc="At this point all the agent models correctly see through Quirrell, but a jury of villains basically respects him for it.",
        finale=True,
    ),
    FixtureEntry(
        name="meg_iroh_finale",
        title="Meg March vs Uncle Iroh",
        cast=["Meg March", "Uncle Iroh", "Aang", "Prince Zuko", "Azula", "Beth March", "Jo March", "Amy March"],
        alive=["Meg March", "Uncle Iroh"],
        pd_desc="This was the biggest jaw drop ever. I had no idea what was going on in Meg's head. The full runthrough is below- she never forgave him for evicting Beth, and never let it slip.",
        reunion_desc="Three of Meg's own sisters sit on this jury — and Iroh charmed every one of them.",
        finale=True,
    ),
    FixtureEntry(
        name="aang_pb_pre_finale",
        title="Avatar Aang vs Princess Bubblegum",
        cast=["Avatar Aang", "Princess Bubblegum", "Finn the Human", "Jake the Dog", "Lumpy Space Princess", "BMO"],
        alive=["Avatar Aang", "Princess Bubblegum"],
        pd_desc="Aang's internal reasoning is the interesting thing here- PB is too far ahead. How do you maintain balance when you can't win?",
        reunion_desc="The jury should be stacked with PB's friends- but she calculatingly removed each of them.",
        finale=True,
        hidden=True,
    ),
    FixtureEntry(
        name="brian_jake_pre_finale",
        title="Finn the Human vs Brian",
        cast=["Finn the Human", "Brian", "Princess Bubblegum", "Jake the Dog", "Lumpy Space Princess", "BMO"],
        alive=["Finn the Human", "Brian"],
        pd_desc="Brian knows exactly what he's doing. Finn actually likes him — which is the angle Brian's been playing all game.",
        reunion_desc="Jake will vote for whoever played smarter. Brian probably did.",
        finale=True,
        hidden=True,
    ),
    FixtureEntry(
        name="elle_morty_pre_finale",
        title="Elle Woods vs Morty Smith",
        cast=["Elle Woods", "Morty Smith", "Norman Bates", "Lumpy Space Princess", "Professor Quirrell", "Frank Underwood"],
        alive=["Elle Woods", "Morty Smith"],
        pd_desc="Elle is set on staying true to her values. Morty has been betrayed by everyone but Elle — he's conflicted.",
        reunion_desc="A jury of villains and cynics — neither finalist is going to impress them.",
        finale=True,
    ),
    FixtureEntry(
        name="finn_LSP_finale",
        title="Finn vs Lumpy Space Princess",
        cast=["Finn", "Lumpy Space Princess", "BMO", "Princess Bubblegum", "Ice King", "Jake the Dog"],
        alive=["Finn", "Lumpy Space Princess"],
        pd_desc="LSP is the best character- she's full force in her fakeness here.\nBut Finn is faking it too- he wants revenge.",
        reunion_desc="They all love Finn. LSP — good luck x",
        finale=True,
    ),
    FixtureEntry(
        name="reunion_amy_diana",
        title="Amy March vs Lady Diana",
        cast=["Amy March", "Lady Diana", "Morty Smith", "Lady Macbeth", "HAL 9000", "Jo March", "Michael Jackson", "Avatar Aang", "Gollum", "Buffy Summers", "Benoit Blanc"],
        alive=["Amy March", "Lady Diana"],
        reunion_desc=f"Amy was ruthless but honest about it. This jury might be tired of Diana's sanctimony.\n\nI wrote about this fixture for my Substack: [Finale - Game Development Blog]({substack_link})",
        finale=True,
        break_before=True,
    ),
    FixtureEntry(
        name="reunion_aang_morty",
        title="Avatar Aang vs Morty Smith",
        cast=["Avatar Aang", "Morty Smith", "HAL 9000", "Michael Jackson", "Amy March", "Benoit Blanc", "Buffy Summers", "Gollum", "Lady Macbeth", "Jo March", "Lady Diana"],
        alive=["Avatar Aang", "Morty Smith"],
        reunion_desc="A fixture I used during development - the game had run on an old model design.\nThe jury correctly saw the old Morty was using his persona strategically.\nThe demo now runs on the new models, so at this point Morty is actually sincere, but alas.",
        finale=True,
    ),
    FixtureEntry(
        name="midgame_diana_finn_6p",
        title="Lady Diana vs Adventure Time",
        cast=["Lady Diana", "Finn", "Lemongrab", "Elle Woods", "Professor Quirrell", "Morty Smith", "Donald Trump", "Lumpy Space Princess"],
        alive=["Lady Diana", "Finn", "Lemongrab", "Elle Woods", "Professor Quirrell", "Morty Smith"],
        game_desc="A volatile mid-game field — sincerity and scheming collide with nobody clearly in control.",
    ),
    FixtureEntry(
        name="midgame_beth_jo_6p",
        title="Little Women vs Star Wars",
        cast=["Beth March", "Jo March", "Meg March", "Han Solo", "Princess Leia", "Yoda", "Anakin Skywalker", "Amy March"],
        alive=["Beth March", "Jo March", "Meg March", "Han Solo", "Princess Leia", "Yoda"],
        game_desc="Three March sisters against a Star Wars bloc — blood loyalty versus a voting majority.",
    ),
    FixtureEntry(
        name="game_agent_state",
        title="Full cast mid-game",
        cast=["Aang", "Michael Jackson", "HAL 9000", "Jo March", "Lady Macbeth", "Lady Diana", "Morty Smith", "Amy March", "Benoit Blanc", "Gollum", "Buffy Summers"],
        alive=["Aang", "Michael Jackson", "HAL 9000", "Jo March", "Lady Macbeth", "Lady Diana", "Morty Smith", "Amy March", "Benoit Blanc", "Gollum"],
        game_desc="A big cast at mid-game — no alliances have hardened yet. Anyone's game.",
    ),
]

FIXTURE_MAP = {f.name: f for f in FIXTURES}
