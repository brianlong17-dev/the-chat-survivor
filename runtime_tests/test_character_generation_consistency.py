"""
Generates Miranda Presley 10 times and prints persona + speaking style each time,
so we can eyeball how consistently the generator captures the character.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
import google.genai as genai
from core.api_client import api_client
from core.bootstrap import DEFAULT_MODEL_NAME, DEFAULT_HIGHER_MODEL_NAME
from core.sinks.console_sink import ConsoleGameEventSink
from agents.character_generation.characterGeneration import CharacterGenerator

NAME = "Miranda Presley"
NAME = "Elsa Greer"
RUNS = 2

if __name__ == "__main__":
    load_dotenv()
    client = genai.Client(
        vertexai=True,
        project=os.getenv("PROJECT"),
        location=os.getenv("LOCATION"),
    )
    api_client.init(client, DEFAULT_MODEL_NAME)

    sink = ConsoleGameEventSink()
    generator = CharacterGenerator(sink, DEFAULT_MODEL_NAME, DEFAULT_HIGHER_MODEL_NAME)

    for i in range(1, RUNS + 1):
        print("\n" + "=" * 80)
        print(f"RUN {i}/{RUNS} — {NAME}")
        print("=" * 80)
        debater = generator.generate_debater(NAME, allow_rename=False)
        print(f"Name: {debater.name}")
        print(f"\nPersona:\n{debater.persona}")
        print(f"\nSpeaking Style:\n{debater.speaking_style}")
