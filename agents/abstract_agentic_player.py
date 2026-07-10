from abc import abstractmethod
from agents.base_agent import BaseAgent
from core.game_context.user_content import UserContent

"""
So a lot of this could be used as an implemented base class since not everything changes between versions.
The reason I'm not doing this: I want to develop on the current agent freely.
To create your own agent you probably just want to

"""

# ============================================================================
# To be usable as an agentic player, implement all methods below:
#
#   __init__(name, initial_persona, api_client, speaking_style="") - constructor signature
#   take_turn_standard   - run one turn, return the model response
#   summarise_phase      - write this phase to memory at phase end
#   _get_full_user_content - render the per-turn user message
#   phase_summaries_string - render accumulated phase memory as a string
#   chain_of_thought_fields - reasoning fields for the turn response schema
#   logic_fields          - game-logic fields for the turn response schema
#   evolution_fields       - self-updating state fields for the turn response schema
#
# _system_prompt and is_human are inherited from BaseAgent.
# ============================================================================

class AbstractAgenticPlayer(BaseAgent):

    def __init__(self, name: str, initial_persona: str, api_client, speaking_style: str = ""):
        super().__init__(name, api_client=api_client)

    def _get_full_user_content(self, game_board, turn_prompt, instruction_override=None) :
        return UserContent.render(self, game_board, turn_prompt, instruction_override)

    def uses_character_dictionary(self):
        return False

    def take_turn_standard(self, turn_prompt, game_board, model, instruction_override=None, thinking=False,
                           use_higher_model=False):

        full_user_content = self._get_full_user_content(game_board, turn_prompt, instruction_override)
        response = self.get_response(full_user_content, model, game_board, thinking, use_higher_model)
        self._process_standard_turn_response(response)
        return response

    def _system_prompt(self, game_board):
        return self._system_prompt_class().render(self)

    @abstractmethod
    def _system_prompt_class(self):
        #This just generates their system prompt.
        raise NotImplementedError

    @abstractmethod
    def _process_standard_turn_response(self, response):
        raise NotImplementedError

    @abstractmethod
    def summarise_phase(self, game_board):
        #Produces the summary - also possible to do some extra processing
        raise NotImplementedError


    @abstractmethod
    def phase_summaries_string(self):
        #This will produce the string for their game context - their compressed view of the game history
        raise NotImplementedError


    @abstractmethod
    def chain_of_thought_fields(self):
        #The fields called before the turn - who you are, hallucination catcher, basic grounding.
        raise NotImplementedError

    @abstractmethod
    def logic_fields(self):
        #Not really used, but just a scratch pad to think about strategy
        raise NotImplementedError

    @abstractmethod
    def evolution_fields(self):
        #Fields called AFTER the turn - designed to update fields used in their system prompt.
        raise NotImplementedError
