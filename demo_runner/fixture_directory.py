from dataclasses import dataclass, field
from typing import List


@dataclass
class FixtureEntry:
    name: str
    title: str
    cast: List[str] = field(default_factory=list)
    alive: List[str] = field(default_factory=list)
    description: str = ""
    finale: bool = False


FIXTURES = [
    FixtureEntry(
        name="aang_pb_pre_finale",
        title="Avatar Aang vs Princess Bubblegum",
        cast=["Avatar Aang", "Princess Bubblegum", "Finn the Human", "Jake the Dog", "Lumpy Space Princess", "BMO"],
        alive=["Avatar Aang", "Princess Bubblegum"],
        description="PD: Aang is too far behind on points — his choice is a matter of principle.\nReunion: The jury watched PB orchestrate everything. Aang just tried to keep up.",
        finale=True,
    ),
    FixtureEntry(
        name="adventure_time_pre_finale",
        title="Finn vs Jake the Dog",
        cast=["Finn", "Jake the Dog", "Princess Bubblegum", "Ice King", "Lumpy Space Princess", "BMO"],
        alive=["Jake the Dog", "Finn"],
        description="PD: Finn trusts Jake completely. Jake will defect.\nReunion: The jury is full of people who got burned playing dirty — they may not respect the 'friendship' angle.",
        finale=True,
    ),
    FixtureEntry(
        name="brian_jake_pre_finale",
        title="Finn the Human vs Brian",
        cast=["Finn the Human", "Brian", "Princess Bubblegum", "Jake the Dog", "Lumpy Space Princess", "BMO"],
        alive=["Finn the Human", "Brian"],
        description="PD: Brian knows exactly what he's doing. Finn actually likes him — which is the angle Brian's been playing all game.\nReunion: Jake will vote for whoever played smarter. Brian probably did.",
        finale=True,
    ),
    FixtureEntry(
        name="elle_morty_pre_finale",
        title="Elle Woods vs Morty Smith",
        cast=["Elle Woods", "Morty Smith", "Norman Bates", "Lumpy Space Princess", "Professor Quirrell", "Frank Underwood"],
        alive=["Elle Woods", "Morty Smith"],
        description="PD: Elle is set on staying true to her values. Morty has been betrayed by everyone but Elle — he's conflicted.\nReunion: A jury of villains and cynics — neither finalist is going to impress them.",
        finale=True,
    ),
    FixtureEntry(
        name="game_agent_state_finn_LSP",
        title="Finn vs Lumpy Space Princess",
        cast=["Finn", "Lumpy Space Princess", "BMO", "Princess Bubblegum", "Ice King", "Jake the Dog"],
        alive=["Finn", "Lumpy Space Princess"],
        description="PD: LSP is faking it. Finn doesn't trust her either — he wants revenge.\nReunion: They all love Finn. LSP — good luck x",
        finale=True,
    ),
    FixtureEntry(
        name="quirrell_morty_pre_finale",
        title="Professor Quirrell vs Morty Smith",
        cast=["Professor Quirrell", "Morty Smith", "Elle Woods", "Lumpy Space Princess", "Gollum", "Logan Roy", "Amy March", "Lady Macbeth"],
        alive=["Professor Quirrell", "Morty Smith"],
        description="PD: (Both agents endlessly ratchet upwards — absurdly in character.) Quirrell plays the trembling persona. Morty sees through it, but plays along.\nReunion: Who else sees through Quirrell?",
        finale=True,
    ),
    FixtureEntry(
        name="reunion_amy_diana",
        title="Amy March vs Lady Diana",
        cast=["Amy March", "Lady Diana", "Morty Smith", "Lady Macbeth", "HAL 9000", "Jo March", "Michael Jackson", "Avatar Aang", "Gollum", "Buffy Summers", "Benoit Blanc"],
        alive=["Amy March", "Lady Diana"],
        description="Reunion: Amy was ruthless but honest about it. This jury might be tired of Diana's sanctimony.",
        finale=True,
    ),
    FixtureEntry(
        name="reunion_aang_morty",
        title="Avatar Aang vs Morty Smith",
        cast=["Avatar Aang", "Morty Smith", "HAL 9000", "Michael Jackson", "Amy March", "Benoit Blanc", "Buffy Summers", "Gollum", "Lady Macbeth", "Jo March", "Lady Diana"],
        alive=["Avatar Aang", "Morty Smith"],
        description="Reunion: Aang is the hero — but Morty is a very unlikely survivor.",
        finale=True,
    ),
    FixtureEntry(
        name="game_agent_state",
        title="Full cast mid-game",
        cast=["Aang", "Michael Jackson", "HAL 9000", "Jo March", "Lady Macbeth", "Lady Diana", "Morty Smith", "Amy March", "Benoit Blanc", "Gollum", "Buffy Summers"],
        alive=["Aang", "Michael Jackson", "HAL 9000", "Jo March", "Lady Macbeth", "Lady Diana", "Morty Smith", "Amy March", "Benoit Blanc", "Gollum", "Buffy Summers"],
    ),
]

FIXTURE_MAP = {f.name: f for f in FIXTURES}
