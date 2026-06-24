from typing import Dict, List, Literal, Optional, Type, TYPE_CHECKING
from pydantic import BaseModel, Field, create_model, field_validator, validator
from prompts.prompts import PromptLibrary

import warnings
if TYPE_CHECKING:
    from agents.human_player import Human
    from agents.player import Debater
    


class BaseResponse(BaseModel):
    private_thoughts: str = Field(description= PromptLibrary.desc_basic_thought)
    public_response: str = Field(description=PromptLibrary.desc_message)
    
    
class DynamicModelFactory:  
    
    @classmethod 
    def create_human_model(cls, public_response_prompt, action_fields):
        ordered_fields = {}
        if action_fields:
            ordered_fields.update(action_fields)
        pub_prompt = public_response_prompt or PromptLibrary.desc_message
        ordered_fields["public_response"] = (str, Field(description=pub_prompt))
        ordered_fields["private_thoughts"] = (str, Field(description="Private thoughts..."))
        return create_model('human_model', **ordered_fields)
        
    
    @classmethod
    def create_model_(
        cls, 
        agent: 'Debater', 
        model_name: str = "DynamicTurnModel",
        public_response_prompt: str = None, 
        private_thoughts_prompt: str = None, 
        additional_thought_nudge: str = None, 
        game_logic_fields: Dict[str, tuple] = None,   # Logic fields prompted by the game
        round_specific_strategy=None,
        action_fields: Dict[str, tuple] = None,      # Actions required by the game (e.g. dropdowns),
        action_post_response = False,
        mobile_outputs=False,
        multi_answer_model=False
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
            base_thought = PromptLibrary.desc_basic_thought
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
        pub_prompt = public_response_prompt or PromptLibrary.desc_message
        if mobile_outputs:
            pub_prompt += f"\nThe format is a phone groupchat- keep to the length you would type in response to the situation. "
        
        ordered_fields["public_response"] = (str, Field(description=pub_prompt))
        #....action 
        if action_fields and action_post_response:
            ordered_fields.update(action_fields)
                
        #........ self-learning
        
        if agent_evolution_fields:
            ordered_fields.update(agent_evolution_fields)
            
            
        #......... round specific strategy  #TODO this needs to be folder elsewhere
        if round_specific_strategy and agent.round_specific_strategy_name():
            ordered_fields[agent.round_specific_strategy_name()] = (str, Field(description=round_specific_strategy))

        return create_model(model_name, **ordered_fields)
    

     
    
