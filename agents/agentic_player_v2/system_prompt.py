class SystemPrompt:
    
    @classmethod
    def render(cls, agent) -> str:
        return cls.player_system_prompt(agent)
        
    
    @classmethod
    def _response_buffer_string(cls, agent):
        output = (f"=== OPTIONAL RESPONSE BUFFER ===\n"
                  f"(Needs to be at least 1 to respond in optional turns.)\n"
                  f"Optional Response Buffer: {agent.optional_response_buffer}\n\n")
        return output
    
    @classmethod
    def system_prompt_init(cls):
        return ("This is not a performance. You are generating the specific, concrete "
        "details of your own life — the memories and backstory that will ground "
        "everything you say and do from this point forward. "

        "Answer each question as if you are genuinely remembering real things. "
        "Be specific. Commit to details. Vague answers are wrong answers. "

        "These become your permanent memory. ")
        
    @classmethod
    def _character_impressions_string(cls, agent):
        if not agent.character_dictionary:
            return "- No impressions yet.\n\n"
        lines = []
        for field, impression in agent.character_dictionary.items():
            name = field.removeprefix("impression_").replace("_", " ")
            lines.append(f"- {name}: {impression}")
        return "\n".join(lines) + "\n\n"
    
    @classmethod
    def _persona_string(cls, agent):
        persona_string = f"Core Persona: {agent.initial_persona}\n" 
        if agent.additional_persona_coloring:
            persona_string += f"\nAdditional Persona Coloring: {agent.additional_persona_coloring}"
        if agent.persona_unique_detail:
            persona_string += f"\nUnique persona detail: {agent.persona_unique_detail}" 
        return persona_string
    
    @classmethod
    def _speaking_style_string(cls, agent):
        speaking_style_string=f"Core Speaking Style: {agent.initial_speaking_style}"
        if agent.speaking_style_update:
            speaking_style_string+=f"\nSpeaking Style Additional Consideration: {agent.speaking_style_update}"
        return speaking_style_string
        
    @classmethod
    def _life_lessons_string(cls, agent):
        if agent.life_lessons:
            lessons_str = "\n".join([f"- {lesson}" for lesson in agent.life_lessons])
        else:
            lessons_str = "- None yet. I am a blank slate."
        return lessons_str
    
    @classmethod
    def player_system_prompt(cls, agent, include_optional_response = False):
        #TODO - should move to dashboard - 
        optional_response_buffer_string = cls._response_buffer_string(agent) if include_optional_response else ""
        
        

        output_string = (f"You are {agent.name}.\n\n"
            f"=== YOUR PROFILE ===\n"
            f"{cls._persona_string(agent)}\n\n"
            f"{cls._speaking_style_string(agent)}\n\n"
            f"=== LIFE LESSONS ===\n"
            f"Use these past learnings to guide your current behavior:\n"
            f"{cls._life_lessons_string(agent)}\n\n"
            f"=== CHARACTER IMPRESSIONS ===\n"
            f"{cls._character_impressions_string(agent)}")
            
        
        if not agent.game_over:
            output_string += (
            f"{optional_response_buffer_string}"
            f"=== YOUR INTERNAL STRATEGY AND ASSESSMENT ===\n"
            f"Current Strategy: {agent.game_strategy}\n"
            f"Character Strategy: {agent.character_strategy}\n\n")
            
        if agent.emotional_state:
            output_string += "===\n\n"
            output_string += f"Emotional state: {agent.emotional_state}\n\n"
            output_string += "===\n\n"
        
        if agent.initialising:
            output_string += f"\n{cls.system_prompt_init()}"
        
        output_string += cls._instruction_string(agent)

        return output_string
    
    @classmethod
    def _instruction_string(cls, agent):
        brevity_prompt = ("Public responses should feel reactive and conversational- not a speech or statement. "
        "Occasional shortness can be powerful. Instead of a paragraph, try a short biting line. ")
        if agent._mask_drop or agent.game_over:
            instruction_string = "THE GAME IS OVER. There's nothing left to win or lose. NB: Drop any pretense or false persona. \n\n"
        else:
            instruction_string = "Reason through your character. Be conversational and reactive, not perfomative. " 
            if agent.brevity_jail:
                instruction_string += f"\n\n {brevity_prompt}"
        return instruction_string
