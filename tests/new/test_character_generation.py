from tests.new.helpers import generate_character


def test_a_configured_model_is_assigned_to_the_generated_agent():
    agent = generate_character("Ada", agent_models={"Ada": "gemini-2.5-flash-lite"})

    assert agent.api_model == "gemini-2.5-flash-lite"


def test_a_player_without_a_configured_model_is_left_unset():
    agent = generate_character("Bo", agent_models={"Ada": "gemini-2.5-flash-lite"})

    assert agent.api_model is None
