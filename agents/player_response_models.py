from typing import Dict, List, Literal, Optional, Type, TYPE_CHECKING
from pydantic import BaseModel, Field, create_model, field_validator, validator
from prompts.prompts import PromptLibrary

import warnings
if TYPE_CHECKING:
    from agents.human_player import Human
    from agents.abstract_agentic_player import AbstractAgenticPlayer
    

default_public_response_prompt="Say what you want- Your thoughts and feelings should come through. (Don't repeat other messages. Say little if you have nothing new to say.)"
        
default_private_thought_prompt="Your internal thoughts. Think in voice. Strategy, feelings, and private observations. "

    
class AgentResponseModelFactory:  
    
    @classmethod 
    def create_human_model(cls, public_response_prompt, action_fields):
        ordered_fields = {}
        if action_fields:
            ordered_fields.update(action_fields)
        pub_prompt = public_response_prompt or "Your public response."
        ordered_fields["public_response"] = (str, Field(description=pub_prompt))
        ordered_fields["private_thoughts"] = (str, Field(description="Private thoughts..."))
        return create_model('human_model', **ordered_fields)
        
    
    @classmethod
    def create_model_(
        cls, 
        agent: 'AbstractAgenticPlayer', 
        game_board,
        model_name: str = "DynamicTurnModel",
        public_response_prompt: str = None, 
        private_thoughts_prompt: str = None, 
        additional_thought_nudge: str = None, 
        game_logic_fields: Dict[str, tuple] = None,   # Logic fields prompted by the game
        action_fields: Dict[str, tuple] = None,      # Actions required by the game (e.g. dropdowns),
        action_post_response = False,
        mobile_outputs=False,
        multi_answer_model=False,
        speech=False
    ) -> Type[BaseModel]:
        if agent.is_human(): # and not agent.is_testing:
            return cls.create_human_model(public_response_prompt, action_fields)
        
        ordered_fields = {}
        
        agent_chain_of_thought_fields = agent.chain_of_thought_fields()
        agent_logic_fields = agent.logic_fields()
        agent_evolution_fields = agent.evolution_fields()

        ordered_fields.update(agent_chain_of_thought_fields)
  
        if additional_thought_nudge:
            ordered_fields["additional_thoughts"] = (
                str, Field(description=f"{additional_thought_nudge}")
            )
            
        if game_logic_fields:
            ordered_fields.update(game_logic_fields)
        
        if not additional_thought_nudge and not game_logic_fields:
            ordered_fields.update(agent_logic_fields)
        
        
        #......... Thoughts
        if not private_thoughts_prompt:
            base_thought = default_private_thought_prompt
        else:
            base_thought = private_thoughts_prompt
     
        ordered_fields["private_thoughts"] = (str, Field(description=base_thought))
        if not multi_answer_model:
            #we dont went bcz it wont make sense to apend them under multiple answers
            ordered_fields["private_thoughts_brief"] = (str, Field(description="Give a one line sum up of your private thoughts. Keep any secret strategic intent you want to carry forward. "))
        
        #....action 
        if action_fields and not action_post_response:
            ordered_fields.update(action_fields)
        #...... public response
        pub_prompt = public_response_prompt or default_public_response_prompt
        if mobile_outputs and not speech:
            pub_prompt += f"\n (1-3 lines) "
        
        ordered_fields["public_response"] = (str, Field(description=pub_prompt))
        #....action 
        if action_fields and action_post_response:
            ordered_fields.update(action_fields)
                
        #........ self-learning
        
        if agent_evolution_fields:
            ordered_fields.update(agent_evolution_fields)
            
            
        if agent.uses_character_dictionary():
            ordered_fields = cls._add_character_fields(ordered_fields, game_board, agent)
        return create_model(model_name, **ordered_fields)


    @staticmethod
    def impression_field(name):
        return f"impression_{name.replace(' ', '_')}"

    @classmethod
    def _add_character_fields(cls, ordered_fields, game_board, agent):
        others = [name for name in game_board.agent_names() if name != agent.name]
        for i, name in enumerate(others):
            field_name = cls.impression_field(name)
            if i == 0:
                description = f"OPTIONAL: Since last turn, your updated impression of the following players- (don't lose any existing key memories, but update with any new noticings). {i + 1}: {name} "
            else:
                description = f"{i + 1}: {name}"
            ordered_fields[field_name] = (
                Optional[str],
                Field(default=None, description=description),
            )
        return ordered_fields

