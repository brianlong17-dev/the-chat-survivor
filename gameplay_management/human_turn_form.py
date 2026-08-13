import warnings
from dataclasses import dataclass, field
from typing import Literal, get_args, get_origin

FALLBACK_TITLES = {"public_response": "Your turn"}


@dataclass
class HumanChoiceInput:
    id: str
    title: str
    choices: list[str] = field(default_factory=list)
    is_multiple_choice: bool = True


@dataclass
class HumanTextInput:
    id: str
    title: str
    placeholder: str = ""
    is_multiple_choice: bool = False


@dataclass
class HumanTurnPage:
    inputs: list[HumanChoiceInput | HumanTextInput] = field(default_factory=list)
    underline: str = ""

    def add_choice_field(self, field_name, field_info):
        self.inputs.append(HumanChoiceInput(
            id=field_name,
            title=self._title(field_name, field_info),
            choices=[str(choice) for choice in get_args(field_info.annotation)],
        ))

    def add_text_field(self, field_name, field_info):
        self.inputs.append(HumanTextInput(
            id=field_name,
            title=self._title(field_name, field_info, with_choice=self._has_choice_input()),
        ))

    def _has_choice_input(self):
        return any(isinstance(turn_input, HumanChoiceInput) for turn_input in self.inputs)

    def _title(self, field_name, field_info, with_choice=False):
        description = field_info.description or field_name.replace("_", " ")
        if field_name == 'public_response':
            return "(Optional) What do you say as your choice is revealed?" if with_choice else "Your turn"
        return FALLBACK_TITLES.get(field_name) or description.strip().split(".")[0].strip()


@dataclass
class HumanTurnForm:
    pages: list[HumanTurnPage] = field(default_factory=list)

    def new_page(self, underline=""):
        page = HumanTurnPage(underline=underline)
        self.pages.append(page)
        return page
    
    def _set_default_pages(self):
        inputs = [turn_input for page in self.pages for turn_input in page.inputs]
        pages = [current_page := HumanTurnPage()]
        last_index = len(inputs) - 1
        for index, turn_input in enumerate(inputs):
            current_page.inputs.append(turn_input)
            if not turn_input.is_multiple_choice and index != last_index:
                current_page = HumanTurnPage()
                pages.append(current_page)
        self.pages = pages
    
    def update_from_description(self, human_input_description_object):
        if not human_input_description_object:
            self._set_default_pages()
            return

        inputs = {turn_input.id: turn_input for page in self.pages for turn_input in page.inputs}

        for field_name, title in human_input_description_object.titles.items():
            inputs[field_name].title = title

        for field_name, placeholder in human_input_description_object.placeholders.items():
            inputs[field_name].placeholder = placeholder

        if human_input_description_object.pages:
            self.pages = [
                HumanTurnPage(inputs=[inputs[field_name] for field_name in field_names])
                for field_names in human_input_description_object.pages
            ]
        else:
            self._set_default_pages()
            
                
                

        underlines = human_input_description_object.underlines
        if len(underlines) > len(self.pages):
            warnings.warn(f"HumanInputDescription gives {len(underlines)} underlines "
                          f"but the form has {len(self.pages)} pages - the extras are ignored.")

        for index, underline in enumerate(underlines[:len(self.pages)]):
            self.pages[index].underline = underline


@dataclass
class HumanInputDescription:
    pages: list[list[str]] = field(default_factory=list) # a list of the fields ie ([field_1, field_2], [field_3])
    titles: dict[str, str] = field(default_factory=dict) # field name, description ie Rock Paper Scissors?
    placeholders: dict[str, str] = field(default_factory=dict) # input placeholders - gonna be cute!
    underlines: list[str] = field(default_factory=list) #one per page, index-matched to pages
