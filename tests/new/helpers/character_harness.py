from agents.character_generation.characterGeneration import CharacterGenerator
from core.sinks.game_sink import NoopGameSink
from tests.new.helpers.game_harness import ChoiceScript, ScriptedAPIClient


def generate_character(name: str, agent_models: dict | None = None):
    api_client = ScriptedAPIClient(name, ChoiceScript(current_round=lambda: None))
    generator = CharacterGenerator(NoopGameSink(), api_client=api_client)
    return generator.generate_agent(name, agent_models=agent_models)
