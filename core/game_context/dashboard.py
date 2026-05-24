class Dashboard:
    
    @classmethod
    def header(cls, string):
        return(f"=== {string} ===")
    
    @classmethod
    def render(cls, agent, game_board) -> str:
        agent_name = agent.name
        game_over = agent.game_over
        agent_scores = dict(game_board.agent_scores)
        dash = []
        dash.append(cls.header("DASHBOARD"))
        
        removed_agent_names = game_board.phase_runner.removed_agent_names()
        if removed_agent_names:
            dead_str = ", ".join(removed_agent_names) if removed_agent_names else "None"
            dash.append(f"EVICTED PLAYERS: {dead_str} \n")
        
        if not game_over:
            dash.append(cls.header("PHASE PROGRESS"))
            dash.append(game_board.phase_runner.get_phase_progress_string())
            
        return "\n".join(dash)
    
