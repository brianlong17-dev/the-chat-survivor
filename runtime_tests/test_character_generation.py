"""
Generates a single character and prints the result.
Swap the name to test different characters.
"""
import os
import shutil
import sys
import textwrap
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.api_client import create_api_client
from core.sinks.console_sink import ConsoleGameEventSink
from agents.character_generation.characterGeneration import CharacterGenerator

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"

WIDTH = min(shutil.get_terminal_size((100, 24)).columns, 100)


def print_character(index, total, player):
    print(f"\n{DIM}{'=' * WIDTH}{RESET}")
    print(f"{BOLD}{CYAN}  [{index}/{total}] {player.name}{RESET}")
    print(f"{DIM}{'=' * WIDTH}{RESET}")
    print_section("PERSONA", player.initial_persona, YELLOW)
    print_section("SPEAKING STYLE", player.initial_speaking_style, MAGENTA)


def print_section(label, body, color):
    print(f"\n{BOLD}{color}--- {label} {'-' * max(0, WIDTH - len(label) - 5)}{RESET}")
    for paragraph in str(body).strip().split("\n"):
        if not paragraph.strip():
            print()
            continue
        print(textwrap.fill(paragraph.strip(), width=WIDTH, initial_indent="  ", subsequent_indent="  "))


if __name__ == "__main__":
    sink = ConsoleGameEventSink()
    api_client = create_api_client(sink, token_budget=200_000)
    generator = CharacterGenerator(sink, api_client=api_client)
    namesx = ["Elena “Lenù” Greco", "Gollum", "Ice King", "Lady Macbeth", "Elle Woods", "BMO", "Lumpy Space Princess"] #, "Luke Skywalker", "Jake the Dog", "Finn the Human", "Miranda Priestly", "Lady Diana"]
    names = ["Jo March", "Amy March", "Meg March", "Beth March", "Marmee March", "Elena “Lenù” Greco", "Rafaella “Lila” Cerullo"]
    names = ["Tree Trunks (Adventure Time)", "Princess Diana", "Ice King"]
    heros = ["Avatar Aang", "Finn the Human", "Frodo"]
    names = ["Hermione Granger"]
    for i, name in enumerate(namesx, start=1):
        player = generator.generate_agent(name, allow_rename=False)
        print_character(i, len(namesx), player)
    print(f"\n{DIM}{'=' * WIDTH}{RESET}\n")
