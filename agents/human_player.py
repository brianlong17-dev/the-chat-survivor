from collections import deque
from pydantic import Field, ValidationError
from agents.player import Debater
from core.shared_web_game_functionality import sanitize_text
from typing import get_args, get_origin, Literal
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from gameplay_management import *

class Human(Debater):
    
    
    def __init__(self, name: str):
        super().__init__(name=name, initial_persona='', api_client=None, speaking_style="")
        self.is_testing = False
    
    def is_human(self):
        return True
    
    def get_response(self, user_content: str, response_model, game_board, thinking=False, use_higher_model=False):
        #thinking, use_higher_model discarded for human player .
        if self.is_testing:
            print(f"[System prompt]:\n{self._system_prompt(game_board)}")
            print(f"[Context]:\n{user_content}")
            print("-" * 50)

        fields = response_model.model_fields
        while True:
            answers = self._collect_answers(fields, game_board)
            try:
                return response_model(**answers)
            except ValidationError as e:
                self._handle_validation_error(e, game_board.game_sink)

    def process_evolution_fields(self, turn):
        pass 
    
    def _collect_answers(self, fields: dict, game_board) -> dict:
        answers = {}
        for field_name, field_info in fields.items():
            if field_name == "private_thoughts":
                answers[field_name] = ""
                continue
            answers[field_name] = self._prompt_field(field_name, field_info, game_board)
        return answers

    def _prompt_field(self, field_name: str, field_info, game_board) -> str:
        description = field_info.description or f"Enter value for {field_name}"
        if field_name == 'public_response':
            description = "Your turn:"
        annotation = field_info.annotation
        if get_origin(annotation) is Literal:
            choices = [str(a) for a in get_args(annotation)]
            return game_board.game_sink.get_user_input_multiple_choice(field_name, description, choices)
        response = game_board.game_sink.get_user_input_simple(field_name, description)
        return sanitize_text(response)

    def _handle_validation_error(self, e: ValidationError, game_board):
        game_board.game_sink.system_private("❌ FORMAT ERROR: The game engine rejected your input.")
        for error in e.errors():
            game_board.game_sink.system_private(f" - Field '{error['loc'][0]}': {error['msg']}")
        game_board.game_sink.system_private("Let's try that again...\n")

    
    def summarise_phase(self, game_board):
        pass