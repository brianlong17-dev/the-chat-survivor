class SummariesStringBuilder:
    
    DETAILED_SUMMARIES_REQUIRED = 2
    
    @classmethod
    def render(cls, agent) -> str:
        return ""
    
    
    @classmethod
    def detailed_summaries_string(cls, agent):
        string = ""
        keys = agent.phase_summaries_detailed.keys()
        for key in (keys):
            summary = agent.phase_summaries_detailed.get(key)
            string += f"Phase {key}:\n{summary}\n\n"
        return string

    @classmethod
    def phase_summaries_string(cls, agent):
        summaries_detailed = agent.phase_summaries_detailed
        summaries_brief = agent.phase_summaries_brief
        all_keys = set(summaries_detailed.keys()).union(
            set(summaries_brief.keys())
        )
        if not all_keys:
            return ""
            
        sorted_keys = sorted(list(all_keys))
        total_summaries = len(sorted_keys)
        detailed_start_index = max(0, total_summaries - cls.DETAILED_SUMMARIES_REQUIRED)
        
        string = ""
        
        for i, key in enumerate(sorted_keys):
            if i < detailed_start_index:
                summary = summaries_brief.get(key) or summaries_detailed.get(key, "Summary missing.")
                string += f"Phase {key}:\n{summary}\n\n"
            else:
                summary = summaries_detailed.get(key) or summaries_brief.get(key, "Summary missing.")
                string += f"Phase {key}:\n{summary}\n\n"
        return string 
    
    @classmethod
    def _summarise_phase_context_string(cls, agent, game_board):
        phase_rounds_formatted = game_board.context_builder.phase_rounds_string(agent)
        context_string = "=== YOUR SUMMARIES OF PREVIOUS PHASES ===\n"
        context_string += cls.phase_summaries_string(agent) 
        context_string += "\n\n------------ The current phase to summarise into memory: ---------\n"
        context_string += phase_rounds_formatted
        context_string += "\n-----------------------------------------------------------\n"
        return context_string