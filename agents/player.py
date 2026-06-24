from collections import deque
from pydantic import Field
from core.game_context.system_prompt import SystemPrompt
from core.game_context.user_content import UserContent
from core.game_context.summaries_builder import SummariesStringBuilder
from agents.player_models import DynamicModelFactory
from prompts.gamePrompts import GamePromptLibrary
from prompts.prompts import PromptLibrary
from agents.base_agent import BaseAgent
from typing import TYPE_CHECKING, Dict, Optional
if TYPE_CHECKING:
    from gameplay_management import *

class Debater(BaseAgent):
    
    
    def __init__(self, name: str, initial_persona: str, api_client, speaking_style: str = ""):
        super().__init__(name, api_client=api_client)
        self.rating = 0
        self.persona = initial_persona
        self.game_strategy = "Begin to take action and form strategy."
        self.position_assessment = ""
        self.life_lessons = deque(maxlen=8)
        self.persona_additions = deque()
        self.speaking_style = speaking_style
        self.phase_summaries_detailed = {}
        self.phase_summaries_brief = {}
        self.game_over = False
        self.initialising = False
        self.currently_summarising = False
        self.optional_response_buffer = 0
        self.round_specific_strategy = ""
        self._phase_initial_speaking_style = self.speaking_style
    
    
    def _system_prompt(self, game_board):
        return SystemPrompt.render(self)
    
    def _get_full_user_content(self, game_board, turn_prompt, instruction_override=None) :
        return UserContent.render(self, game_board, turn_prompt, instruction_override)

    def take_turn_standard(self, turn_prompt, game_board, model, instruction_override=None, thinking=False,
                           use_higher_model = False):
        full_user_content = self._get_full_user_content(game_board, turn_prompt, instruction_override)
        turn = self.get_response(full_user_content, model, game_board, thinking, use_higher_model) 
        self.process_evolution_fields(turn)
        return turn
    
    #-----------
    #
    # turn fields
    #
    #-----------
    
    
    def logic_fields(self):
        if self.game_over:
            return {}
        else:
            return {
                "position_assessment": (str, Field(description=PromptLibrary.desc_agent_position_assessment))
            }
            
    def chain_of_thought_fields(self):
        fields = {}
        fields["who_are_you"] = (
                str, Field(description=f"Remind yourself of who you are, so you don't get confused. Just a line."))
        fields["hallucination_catcher"] = (
                str, Field(description=f"In the past round do you see another player hallucination or lie? Be careful not to repeat it"))
        fields["bandwagon"] = (
                str, Field(description=f"Is everyone jumping on a repeated thought? Do you agree? If not, say so"))
        fields["feeling"] = (
                str, Field(description=f"How are you feeling? Just a line, or two. "))
        fields["mood"] = (
                str, Field(description=f"Current mood? Just a word or two to about your mood before you speak. "))
        return fields
        
    
    def evolution_fields(self):
        fields = {}
        if not self.game_over:
            fields["game_strategy"] = (str | None, Field(default=None, description=
                                        ("Only populate if you want to update your game strategy. "
                                        "Based on how the game works, what is the smartest strategy?"))) 
        fields["life_lessons"] =  (Optional[str], Field(default=None, description=
                                ("A new lesson to you mind that you will take forward. "
                                "This will shape your future descisions. Take key lessons only, so you don't cloud your decision making.")))
        
        fields["persona_additions"] = self._persona_field()
        fields["speaking_style"] = self._speaking_style_field()
        return fields


                
    def _speaking_style_field(self):
        if self.currently_summarising:
             return (str, Field(description=(
                f"Restore it to the specificity and richness it had at the start of this phase, keeping any genuine changes in tone. "
                f"Strip any verbal tics, catchphrases, or phrases you have fallen into repeating. "
                f"Your style at the start of this phase (match this richness): {self._phase_initial_speaking_style} "
                f"Your style now: {self.speaking_style}"
                )))
        else:
             return (Optional[str], Field(default=None, description=(
                "Only populate if your speaking style has evolved or shifted during this round — "
                "If nothing has changed, leave this blank. Do NOT explain or comment on why no change is needed. "
                "A description of HOW you talk, HOW you express yourself. "
                "NO specific word or phrases. "
                "Approximately as long and detailed as the previous speaking style."
            )))
         
    def _persona_field(self):
        if self.currently_summarising:
            new_persona_detail = '\n'.join(self.persona_additions) 
            return (str, Field(description=(
                f"Integrate the new persona detail into the existing persona from the start of the phase. "
                "Write within the register, spirit and complexity of the character, but integrate their evolutions."
                f"Compress all to the length of the original persona: ({len(self.persona.split())} words). \n\n"
                
                f"Your persona at the start of this phase (match this length, complexity and specificality): \n{self.persona} \n\n "
                f"New Persona detail: \n{new_persona_detail}\n\n"
                )))
        else:
             return (Optional[str], Field(default=None, description=
                ("If no evolution in public persona - leave BLANK. "
                 "In keeping with your existing public persona, "
                 "If your persona had reason to evolve, what direction would your character evolve in? "
                 "In keeping with their existing character - "
                 "You can add an aditional line.  "
                 "Not worldview or strategy - only your outward persona. "
            )))
                
         
    
        
    #TODO hmmm - probably remove- where would you put this? as an optional string i guess
    
    def round_specific_strategy_name(self):
        return 'round_specific_strategy'
    
    def clear_round_specific_strategy(self):
        self.round_specific_strategy=""
        
    # this is----- hmmm no longer needed i would say
    
    #########
    
    
    def process_evolution_fields(self, turn):
        thought = getattr(turn, 'private_thoughts_brief', "")
        self.most_recent_internal_thought = thought
      
        personality_field_names = list(self.evolution_fields()) #+ [self.round_specific_strategy_name()]
        for field_name in personality_field_names:
            value = getattr(turn, field_name, None)
            if self._check_if_empty(value):
                continue
            target_attr_name = field_name
            current_attr_value = getattr(self, target_attr_name)
            
            if isinstance(current_attr_value, (list, deque)):
                clean_val = value.strip()
                is_duplicate = any(clean_val.lower() == existing.lower() for existing in current_attr_value)
                if not is_duplicate:
                    current_attr_value.append(clean_val)
            else:
                setattr(self, target_attr_name, value)

    
    def detailed_summaries_string(self):
        return SummariesStringBuilder.detailed_summaries_string(self)


    def phase_summaries_string(self):
        return SummariesStringBuilder.phase_summaries_string(self)

    def _summarise_phase_context_string(self, game_board):
        return SummariesStringBuilder._summarise_phase_context_string(self, game_board)
    
    def _life_lesson_compression_field(self):
        if len(self.life_lessons) < 5:
            return {}
        existing = "\n".join(f"- {l}" for l in self.life_lessons)
        return {
            "compressed_life_lessons": (
                list[str],
                Field(
                    min_length=3,
                    max_length=3,
                    description=(
                        f"Synthesize your {len(self.life_lessons)} accumulated lessons into exactly 3 "
                        f"distilled principles. Merge redundant themes.\n\n{existing}"
                    )
                )
            )
        }
        
    def _summary_action_fields(self):
        fields = {}
        fields["brief_summary"] = (
                str, Field(description=
                            "Write an a brief summary of the phase from your perspective- Include the most essential information you want to remember. A brief couple of bullet points. Eventually this will be all you have to access from early phases."))
        fields["persona_unique_detail"] = (str, Field(description= 
                            "Inkeeping with the core of your character - what is one trait that you hold on to, in spite of the game, that makes you unique from other players? "))
        
        if self.game_over:
            game_commentary_description = "As an ex-player, could you give us commentary on the game after the last phase- write something punchy we can use for a clip."
        else:
            game_commentary_description = "Given your place in the competition, how do you feel after that last phase? Anything you want to say to those supporting you at home?"
        fields["game_commentary"] = (
            (str, Field(description=game_commentary_description)))
        fields.update(self._life_lesson_compression_field())

        return fields
    
    def _build_summary_model(self):
        public_response_prompt = "This is your summary- write in the first person, how you experienced the phase. Write every detail you think is important to commit to memory. This will only be seen by you. Maintain every detail about every player that you want to remember strategically. Remember how you felt. If you have a grudge, or an alliance- include it. "
        if self.game_over:
            public_response_prompt += "Remember, you have been eliminated and you are now in the audience observing. What do you think of the players, who's doing well, what do you think of their strategies, who do you want to win?"

        action_fields = self._summary_action_fields()
        
        response_model = DynamicModelFactory.create_model_(
                self,
                model_name="sumariser",
                public_response_prompt=(public_response_prompt),
                private_thoughts_prompt=("What details are important for you to remember?"),
                action_fields= action_fields,
                action_post_response = True)
        return response_model
        
    def summarise_phase(self, game_board):
        #NOTE this works really well with DEFAULT_HIGHER_MODEL_NAME = "gemini-2.5-flash"
        #But other models will be brief - this needs to prompted to be detailed
        self.currently_summarising=True
        phase_number = game_board.phase_number
        prompt = ("From your perspective, write a summary of what happened in this phase. "
                  "Include all information that you think is relevant to retain, as this will be your memory of the phase going forward."
                  "THIS IS PRIVATE- No one will see. ")
        if self.game_over:
            prompt += ("Don't forget, you have been eliminated, but your opinion matters- you may be asked to vote for a favorite later. "
            "Who's playing a good game, who are you rooting for, what drama are you most compelled by? ")
        
        context_string = self._summarise_phase_context_string(game_board)
        use_higher_model_for_summary = not self.game_over
        response_model = self._build_summary_model()
        
        response = self.take_turn_standard(prompt, game_board, response_model, instruction_override=context_string, 
                                           use_higher_model = use_higher_model_for_summary)
        self._process_summary_turn(response, phase_number)

    def _process_summary_turn(self, response, phase_number):
        self.phase_summaries_detailed[phase_number] = response.public_response
        self.phase_summaries_brief[phase_number] = response.brief_summary
        self._process_summary_turn_evolution(response)
        self.currently_summarising=False
        
    def _process_summary_turn_evolution(self, response):
        self._process_life_lesson_compression(response)
        self._phase_initial_speaking_style = self.speaking_style
        self.persona = response.persona_additions #in summary round this field becomes the compressed & combined output
        self.persona_additions = deque([response.persona_unique_detail])
       
        
    def _process_life_lesson_compression(self, response):
        new_lesson = getattr(response, 'life_lessons', None)
        if hasattr(response, "compressed_life_lessons") and response.compressed_life_lessons:
            self.life_lessons.clear()
            self.life_lessons.extend(response.compressed_life_lessons)
        if new_lesson:
            self.life_lessons.append(new_lesson)

        
