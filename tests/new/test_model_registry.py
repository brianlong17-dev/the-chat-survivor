from core.api_client.model_registry import (
    AVAILABLE_MODELS,
    DEFAULT_MODEL_NAME,
    get_available_models,
    get_model_by_id,
)


def test_get_model_by_id_finds_a_registered_model():
    model = get_model_by_id(DEFAULT_MODEL_NAME)

    assert model is not None
    assert model.id == DEFAULT_MODEL_NAME


def test_get_model_by_id_returns_none_for_an_unknown_id():
    assert get_model_by_id("not-a-real-model") is None


def test_get_available_models_returns_the_registry():
    assert get_available_models() == AVAILABLE_MODELS


def test_exactly_one_model_is_marked_default():
    defaults = [model for model in AVAILABLE_MODELS if model.default]

    assert len(defaults) == 1
    assert defaults[0].id == DEFAULT_MODEL_NAME
