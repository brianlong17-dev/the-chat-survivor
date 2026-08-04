from core.game_context.formatting import header


class Dashboard:

    @classmethod
    def render(cls, agent, game_board) -> str:
        dash = []
        dash.append(header("DASHBOARD"))

        removed_agent_names = game_board.phase_runner.removed_agent_names()
        if removed_agent_names:
            dead_str = ", ".join(removed_agent_names) if removed_agent_names else "None"
            dash.append(f"EVICTED PLAYERS: {dead_str} \n")

        return "\n".join(dash)
    
