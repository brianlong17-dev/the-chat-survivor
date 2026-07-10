from collections import deque
from pydantic import Field

from agents.agentic_player_v1.system_prompt_v1 import SystemPromptV1
from agents.player_response_models import AgentResponseModelFactory
from agents.abstract_agentic_player import AbstractAgenticPlayer

from typing import TYPE_CHECKING, Dict, Optional
if TYPE_CHECKING:
    from gameplay_management import *

_DESC_POSITION_ASSESSMENT = ("Based on your position in the scoreboard, what do you need to do? If it's a discussion round, what is your position in the upcoming round? Can you help yourself in some way?")
_DESC_UPDATED_GAME_STRATEGY = ("Only populate if you want to update your game strategy. "
                                      "Based on how the game works, what is the smartest strategy?")
_DESC_LIFE_LESSONS = ("A new lesson to you mind that you will take forward. This will shape your future descisions. Take key lessons only, so you don't cloud your decision making.")
_DESC_SPEAKING_STYLE = (
    "Only populate if your speaking style has evolved or shifted during this round — "
    "If nothing has changed, leave this blank. Do NOT explain or comment on why no change is needed. "
    "A description of HOW you talk, HOW you express yourself. "
    "NO specific word or phrases. "
    "Approximately as long and detailed as the previous speaking style."
)

