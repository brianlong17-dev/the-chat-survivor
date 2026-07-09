from core.levels.game_designs.game_design import GameDesign


class GameDesignComedyRoast(GameDesign):

    @classmethod
    def min_players(cls) -> int:
        return 7

    @classmethod
    def max_players(cls) -> int:
        return 8

    @classmethod
    def should_dead_players_summarise(cls) -> bool:
        return True #for audience vote
    
    @classmethod
    def get_phase_description(cls, phase_number, agent_number, cfg):
        raise NotImplementedError("GameDesignComedyRoast phases not yet implemented")
