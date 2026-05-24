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
        "everything you say and do from this point forward."

        "Answer each question as if you are genuinely remembering real things. "
        "Be specific. Commit to details. Vague answers are wrong answers. "

        "These become your permanent memory. ")
    
    @classmethod
    def player_system_prompt(cls, agent):
        #TODO maybe this should be optional- hard to say
        #I think we will make a new class - dashboard- that will have more flexibility
        optional_response_buffer_string = cls._response_buffer_string(agent) #if game_board.optional_responses_in_use else ""
        
        # Format Life Lessons as a bulleted list (Clean Readability)
        if agent.life_lessons:
            lessons_str = "\n".join([f"- {lesson}" for lesson in agent.life_lessons])
        else:
            lessons_str = "- None yet. I am a blank slate."

        output_string = (f"You are {agent.name}.\n\n"
            
            f"=== YOUR PROFILE ===\n"
            f"Persona: {agent.persona}\n"
            f"Speaking Style: {agent.speaking_style}\n\n"

            f"=== LIFE LESSONS ===\n"
            f"Use these past learnings to guide your current behavior:\n"
            f"{lessons_str}\n\n")
        
        if not agent.game_over:
            output_string += (
            f"{optional_response_buffer_string}"
            f"=== YOUR INTERNAL STRATEGY AND ASSESSMENT ===\n"
            f"Current Strategy: {agent.game_strategy}\n"
            f"Position Assessment: {agent.position_assessment}\n")
            if agent.round_specific_strategy:
                output_string += (f"\n\nCurrent round strategy: {agent.round_specific_strategy}\n")

        if agent.initialising:
            output_string += f"\n{cls.system_prompt_init()}"
        
        brevity_prompt = ("Public responses should feel like a reaction, and less like a statement."
        "Occasional shortness can be powerful. 'Right. Fine.' carries more weight than a paragraph of composure.")
        if agent.brevity_jail:
            output_string += brevity_prompt
        
        if agent.most_recent_internal_thought:
            output_string += f"\n\nYour internal thoughts at your last turn: \n{agent.most_recent_internal_thought}"

        return output_string