class AgenticPlayerV1(AbstractAgenticPlayer):


    def __init__(
        self,
        name: str,
        initial_persona: str,
        api_client,
        speaking_style: str = ""
    ):
        super().__init__(name, initial_persona, api_client=api_client, speaking_style=speaking_style)
        self.rating = 0
        self.persona = initial_persona
        self.game_strategy = "Begin to take action and form strategy."
        self.position_assessment = ""
        self.life_lessons = deque(maxlen=8)
        self.persona_additions = deque()
        self.speaking_style = speaking_style
        self.phase_summaries_detailed = {}
        self.phase_summaries_brief = {}
        self.detailed_summary_count = 2
        self.game_over = False
        self.initialising = False
        self.currently_summarising = False
        self._mask_drop = False
        self.optional_response_buffer = 0
        self.round_specific_strategy = ""
        self._phase_initial_speaking_style = self.speaking_style

        #todo : implement temperature

    # --- 1. CONFIGURATION (The Map) ---
    @property
    def field_mappings(self) -> Dict[str, str]:
        #TODO just allgin these
        return {
            "persona_additions": "persona_additions",
            "updated_game_strategy": "game_strategy",
            "position_assessment": "position_assessment",
            "lifeLesson": "life_lessons",
            "speaking_style": "speaking_style",
            "round_specific_strategy": "round_specific_strategy"
        }

    def logic_fields(self):
        if self.game_over:
            return {}
        else:
            return {
                "position_assessment": (str, Field(description=_DESC_POSITION_ASSESSMENT))
            }

    def round_specific_strategy_name(self):
        return 'round_specific_strategy'

    def clear_round_specific_strategy(self):
        self.round_specific_strategy=""


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
            fields["updated_game_strategy"] = (str | None, Field(default=None, description=_DESC_UPDATED_GAME_STRATEGY))
        fields["persona_additions"] = self._persona_field()
        fields["lifeLesson"] =  (Optional[str], Field(default=None, description=_DESC_LIFE_LESSONS))
        fields["speaking_style"] = self._speaking_style_field()
        return fields

    def cognitive_fields(self):
        return {**self.logic_fields(), **self.evolution_fields()}

    def _system_prompt_class(self):
        return SystemPromptV1

    def persona_string(self):
        return self.persona + '\n' + '\n'.join(self.persona_additions)

    def _process_standard_turn_response(self, turn):
        thought = getattr(turn, 'private_thoughts_brief', "")
        self.most_recent_internal_thought = thought


        personality_field_names = list(self.cognitive_fields()) + [self.round_specific_strategy_name()]
        for field_name in personality_field_names:
            value = getattr(turn, field_name, None)
            if self._check_if_empty(value):
                continue
            target_attr_name = self.field_mappings.get(field_name)
            if not target_attr_name:
                continue


            current_attr_value = getattr(self, target_attr_name)
            # if its a queue we need to append
            if isinstance(current_attr_value, (list, deque)):
                clean_val = value.strip()
                # Check for duplicates (case-insensitive)
                is_duplicate = any(clean_val.lower() == existing.lower() for existing in current_attr_value)
                if not is_duplicate:
                    current_attr_value.append(clean_val)
            else:
                setattr(self, target_attr_name, value)

    def detailed_summaries_string(self):
        string = ""
        keys = self.phase_summaries_detailed.keys()
        for key in (keys):
            summary = self.phase_summaries_detailed.get(key)
            string += f"Phase {key}:\n{summary}\n\n"
        return string

    def phase_summaries_string(self):
        all_keys = set(self.phase_summaries_detailed.keys()).union(
            set(self.phase_summaries_brief.keys())
        )
        if not all_keys:
            return ""

        sorted_keys = sorted(list(all_keys))
        total_summaries = len(sorted_keys)
        detailed_start_index = max(0, total_summaries - self.detailed_summary_count)

        string = ""

        for i, key in enumerate(sorted_keys):
            if i < detailed_start_index:
                summary = self.phase_summaries_brief.get(key) or self.phase_summaries_detailed.get(key, "Summary missing.")
                string += f"Phase {key}:\n{summary}\n\n"
            else:
                summary = self.phase_summaries_detailed.get(key) or self.phase_summaries_brief.get(key, "Summary missing.")
                string += f"Phase {key}:\n{summary}\n\n"
        return string

    def _summarise_phase_context_string(self, game_board):
        phase_rounds_formatted = game_board.context_builder.phase_rounds_string(self)
        context_string = "=== YOUR SUMMARIES OF PREVIOUS PHASES ===\n"
        context_string += self.phase_summaries_string() #this should say none yet if empty.
        context_string += "\n\n------------ The current phase to summarise into memory: ---------\n"
        context_string += phase_rounds_formatted
        context_string += "\n-----------------------------------------------------------\n"
        return context_string

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

    def _build_summary_model(self, game_board):

        brief_summary_field = {"brief_summary" : (str, Field(description="Write an a brief summary of the phase from your perspective- Include the most essential information you want to remember. A brief couple of bullet points. Eventually this will be all you have to access from early phases."))}
        if self.game_over:
            game_commentary_description = "As an ex-player, could you give us commentary on the game after the last phase- write something punchy we can use for a clip."
        else:
            game_commentary_description = "Given your place in the competition, how do you feel after that last phase? Anything you want to say to those supporting you at home?"
        game_commentary_field = {"game_commentary" : (str, Field(description=game_commentary_description))}
        persona_uniqueness_field = {"persona_unique_detail" : (str, Field(description= "Inkeeping with the core of your character - what is one trait that you hold on to, in spite of the game, that makes you unique from other players? "))}

        public_response_prompt = "This is your summary- write in the first person, how you experienced the phase. Write every detail you think is important to commit to memory. This will only be seen by you. "
        if self.game_over:
            public_response_prompt += "Remember, you have been eliminated and you are now in the audience observing. What do you think of the players, who's doing well, what do you think of their strategies, who do you want to win?"

        action_fields = brief_summary_field | game_commentary_field | persona_uniqueness_field | self._life_lesson_compression_field()
        response_model = AgentResponseModelFactory.create_model_(
                self,
                game_board,
                model_name="sumariser",
                public_response_prompt=(public_response_prompt),
                private_thoughts_prompt=(
                    "What is important to remember?"
                ),
                action_fields= action_fields,
                action_post_response = True
            )


        return response_model

    def summarise_phase(self, game_board):
        #NOTE this works really well with DEFAULT_HIGHER_MODEL_NAME = "gemini-2.5-flash"
        #But other models will be brief - this needs to prompted to be detailed
        self.currently_summarising=True
        phase_number = game_board.phase_number
        prompt = ("From your perspective, write a summary of what happened in this phase. "
                  "Include all information that you think is relevant to retain, as this will be your memory of the game going forward."
                  "THIS IS PRIVATE- No one will see. ")
        if self.game_over:
            prompt += ("Don't forget, you have been eliminated, but your opinion matters- you may be asked to vote for a favorite later. "
            "Who's playing a good game, who are you rooting for, what drama are you most compelled by? ")

        context_string = self._summarise_phase_context_string(game_board)

        use_higher_model_for_summary = not self.game_over
        response_model = self._build_summary_model(game_board)

        response = self.take_turn_standard(prompt, game_board, response_model, instruction_override=context_string,
                                           use_higher_model = use_higher_model_for_summary)
        self._process_life_lesson_compression(response)
        self.phase_summaries_detailed[phase_number] = response.public_response
        self.phase_summaries_brief[phase_number] = response.brief_summary

        #TODO we need to seperate the summary cognative fields -
        #probably a parameter on take_turn_standard to skip, then manage it ourselves --
        #we should probably make a new cognative model , since we're currently overwriting 3/4 anwyay
        #and persona_additions is not an accurate field header anymore

        self._phase_initial_speaking_style = self.speaking_style

        self.persona = response.persona_additions #in summary round this field becomes the compressed & combined output
        self.persona_additions = deque([response.persona_unique_detail])

        self.currently_summarising=False

    def _process_life_lesson_compression(self, response):
        new_lesson = getattr(response, 'lifeLesson', None)
        if hasattr(response, "compressed_life_lessons") and response.compressed_life_lessons:
            self.life_lessons.clear()
            self.life_lessons.extend(response.compressed_life_lessons)
        if new_lesson:
            self.life_lessons.append(new_lesson)

    def _speaking_style_field(self):
        if self.currently_summarising:
             return (str, Field(description=(
                f"Restore it to the specificity and richness it had at the start of this phase, keeping any genuine changes in tone. "
                f"Strip any verbal tics, catchphrases, or phrases you have fallen into repeating. "
                f"Your style at the start of this phase (match this richness): {self._phase_initial_speaking_style} "
                f"Your style now: {self.speaking_style}"
                )))
        else:
             return (Optional[str], Field(default=None, description=_DESC_SPEAKING_STYLE))

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
