"""
Generates a single character and prints the result.
Swap the name to test different characters.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.api_client_setup import create_api_client
from core.sinks.console_sink import ConsoleGameEventSink
from agents.character_generation.characterGeneration import CharacterGenerator

if __name__ == "__main__":
    sink = ConsoleGameEventSink()
    api_client = create_api_client(sink)
    generator = CharacterGenerator(sink, api_client=api_client)

    mj = generator.generate_debater("Lady Diana", allow_rename=False)
    print(f"Name: {mj.name}")
    print(f"\nPersona:\n{mj.persona}")
    print(f"\nSpeaking Style:\n{mj.speaking_style}")
