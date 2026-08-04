from core.game_context.formatting import header, subheader
from core.game_context.dashboard import Dashboard


class UserContent:
    
    @classmethod
    def render(cls, agent, game_board, turn_instruction, game_history_override) -> str:
        #TODO the game_history_override -- eventually will have different context objects that call different render methods
        dash = []
        dashboard = Dashboard.render(agent, game_board)
        dash.append(dashboard)
      
        if game_history_override:
            dash.append(game_history_override)
        else:
            cls.append_game_context(dash, agent, game_board)
            
        dash.append(header("YOUR TURN"))
        if turn_instruction:
            dash.append(f"{turn_instruction}")
            
        return "\n\n".join(dash)
    
    
    
    @classmethod
    def append_game_context(cls, dash, agent, game_board):
        summaries = agent.phase_summaries_string()
        cb = game_board.context_builder
        
        current_round = cb.current_round_formatted(agent, incl_scores=True)
        previous_rounds = cb.previous_rounds_formatted(agent, use_game_ledger = True)
        
        if summaries:
            dash.append(header("PAST PHASES: SUMMARIES"))
            dash.append(summaries)
        
        dash.append(header("CURRENT PHASE"))
        dash.append(subheader("Round Progress"))
        dash.append(game_board.phase_runner.get_phase_progress_string())
        if previous_rounds:
            #subheader included in method
            dash.append(previous_rounds)
        dash.append(header("CURRENT ROUND"))
        dash.append(current_round)
        
    
        
        
    