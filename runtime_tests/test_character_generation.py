"""
Generates a single character and prints the result.
Swap the name to test different characters.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.api_client import create_api_client
from core.sinks.console_sink import ConsoleGameEventSink
from agents.character_generation.characterGeneration import CharacterGenerator

if __name__ == "__main__":
    sink = ConsoleGameEventSink()
    api_client = create_api_client(sink, token_budget=200_000)
    generator = CharacterGenerator(sink, api_client=api_client)
    names = ["Gollum", "Ice King", "Lady Macbeth", "Elle Woods", "BMO", "Lumpy Space Princess", "Luke Skywalker", "Jake the Dog", "Finn the Human", "Miranda Priestly", "Lady Diana"]
    names = ["Jo March", "Amy March", "Meg March", "Beth March", "Marmee March", "Elena “Lenù” Greco", "Rafaella “Lila” Cerullo"]
    names = ["Tree Trunks (Adventure Tiem)", "Pricess Diana", "Ice King"]
    for name in names:
        
        mj = generator.generate_debater(name, allow_rename=False)
        print(f"Name: {mj.name}")
        #print(f"\nPersona:\n{mj.persona}")
        #print(f"\nSpeaking Style:\n{mj.speaking_style}")
