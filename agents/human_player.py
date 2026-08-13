from agents.agentic_player_v2.agentic_player import AgenticPlayer
from core.shared_helpers import sanitize_text
from gameplay_management.human_turn_form import HumanTurnForm
from typing import get_origin, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from gameplay_management import *



class Human(AgenticPlayer):

    def __init__(self, name: str):
        super().__init__(name=name, initial_persona='', api_client=None, speaking_style="")
        self.is_testing = False

    def is_human(self):
        return True

    def get_response(self, user_content: str, response_model, game_board, thinking=False, use_higher_model=False,
                    human_input_description_object=None): 
        #thinking, use_higher_model discarded for human player .


        form = self._create_input_response_object(response_model, human_input_description_object)
        values = game_board.game_sink.get_user_input_form(form)
        values = self._sanitize_values(response_model, values)

        response = response_model(**values)
        for field_name in self.HIDDEN_FIELDS:
            object.__setattr__(response, field_name, "")
        return response
        
    def _sanitize_values(self, response_model, values):
        text_ids = [
            name for name, info in response_model.model_fields.items()
            if get_origin(info.annotation) is not Literal
        ]
        for field_name in text_ids:
            if values.get(field_name):
                values[field_name] = sanitize_text(values[field_name])
        return values

    def _create_input_response_object(self, response_model, human_input_description_object):
        
        form = HumanTurnForm(pages=[])
        
        page = form.new_page()

        for field_name, field_info in response_model.model_fields.items():
            if field_name not in self.HIDDEN_FIELDS:
                if get_origin(field_info.annotation) is Literal:
                    page.add_choice_field(field_name, field_info)
                else:
                    page.add_text_field(field_name, field_info)
        
        form.update_from_description(human_input_description_object)
        return form



    def process_evolution_fields(self, turn):
        pass

    def summarise_phase(self, game_board):
        pass
