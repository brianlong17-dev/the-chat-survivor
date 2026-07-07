from collections import deque
from pydantic import Field
from core.game_context.system_content import SystemPrompt
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
        self.game_strategy = "Begin to take action and form strategy."
        self.life_lessons = deque(maxlen=8)
        self.phase_summaries_detailed = {}
        self.phase_summaries_brief = {}
        
        self.optional_response_buffer = 0
        
        
        self.character_dictionary = {}
        # -- State flags -- #
        self.game_over = False
        self.initialising = False
        self.currently_summarising = False
        self._mask_drop=False
        
        self.character_strategy = None
        
        #persona
        self.initial_persona = initial_persona
        self.additional_persona_coloring = None
        self.persona_unique_detail = None
        
        #Speaking style
        self.initial_speaking_style = speaking_style
        self.speaking_style_update = None
        
    
    def process_character_impressions(self, response):
        fields = [f for f in response.model_fields if f.startswith("impression_")]
        for field in fields:
            value = getattr(response, field)
            if value is not None:
                self.character_dictionary[field] = value
        for field in list(self.character_dictionary):
            if field not in fields:
                del self.character_dictionary[field]
    
    def _system_prompt(self, game_board):
        return SystemPrompt.render(self)
    
    def _get_full_user_content(self, game_board, turn_prompt, instruction_override=None) :
        return UserContent.render(self, game_board, turn_prompt, instruction_override)

    def take_turn_standard(self, turn_prompt, game_board, model, instruction_override=None, thinking=False,
                           use_higher_model = False):
        full_user_content = self._get_full_user_content(game_board, turn_prompt, instruction_override)
        response = self.get_response(full_user_content, model, game_board, thinking, use_higher_model) 
        self.process_evolution_fields(response)
        self.process_character_impressions(response)
        return response
    
    #-----------
    #
    # turn fields
    #
    #-----------
    
    
    def logic_fields(self):
        if True:
            return {}
        else:
            #keeping as template - currently unused.
            return {
                #"position_assessment": (str, Field(description=("With an eye on the finale, what is your position on the scoreboard?")))
            }
            
    def chain_of_thought_fields(self):
        fields = {}
        fields["who_are_you"] = (
                str, Field(description=f"Remind yourself of who you are, so you don't get confused. Just a line."))
        fields["hallucination_catcher"] = (
                str, Field(description=f"In the past round do you see another player hallucinate or lie? Be careful not to repeat it"))
        fields["bandwagon"] = (
                str, Field(description=f"Is everyone jumping on a repeated thought? Do you agree? If not, say so"))
        fields["feeling"] = (
                str, Field(description=f"Based on your initial persona, how are you really feeling inside? Just a line, or two. "))
        fields["outer_mood"] = (
                str, Field(description=f"What mood are you outwardly expressing? Just a word or two. "))
        return fields
        
    
    def evolution_fields(self):
        fields = {}
        if not self.game_over:
            fields["game_strategy"] = (str | None, Field(default=None, description=
                                        ("Only populate if you want to update your game strategy. "
                                        "Based on your initial persona written in initial speaking style- what's your long term game plan? "))) 
        fields["life_lessons"] =  (Optional[str], Field(default=None, description=
                                ("OPTIONAL: New information to form a new life lesson. Write from your persona. ")))
        
        fields["additional_persona_coloring"] = self._persona_coloring_field_description()
        fields["character_strategy"] =( Optional[str], Field(default=None, description=
                                ("Optional update: In line with core values and speaking style: what is your game plan? ")))
        
        fields["speaking_style_update"] = self._speaking_style_field()
        
        return fields
                
    def _speaking_style_field(self):
        if self.currently_summarising:
             return (str, Field(description=(
                f"Rewrite speaking style update in style of the initial speaking style. Strip any verbal tics, catchphrases, or phrases. "
                f"Your current speaking style update: {self.speaking_style_update}"
                )))
        else:
             return (Optional[str], Field(default=None, description=(
                "In keeping with initial persona and initial speaking style."
                "To make you speaking style more colorful - Optional speaking style update: "
            )))
         
    def _persona_coloring_field_description(self):
        description = ("Add a splash of colour to your Unique Persona Detail? In keeping with your existing persona, written in your speaking style- perhaps a new fun element? Or just something you feel is missing? ")
        if self.additional_persona_coloring:
            return (Optional[str], Field(default=None, description=f"Optional: Update unique persona detail? In keeping with your existing persona, written in your speaking style- a fun new persona element?"))
             
        else:
            return (str, Field(description=f"Add a fun persona detail that makes you stand out from the rest of the players- what adds colour and spark to your character? "))
            
            

    def process_evolution_fields(self, turn):
        thought = getattr(turn, 'private_thoughts_brief', "")
        self.most_recent_internal_thought = thought
      
        personality_field_names = list(self.evolution_fields()) + list(self.logic_fields())
        
        
        for target_attr_name in personality_field_names:
            value = getattr(turn, target_attr_name, None)
            if self._check_if_empty(value):
                continue
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
                        f"In characters, compress your {len(self.life_lessons)} accumulated lessons into exactly 3 "
                        f"life lessons. Keep each detail but merge redundant themes.\n\n{existing}. NB: WRITE IN CHARACTER'S INITIAL SPEAKING STYLE"
                    )
                )
            )
        }
        
    def _summary_action_fields(self):
        fields = {}
        detailed_phase_summary_prompt = "This is your summary- write in the first person, how you experienced the phase. Write every detail you think is important to commit to memory. This will only be seen by you. Maintain every detail about every player that you want to remember strategically. Remember how you felt. If you have a grudge, or an alliance- include it. "
        if self.game_over:
            detailed_phase_summary_prompt += "Remember, you have been eliminated and you are now in the audience observing. What do you think of the players, who's doing well, what do you think of their strategies, who do you want to win?"

        fields["personal_detailed_phase_summary"] = (
                str, Field(description=detailed_phase_summary_prompt))
        fields["brief_summary"] = (
                str, Field(description=
                            "Write a brief summary of the phase from your perspective- Include the most essential information you want to remember. A brief couple of bullet points. Eventually this will be all you have to access from early phases."))
        fields["persona_unique_detail"] = (str, Field(description= 
                            "In keeping with the core of your character, written in your initial speaking style - what is one trait that you hold on to, in spite of the game, that makes you unique from other players? "))
        
        if self.game_over:
            game_commentary_description = "As an ex-player, could you give us commentary on the game after the last phase- write something punchy we can use for a clip."
        else:
            game_commentary_description = "Given your place in the competition, how do you feel after that last phase? Anything you want to say to those supporting you at home?"
        fields["game_commentary"] = (
            (str, Field(description=game_commentary_description)))
        fields.update(self._life_lesson_compression_field())

        return fields
    
    def _build_summary_model(self, game_board):

        action_fields = self._summary_action_fields()

        response_model = DynamicModelFactory.create_model_(
                self,
                game_board=game_board,
                model_name="summariser",
                public_response_prompt="No public response needed. The summaries will be private- no need to say anything. ",
                private_thoughts_prompt=("This is the summary phase - you will commit this phase to memory, and the upcoming will be your only record- What details are important for you to remember?"),
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
        response_model = self._build_summary_model(game_board)
        
        response = self.take_turn_standard(prompt, game_board, response_model, instruction_override=context_string, 
                                           use_higher_model = use_higher_model_for_summary)
        self._process_summary_turn(response, phase_number)

    def _process_summary_turn(self, response, phase_number):
        self.phase_summaries_detailed[phase_number] = response.personal_detailed_phase_summary
        self.phase_summaries_brief[phase_number] = response.brief_summary
        self._process_summary_turn_evolution(response)
        self.currently_summarising=False
        
    def _process_summary_turn_evolution(self, response):
        self._process_life_lesson_compression(response)
        self.persona_unique_detail = response.persona_unique_detail

    def _process_life_lesson_compression(self, response):
        new_lesson = getattr(response, 'life_lessons', None)
        if hasattr(response, "compressed_life_lessons") and response.compressed_life_lessons:
            self.life_lessons.clear()
            self.life_lessons.extend(response.compressed_life_lessons)
        if new_lesson:
            self.life_lessons.append(new_lesson)

        
