from types import SimpleNamespace

from agents.agentic_player import AgenticPlayer
from core.game_config import GameConfig
from core.gameboard import GameBoard
from core.phase_runner import PhaseRunner
from core.levels.phase_description import PhaseDescription
from core.sinks.game_sink import NoopGameSink
from gameplay_management.game_cycle.game_knives import GameKnives


def turn_payload(target_name=None, public_response="pub", private_thoughts="priv", **extra_fields):
    payload = {
        "public_response": public_response,
        "private_thoughts": private_thoughts,
        **extra_fields,
    }
    if target_name is not None:
        payload["target_name"] = target_name
    return payload


class _QueuedResponse(SimpleNamespace):
    def model_dump(self):
        return dict(vars(self))


class TestGameSink(NoopGameSink):
    def get_user_input_simple(self, field_name, description):
        raise RuntimeError("TestGameSink cannot collect user input")

    def get_user_input_multiple_choice(self, field_name, description, choices):
        raise RuntimeError("TestGameSink cannot collect user input")


class QueuedClient:
    _mock_output = False
    default_model = "test-model"
    higher_model = "test-model-high"

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def create(self, response_model, messages, thinking=False, use_higher_model=False):
        self.calls.append({
            "response_model": response_model,
            "messages": messages,
            "thinking": thinking,
            "use_higher_model": use_higher_model,
        })
        if not self._responses:
            raise AssertionError("API client called more times than expected")
        response = self._responses.pop(0)
        return _QueuedResponse(**response)

    def assert_exhausted(self):
        assert not self._responses, f"Unused queued responses: {len(self._responses)}"


class NoopGameMaster:
    def summariseRound(self, *_args, **_kwargs):
        return SimpleNamespace(round_summary="")

    def summarise_game_text(self, context, game_text):
        return "[test summary]"


class TestSimulation:
    __test__ = False

    def __init__(self, agents, gameplay_config=None):
        self.agents = list(agents)
        self.dead_agents = []
        self.gameplay_config = gameplay_config or GameConfig()
        self.game_board = None
        self.game_manager = None

    def eliminate_player(self, agent):
        self.agents.remove(agent)
        self.dead_agents.append(agent)


def attach_test_runtime(board, simulation, game_manager, game_master=None):
    simulation.game_board = board
    simulation.game_manager = game_manager
    simulation.game_master = game_master or NoopGameMaster()
    board.phase_runner = PhaseRunner(simulation)
    return game_manager


def make_debater(name, api_client):
    return AgenticPlayer(
        name=name,
        initial_persona=f"{name} persona",
        speaking_style="normal",
        api_client=api_client,
    )


def _iter_round_messages(board):
    round_entry = board.game_log.current_round
    if round_entry is None:
        return
    for entry in round_entry.messageEntries:
        for msg in entry.messages:
            yield msg


def host_messages(board):
    return [msg["message"] for msg in _iter_round_messages(board) if msg["speaker"] == GameBoard.HOST_NAME]


def messages_for(board, speaker):
    return [msg["message"] for msg in _iter_round_messages(board) if msg["speaker"] == speaker]


def ledger_text(board):
    round_entry = board.game_log.current_round
    return round_entry.game_ledger if round_entry else ""


def build_targeted_choice_game(game_cls, agent_specs, initial_scores=None):
    clients = {name: QueuedClient(responses) for name, responses in agent_specs.items()}
    agents = [make_debater(name, clients[name]) for name in agent_specs]

    board = GameBoard(TestGameSink())
    board.initialize_agents(agents)
    if initial_scores:
        for name, score in initial_scores.items():
            if name in board.agent_scores:
                board.agent_scores[name] = score

    simulation = TestSimulation(agents)
    game = game_cls(board, simulation)
    attach_test_runtime(board, simulation, game)
    game._shuffled_agents = lambda: list(simulation.agents)
    board.newRound()
    board.phase_runner.current_phase_description = PhaseDescription(rounds=[game_cls])
    board.phase_runner.current_round_index = 0
    return game, board, agents, clients


def build_pd_game(agent_specs, initial_scores=None):
    clients = {name: QueuedClient(responses) for name, responses in agent_specs.items()}
    agents = [make_debater(name, clients[name]) for name in agent_specs]

    board = GameBoard(TestGameSink())
    board.initialize_agents(agents)
    if initial_scores:
        for name, score in initial_scores.items():
            if name in board.agent_scores:
                board.agent_scores[name] = score

    simulation = TestSimulation(agents)
    from gameplay_management.unified_controller import UnifiedController
    game = UnifiedController(board, simulation)
    attach_test_runtime(board, simulation, game)
    return game, board, agents, clients


def build_guess_game(agent_specs, initial_scores=None):
    clients = {name: QueuedClient(responses) for name, responses in agent_specs.items()}
    agents = [make_debater(name, clients[name]) for name in agent_specs]

    board = GameBoard(TestGameSink())
    board.initialize_agents(agents)
    if initial_scores:
        for name, score in initial_scores.items():
            if name in board.agent_scores:
                board.agent_scores[name] = score

    simulation = TestSimulation(agents)
    simulation.gameplay_config.guess_number_range = 4
    from gameplay_management.unified_controller import UnifiedController
    game = UnifiedController(board, simulation)
    attach_test_runtime(board, simulation, game)
    return game, board, agents, clients


def build_vote_game(agent_specs, initial_scores=None):
    clients = {name: QueuedClient(responses) for name, responses in agent_specs.items()}
    agents = [make_debater(name, clients[name]) for name in agent_specs]

    board = GameBoard(TestGameSink())
    board.initialize_agents(agents)
    if initial_scores:
        for name, score in initial_scores.items():
            if name in board.agent_scores:
                board.agent_scores[name] = score

    simulation = TestSimulation(agents)
    from gameplay_management.unified_controller import UnifiedController
    manager = UnifiedController(board, simulation)
    attach_test_runtime(board, simulation, manager)
    return manager, board, agents, clients


def build_knives_game(agent_specs, initial_scores=None, config_overrides=None):
    clients = {name: QueuedClient(responses) for name, responses in agent_specs.items()}
    agents = [make_debater(name, clients[name]) for name in agent_specs]

    board = GameBoard(TestGameSink())
    board.initialize_agents(agents)
    if initial_scores:
        for name, score in initial_scores.items():
            if name in board.agent_scores:
                board.agent_scores[name] = score

    simulation = TestSimulation(agents)
    if config_overrides:
        for key, value in config_overrides.items():
            setattr(simulation.gameplay_config, key, value)

    game = GameKnives(board, simulation)
    attach_test_runtime(board, simulation, game)
    game._shuffled_agents = lambda: list(simulation.agents)
    board.newRound()
    board.phase_runner.current_phase_description = PhaseDescription(rounds=[GameKnives])
    board.phase_runner.current_round_index = 0
    return game, board, agents, clients
